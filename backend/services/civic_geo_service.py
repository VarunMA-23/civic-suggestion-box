"""
Service for the civic geo layer: idea locations, images, map and hotspots.
"""

import hashlib
import os
import uuid
from pathlib import Path
from typing import List, Optional, Sequence

from fastapi import UploadFile
from sqlalchemy.orm import Session

import models.schemas as schemas
import repositories.db_models as db_models
from helpers.file_validation import detect_image_mime
from models.exceptions import (
    IdeaNotFoundException,
    NotFoundException,
    PermissionDeniedException,
    ValidationException,
)
from repositories.image_repository import IdeaImageRepository
from repositories.location_repository import IdeaLocationRepository

ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_IMAGES_PER_IDEA = 5


class CivicGeoService:
    """Business logic for civic location and photo features."""

    @staticmethod
    def _get_idea_or_raise(db: Session, idea_id: int) -> db_models.Idea:
        idea = (
            db.query(db_models.Idea)
            .filter(
                db_models.Idea.id == idea_id,
                db_models.Idea.deleted_at.is_(None),
            )
            .first()
        )
        if idea is None:
            raise IdeaNotFoundException(f"Idea with ID {idea_id} not found")
        return idea

    @staticmethod
    def _assert_can_edit(
        idea: db_models.Idea, user_id: int, is_admin: bool
    ) -> None:
        if is_admin:
            return
        if int(idea.user_id) != user_id:
            raise PermissionDeniedException(
                "You can only modify civic data for your own ideas"
            )

    # ------------------------------------------------------------------
    # Locations
    # ------------------------------------------------------------------
    @staticmethod
    def get_location(
        db: Session, idea_id: int
    ) -> Optional[schemas.IdeaLocationRead]:
        CivicGeoService._get_idea_or_raise(db, idea_id)
        location = IdeaLocationRepository(db).get_by_idea_id(idea_id)
        if location is None:
            return None
        return schemas.IdeaLocationRead.model_validate(location)

    @staticmethod
    def upsert_location(
        db: Session,
        idea_id: int,
        data: schemas.IdeaLocationCreate,
        user_id: int,
        is_admin: bool = False,
    ) -> schemas.IdeaLocationRead:
        idea = CivicGeoService._get_idea_or_raise(db, idea_id)
        CivicGeoService._assert_can_edit(idea, user_id, is_admin)

        location = IdeaLocationRepository(db).upsert(
            idea_id=idea_id,
            latitude=data.latitude,
            longitude=data.longitude,
            neighborhood=data.neighborhood,
            address=data.address,
        )
        return schemas.IdeaLocationRead.model_validate(location)

    # ------------------------------------------------------------------
    # Images
    # ------------------------------------------------------------------
    @staticmethod
    def list_images(db: Session, idea_id: int) -> List[schemas.IdeaImageRead]:
        CivicGeoService._get_idea_or_raise(db, idea_id)
        images = IdeaImageRepository(db).get_by_idea_id(idea_id)
        return [schemas.IdeaImageRead.model_validate(image) for image in images]

    @staticmethod
    def upload_image(
        db: Session,
        idea_id: int,
        file: UploadFile,
        user_id: int,
        is_admin: bool = False,
    ) -> schemas.IdeaImageRead:
        idea = CivicGeoService._get_idea_or_raise(db, idea_id)
        CivicGeoService._assert_can_edit(idea, user_id, is_admin)

        image_repo = IdeaImageRepository(db)
        if image_repo.count_for_idea(idea_id) >= MAX_IMAGES_PER_IDEA:
            raise ValidationException(
                f"A maximum of {MAX_IMAGES_PER_IDEA} images is allowed per idea"
            )

        content = file.file.read()
        file.file.seek(0)

        if not content:
            raise ValidationException("Uploaded file is empty")
        if len(content) > MAX_IMAGE_SIZE:
            raise ValidationException("File size exceeds 5MB limit")

        detected_type = detect_image_mime(content)
        if detected_type is None:
            raise ValidationException(
                "Invalid image file. Allowed: image/jpeg, image/png, image/gif, image/webp"
            )

        extension = ALLOWED_IMAGE_MIME_TYPES[detected_type]
        filename = f"{uuid.uuid4()}{extension}"
        upload_dir = Path("data/uploads/ideas")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / filename

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        content_hash = hashlib.sha256(content).hexdigest()
        url = str(file_path).replace("\\", "/")
        image = image_repo.create_image(
            idea_id=idea_id, url=url, content_hash=content_hash
        )
        return schemas.IdeaImageRead.model_validate(image)

    @staticmethod
    def delete_image(
        db: Session,
        idea_id: int,
        image_id: int,
        user_id: int,
        is_admin: bool = False,
    ) -> None:
        idea = CivicGeoService._get_idea_or_raise(db, idea_id)
        CivicGeoService._assert_can_edit(idea, user_id, is_admin)

        image_repo = IdeaImageRepository(db)
        image = image_repo.get_by_id_for_idea(image_id, idea_id)
        if image is None:
            raise NotFoundException(f"Image with ID {image_id} not found")

        file_path = Path(str(image.url).replace("/", os.sep))
        image_repo.delete(image)
        try:
            if file_path.exists():
                file_path.unlink()
        except OSError:
            # The database record is gone; a leftover file is non-fatal.
            pass

    # ------------------------------------------------------------------
    # Map & hotspots
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_statuses(
        status: Optional[str],
    ) -> Optional[Sequence[db_models.IdeaStatus]]:
        if not status:
            return [db_models.IdeaStatus.APPROVED]
        values = [value.strip() for value in status.split(",") if value.strip()]
        parsed: List[db_models.IdeaStatus] = []
        for value in values:
            try:
                parsed.append(db_models.IdeaStatus(value))
            except ValueError as exc:
                raise ValidationException(f"Invalid idea status '{value}'") from exc
        return parsed or [db_models.IdeaStatus.APPROVED]

    @staticmethod
    def get_map(
        db: Session,
        min_lat: float,
        min_lng: float,
        max_lat: float,
        max_lng: float,
        status: Optional[str] = None,
        category_id: Optional[int] = None,
        limit: int = 1000,
    ) -> List[schemas.IdeaMapItem]:
        if min_lat > max_lat or min_lng > max_lng:
            raise ValidationException("Invalid bounding box")
        if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
            raise ValidationException("Latitude must be between -90 and 90")
        if not (-180 <= min_lng <= 180 and -180 <= max_lng <= 180):
            raise ValidationException("Longitude must be between -180 and 180")

        statuses = CivicGeoService._parse_statuses(status)
        rows = IdeaLocationRepository(db).get_map_items(
            min_lat=min_lat,
            min_lng=min_lng,
            max_lat=max_lat,
            max_lng=max_lng,
            statuses=statuses,
            category_id=category_id,
            limit=limit,
        )

        items: List[schemas.IdeaMapItem] = []
        for row in rows:
            upvotes = int(row.upvotes or 0)
            downvotes = int(row.downvotes or 0)
            items.append(
                schemas.IdeaMapItem(
                    id=row.id,
                    title=row.title,
                    category_id=row.category_id,
                    status=row.status,
                    latitude=row.latitude,
                    longitude=row.longitude,
                    neighborhood=row.neighborhood,
                    address=row.address,
                    upvotes=upvotes,
                    downvotes=downvotes,
                    score=upvotes - downvotes,
                )
            )
        return items

    @staticmethod
    def get_hotspots(
        db: Session,
        limit: int = 20,
        category_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> schemas.IdeaHotspotResponse:
        statuses = CivicGeoService._parse_statuses(status)
        rows = IdeaLocationRepository(db).get_hotspots(
            limit=limit, category_id=category_id, statuses=statuses
        )

        neighborhoods = [
            schemas.IdeaHotspot(
                neighborhood=row.neighborhood,
                count=int(row.count),
                latitude=float(row.latitude),
                longitude=float(row.longitude),
                category_id=category_id,
            )
            for row in rows
        ]
        total = sum(item.count for item in neighborhoods)
        return schemas.IdeaHotspotResponse(total=total, neighborhoods=neighborhoods)
