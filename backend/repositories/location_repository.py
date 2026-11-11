"""
Repository for idea locations (civic geo layer).
"""

from typing import Any, List, Optional, Sequence

from sqlalchemy import case, func
from sqlalchemy.orm import Session

import repositories.db_models as db_models
from .base import BaseRepository


class IdeaLocationRepository(BaseRepository[db_models.IdeaLocation]):
    """Repository for IdeaLocation entity database operations."""

    def __init__(self, db: Session):
        super().__init__(db_models.IdeaLocation, db)

    def get_by_idea_id(self, idea_id: int) -> Optional[db_models.IdeaLocation]:
        """Return the location for an idea, if any."""
        return (
            self.db.query(db_models.IdeaLocation)
            .filter(db_models.IdeaLocation.idea_id == idea_id)
            .first()
        )

    def upsert(
        self,
        idea_id: int,
        latitude: float,
        longitude: float,
        neighborhood: Optional[str] = None,
        address: Optional[str] = None,
    ) -> db_models.IdeaLocation:
        """Create or update the location attached to an idea."""
        location = self.get_by_idea_id(idea_id)
        if location is None:
            location = db_models.IdeaLocation(
                idea_id=idea_id,
                latitude=latitude,
                longitude=longitude,
                neighborhood=neighborhood,
                address=address,
            )
            self.db.add(location)
        else:
            location.latitude = latitude
            location.longitude = longitude
            location.neighborhood = neighborhood
            location.address = address
        self.db.commit()
        self.db.refresh(location)
        return location

    def delete_by_idea_id(self, idea_id: int) -> bool:
        """Delete the location attached to an idea. Returns True if deleted."""
        location = self.get_by_idea_id(idea_id)
        if location is None:
            return False
        self.db.delete(location)
        self.db.commit()
        return True

    def get_map_items(
        self,
        min_lat: float,
        min_lng: float,
        max_lat: float,
        max_lng: float,
        statuses: Optional[Sequence[db_models.IdeaStatus]] = None,
        category_id: Optional[int] = None,
        limit: int = 1000,
    ) -> List[Any]:
        """Return ideas within a bounding box joined with their location and vote counts."""
        vote_counts = (
            self.db.query(
                db_models.Vote.idea_id.label("idea_id"),
                func.sum(
                    case((db_models.Vote.vote_type == db_models.VoteType.UPVOTE, 1), else_=0)
                ).label("upvotes"),
                func.sum(
                    case(
                        (db_models.Vote.vote_type == db_models.VoteType.DOWNVOTE, 1),
                        else_=0,
                    )
                ).label("downvotes"),
            )
            .group_by(db_models.Vote.idea_id)
            .subquery()
        )

        query = (
            self.db.query(
                db_models.Idea.id,
                db_models.Idea.title,
                db_models.Idea.category_id,
                db_models.Idea.status,
                db_models.IdeaLocation.latitude,
                db_models.IdeaLocation.longitude,
                db_models.IdeaLocation.neighborhood,
                db_models.IdeaLocation.address,
                func.coalesce(vote_counts.c.upvotes, 0).label("upvotes"),
                func.coalesce(vote_counts.c.downvotes, 0).label("downvotes"),
            )
            .join(
                db_models.IdeaLocation,
                db_models.IdeaLocation.idea_id == db_models.Idea.id,
            )
            .outerjoin(vote_counts, vote_counts.c.idea_id == db_models.Idea.id)
            .filter(
                db_models.Idea.deleted_at.is_(None),
                db_models.Idea.is_hidden.is_(False),
                db_models.IdeaLocation.latitude >= min_lat,
                db_models.IdeaLocation.latitude <= max_lat,
                db_models.IdeaLocation.longitude >= min_lng,
                db_models.IdeaLocation.longitude <= max_lng,
            )
        )

        if statuses:
            query = query.filter(db_models.Idea.status.in_(statuses))
        if category_id is not None:
            query = query.filter(db_models.Idea.category_id == category_id)

        return query.limit(limit).all()

    def get_hotspots(
        self,
        limit: int = 20,
        category_id: Optional[int] = None,
        statuses: Optional[Sequence[db_models.IdeaStatus]] = None,
    ) -> List[Any]:
        """Aggregate idea counts per neighborhood."""
        count_col = func.count(db_models.IdeaLocation.id)
        query = (
            self.db.query(
                db_models.IdeaLocation.neighborhood.label("neighborhood"),
                count_col.label("count"),
                func.avg(db_models.IdeaLocation.latitude).label("latitude"),
                func.avg(db_models.IdeaLocation.longitude).label("longitude"),
            )
            .join(db_models.Idea, db_models.Idea.id == db_models.IdeaLocation.idea_id)
            .filter(
                db_models.IdeaLocation.neighborhood.isnot(None),
                db_models.IdeaLocation.neighborhood != "",
                db_models.Idea.deleted_at.is_(None),
                db_models.Idea.is_hidden.is_(False),
            )
        )

        if statuses:
            query = query.filter(db_models.Idea.status.in_(statuses))
        if category_id is not None:
            query = query.filter(db_models.Idea.category_id == category_id)

        return (
            query.group_by(db_models.IdeaLocation.neighborhood)
            .order_by(count_col.desc())
            .limit(limit)
            .all()
        )
