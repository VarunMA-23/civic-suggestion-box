"""Unit tests for init_db functionality."""

from unittest.mock import patch

import pytest

from services.config_service import clear_config_cache


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear config cache before each test."""
    clear_config_cache()
    yield
    clear_config_cache()


class TestGetDefaultCategories:
    """Tests for get_default_categories function."""

    def test_returns_list_of_categories(self):
        """Should return a list of category dictionaries."""
        from init_db import get_default_categories

        categories = get_default_categories()

        assert isinstance(categories, list)
        assert len(categories) > 0

    def test_categories_have_required_fields(self):
        """Each category should have required bilingual fields."""
        from init_db import get_default_categories

        categories = get_default_categories()

        for cat in categories:
            assert "name_en" in cat
            assert "name_fr" in cat
            assert "description_en" in cat
            assert "description_fr" in cat

    def test_category_descriptions_use_entity_name(self):
        """Category descriptions should include entity name from config."""
        # Mock the config to return a custom entity name
        with patch("init_db.get_entity_name") as mock_get_entity:
            mock_get_entity.return_value = "TestCity"

            from init_db import get_default_categories

            categories = get_default_categories()

        # Roads category should mention the entity
        roads_cat = next(c for c in categories if c["name_en"] == "Roads & Infrastructure")
        assert "TestCity" in roads_cat["description_en"]
        assert "TestCity" in roads_cat["description_fr"]

    def test_handles_empty_entity_name(self):
        """Should provide fallback description when entity name is empty."""
        with patch("init_db.get_entity_name") as mock_get_entity:
            mock_get_entity.return_value = ""

            from init_db import get_default_categories

            categories = get_default_categories()

        # Should still have valid descriptions
        for cat in categories:
            assert len(cat["description_en"]) > 0
            assert len(cat["description_fr"]) > 0

    def test_includes_expected_categories(self):
        """Should include Bengaluru civic categories."""
        from init_db import get_default_categories

        categories = get_default_categories()
        category_names = [c["name_en"] for c in categories]

        expected = [
            "Roads & Infrastructure",
            "Waste Management & Sanitation",
            "Water Supply & Drainage",
            "Public Transport",
            "Electricity & Street Lighting",
            "Public Safety & Policing",
            "Parks, Lakes & Environment",
            "Health & Education",
            "Civic Services & Digital Governance",
            "Community & Culture",
        ]

        for expected_name in expected:
            assert expected_name in category_names, f"Missing category: {expected_name}"

    def test_roads_category_uses_entity_name(self):
        """Roads category should reference the entity."""
        with patch("init_db.get_entity_name") as mock_get_entity:
            mock_get_entity.return_value = "Bengaluru"

            from init_db import get_default_categories

            categories = get_default_categories()

        roads_cat = next(c for c in categories if c["name_en"] == "Roads & Infrastructure")
        assert "Bengaluru" in roads_cat["description_en"]
        assert "Bengaluru" in roads_cat["description_fr"]

    def test_some_categories_do_not_require_entity(self):
        """Some categories like waste management don't need entity name."""
        from init_db import get_default_categories

        categories = get_default_categories()

        waste_cat = next(
            c for c in categories if c["name_en"] == "Waste Management & Sanitation"
        )

        # Waste category has generic description
        assert "garbage collection" in waste_cat["description_en"]
        assert "garbage collection" in waste_cat["description_fr"]
