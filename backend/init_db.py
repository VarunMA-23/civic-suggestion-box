"""Initialize the database with default categories and an admin user."""

from authentication.auth import get_password_hash
from models.config import settings
from repositories.database import Base, SessionLocal, engine
from repositories.db_models import Category, User
from services.config_service import get_entity_name

# Create tables
Base.metadata.create_all(bind=engine)


def get_default_categories() -> list[dict]:
    """Get default categories for the Bengaluru civic instance.

    The database schema keeps legacy ``name_fr`` / ``description_fr`` columns
    for compatibility, but this English-only demo mirrors the English values
    into them so no French text is shown.

    Returns:
        List of category dictionaries with localized names and descriptions.
    """
    entity_en = get_entity_name("en")

    def localized(name: str, description: str) -> dict:
        return {
            "name_en": name,
            "name_fr": name,
            "description_en": description,
            "description_fr": description,
        }

    return [
        localized(
            "Roads & Infrastructure",
            f"Report potholes, footpaths, road repairs, and infrastructure issues in {entity_en}"
            if entity_en
            else "Report potholes, footpaths, road repairs, and infrastructure issues",
        ),
        localized(
            "Waste Management & Sanitation",
            "Report garbage collection, street sweeping, and sanitation concerns",
        ),
        localized(
            "Water Supply & Drainage",
            "Report water supply interruptions, pipeline leaks, and storm-water drain issues",
        ),
        localized(
            "Public Transport",
            "Improve BMTC buses, Namma Metro, and last-mile connectivity",
        ),
        localized(
            "Electricity & Street Lighting",
            "Report power outages and non-functional street lights",
        ),
        localized(
            "Public Safety & Policing",
            "Improve safety, traffic enforcement, and emergency response",
        ),
        localized(
            "Parks, Lakes & Environment",
            "Protect lakes, parks, trees, and green spaces",
        ),
        localized(
            "Health & Education",
            "Improve public health services, schools, and anganwadis",
        ),
        localized(
            "Civic Services & Digital Governance",
            "Improve BBMP services, permits, and digital access",
        ),
        localized(
            "Community & Culture",
            "Support neighborhood events, libraries, and community programs",
        ),
    ]


def init_db():
    """Initialize the database with default data."""
    db = SessionLocal()

    try:
        # Check if categories already exist
        existing_categories = db.query(Category).first()
        if not existing_categories:
            categories = [Category(**cat) for cat in get_default_categories()]
            for category in categories:
                db.add(category)
            db.commit()
            print("[OK] Default categories created")

        # Check if admin user exists
        existing_admin = (
            db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        )
        if not existing_admin:
            # Create default admin user with password from settings/.env
            from datetime import datetime, timezone

            now = datetime.now(timezone.utc)
            admin = User(
                email=settings.ADMIN_EMAIL,
                username="admin",
                display_name="Administrator",
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                is_global_admin=True,
                # Consent fields (Law 25 compliance) - admin implicitly consents
                consent_terms_accepted=True,
                consent_privacy_accepted=True,
                consent_terms_version="1.0",
                consent_privacy_version="1.0",
                consent_timestamp=now,
                marketing_consent=False,
            )
            db.add(admin)
            db.commit()
            print("[OK] Admin user created")
            print(f"  Email: {settings.ADMIN_EMAIL}")
            print("  Password: (from ADMIN_PASSWORD in .env)")
            print("  IMPORTANT: Change this password in production!")

        print("\n[OK] Database initialization complete!")

    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
