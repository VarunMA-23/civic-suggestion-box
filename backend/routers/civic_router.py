"""
HTTP routes for the civic geo layer (map, hotspots, locations, images).

Mounted under /api/ideas and included BEFORE ideas_router so that the static
/map and /hotspots paths are not shadowed by /{idea_id}.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

import authentication.auth as auth
import models.schemas as schemas
import repositories.db_models as db_models
from repositories.database import get_db
from services.civic_geo_service import CivicGeoService

router = APIRouter(prefix="/ideas", tags=["civic-geo"])


def _is_admin(user: db_models.User) -> bool:
    return bool(user.is_global_admin)


@router.get("/map", response_model=List[schemas.IdeaMapItem])
def get_ideas_map(
    min_lat: float = Query(..., ge=-90, le=90),
    min_lng: float = Query(..., ge=-180, le=180),
    max_lat: float = Query(..., ge=-90, le=90),
    max_lng: float = Query(..., ge=-180, le=180),
    status: Optional[str] = Query(
        default=None,
        description="Comma-separated idea statuses (default: approved)",
    ),
    category_id: Optional[int] = Query(default=None),
    limit: int = Query(default=1000, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """Return approved ideas within a bounding box for the live map."""
    return CivicGeoService.get_map(
        db=db,
        min_lat=min_lat,
        min_lng=min_lng,
        max_lat=max_lat,
        max_lng=max_lng,
        status=status,
        category_id=category_id,
        limit=limit,
    )


@router.get("/hotspots", response_model=schemas.IdeaHotspotResponse)
def get_idea_hotspots(
    limit: int = Query(default=20, ge=1, le=100),
    category_id: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Return idea counts grouped by neighborhood, most active first."""
    return CivicGeoService.get_hotspots(
        db=db, limit=limit, category_id=category_id, status=status
    )


@router.get(
    "/{idea_id}/location",
    response_model=Optional[schemas.IdeaLocationRead],
)
def get_idea_location(
    idea_id: int,
    db: Session = Depends(get_db),
):
    """Return the location attached to an idea, or null if none."""
    return CivicGeoService.get_location(db, idea_id)


@router.post(
    "/{idea_id}/location",
    response_model=schemas.IdeaLocationRead,
)
def set_idea_location(
    idea_id: int,
    location: schemas.IdeaLocationCreate,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(auth.get_current_active_user),
):
    """Create or update the location attached to an idea."""
    return CivicGeoService.upsert_location(
        db=db,
        idea_id=idea_id,
        data=location,
        user_id=int(current_user.id),
        is_admin=_is_admin(current_user),
    )


@router.delete("/{idea_id}/location")
def delete_idea_location(
    idea_id: int,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(auth.get_current_active_user),
):
    """Remove the location attached to an idea."""
    from models.exceptions import IdeaNotFoundException, PermissionDeniedException
    from repositories.idea_repository import IdeaRepository

    idea = IdeaRepository(db).get_by_id(idea_id)
    if idea is None:
        raise IdeaNotFoundException(f"Idea with ID {idea_id} not found")
    if not _is_admin(current_user) and int(idea.user_id) != int(current_user.id):
        raise PermissionDeniedException(
            "You can only modify civic data for your own ideas"
        )

    from repositories.location_repository import IdeaLocationRepository

    deleted = IdeaLocationRepository(db).delete_by_idea_id(idea_id)
    return {"deleted": deleted, "idea_id": idea_id}


@router.get("/{idea_id}/images", response_model=List[schemas.IdeaImageRead])
def list_idea_images(
    idea_id: int,
    db: Session = Depends(get_db),
):
    """List images attached to an idea."""
    return CivicGeoService.list_images(db, idea_id)


@router.post("/{idea_id}/images", response_model=schemas.IdeaImageRead)
def upload_idea_image(
    idea_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(auth.get_current_active_user),
):
    """Upload a photo for an idea (max 5MB, jpeg/png/gif/webp)."""
    return CivicGeoService.upload_image(
        db=db,
        idea_id=idea_id,
        file=file,
        user_id=int(current_user.id),
        is_admin=_is_admin(current_user),
    )


@router.delete("/{idea_id}/images/{image_id}")
def delete_idea_image(
    idea_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(auth.get_current_active_user),
):
    """Delete an image attached to an idea."""
    CivicGeoService.delete_image(
        db=db,
        idea_id=idea_id,
        image_id=image_id,
        user_id=int(current_user.id),
        is_admin=_is_admin(current_user),
    )
    return {"deleted": True, "idea_id": idea_id, "image_id": image_id}
