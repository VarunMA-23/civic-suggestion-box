"""
Repository for idea images (civic geo layer).
"""

from typing import List, Optional

from sqlalchemy.orm import Session

import repositories.db_models as db_models
from .base import BaseRepository


class IdeaImageRepository(BaseRepository[db_models.IdeaImage]):
    """Repository for IdeaImage entity database operations."""

    def __init__(self, db: Session):
        super().__init__(db_models.IdeaImage, db)

    def get_by_idea_id(self, idea_id: int) -> List[db_models.IdeaImage]:
        """Return all images for an idea, oldest first."""
        return (
            self.db.query(db_models.IdeaImage)
            .filter(db_models.IdeaImage.idea_id == idea_id)
            .order_by(db_models.IdeaImage.created_at.asc(), db_models.IdeaImage.id.asc())
            .all()
        )

    def get_by_id_for_idea(
        self, image_id: int, idea_id: int
    ) -> Optional[db_models.IdeaImage]:
        """Return an image only if it belongs to the given idea."""
        return (
            self.db.query(db_models.IdeaImage)
            .filter(
                db_models.IdeaImage.id == image_id,
                db_models.IdeaImage.idea_id == idea_id,
            )
            .first()
        )

    def create_image(
        self,
        idea_id: int,
        url: str,
        content_hash: Optional[str] = None,
    ) -> db_models.IdeaImage:
        """Persist a new image record for an idea."""
        image = db_models.IdeaImage(
            idea_id=idea_id, url=url, content_hash=content_hash
        )
        return self.create(image)

    def count_for_idea(self, idea_id: int) -> int:
        """Count images attached to an idea."""
        return (
            self.db.query(db_models.IdeaImage)
            .filter(db_models.IdeaImage.idea_id == idea_id)
            .count()
        )
