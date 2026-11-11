"""
Tests for the civic geo layer: idea locations, images, map and hotspots.
"""

import struct
import zlib

from fastapi.testclient import TestClient


def make_png() -> bytes:
    """Build a tiny valid PNG image in memory."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0)
    raw = b"\x00\xff\x00\x00\xff\x00\x00" + b"\x00\x00\xff\x00\x00\x00\xff"
    idat = zlib.compress(raw)
    return (
        signature
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", idat)
        + chunk(b"IEND", b"")
    )


LOCATION_PAYLOAD = {
    "latitude": 45.5019,
    "longitude": -73.5674,
    "neighborhood": "Testville",
    "address": "123 Test Street",
}


def test_set_and_get_location(client: TestClient, auth_headers, test_idea):
    response = client.post(
        f"/api/ideas/{test_idea.id}/location",
        json=LOCATION_PAYLOAD,
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["idea_id"] == test_idea.id
    assert data["neighborhood"] == "Testville"

    response = client.get(f"/api/ideas/{test_idea.id}/location")
    assert response.status_code == 200
    assert response.json()["latitude"] == LOCATION_PAYLOAD["latitude"]


def test_location_upsert_updates_existing(client: TestClient, auth_headers, test_idea):
    client.post(
        f"/api/ideas/{test_idea.id}/location",
        json=LOCATION_PAYLOAD,
        headers=auth_headers,
    )
    updated = {**LOCATION_PAYLOAD, "neighborhood": "Newville"}
    response = client.post(
        f"/api/ideas/{test_idea.id}/location",
        json=updated,
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["neighborhood"] == "Newville"

    response = client.get(f"/api/ideas/{test_idea.id}/location")
    assert response.json()["neighborhood"] == "Newville"


def test_location_requires_authentication(client: TestClient, test_idea):
    response = client.post(
        f"/api/ideas/{test_idea.id}/location", json=LOCATION_PAYLOAD
    )
    assert response.status_code == 401


def test_location_rejects_other_user(client: TestClient, other_user, test_idea):
    from authentication.auth import create_access_token

    token = create_access_token(data={"sub": other_user.email})
    response = client.post(
        f"/api/ideas/{test_idea.id}/location",
        json=LOCATION_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_location_validates_coordinates(client: TestClient, auth_headers, test_idea):
    response = client.post(
        f"/api/ideas/{test_idea.id}/location",
        json={"latitude": 200, "longitude": 0},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_idea_detail_includes_location(client: TestClient, auth_headers, test_idea):
    client.post(
        f"/api/ideas/{test_idea.id}/location",
        json=LOCATION_PAYLOAD,
        headers=auth_headers,
    )
    response = client.get(f"/api/ideas/{test_idea.id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["location"] is not None
    assert data["location"]["neighborhood"] == "Testville"


def test_map_returns_approved_ideas_in_bounds(
    client: TestClient, auth_headers, test_idea
):
    client.post(
        f"/api/ideas/{test_idea.id}/location",
        json=LOCATION_PAYLOAD,
        headers=auth_headers,
    )
    response = client.get(
        "/api/ideas/map",
        params={
            "min_lat": 45.0,
            "min_lng": -74.0,
            "max_lat": 46.0,
            "max_lng": -73.0,
        },
    )
    assert response.status_code == 200, response.text
    items = response.json()
    assert len(items) == 1
    assert items[0]["id"] == test_idea.id
    assert items[0]["neighborhood"] == "Testville"


def test_map_excludes_ideas_outside_bounds(client: TestClient, auth_headers, test_idea):
    client.post(
        f"/api/ideas/{test_idea.id}/location",
        json=LOCATION_PAYLOAD,
        headers=auth_headers,
    )
    response = client.get(
        "/api/ideas/map",
        params={
            "min_lat": 10.0,
            "min_lng": 10.0,
            "max_lat": 11.0,
            "max_lng": 11.0,
        },
    )
    assert response.status_code == 200
    assert response.json() == []


def test_map_rejects_invalid_bbox(client: TestClient):
    response = client.get(
        "/api/ideas/map",
        params={
            "min_lat": 46.0,
            "min_lng": -73.0,
            "max_lat": 45.0,
            "max_lng": -74.0,
        },
    )
    assert response.status_code == 422


def test_hotspots_group_by_neighborhood(client: TestClient, auth_headers, test_idea):
    client.post(
        f"/api/ideas/{test_idea.id}/location",
        json=LOCATION_PAYLOAD,
        headers=auth_headers,
    )
    response = client.get("/api/ideas/hotspots")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total"] == 1
    assert data["neighborhoods"][0]["neighborhood"] == "Testville"
    assert data["neighborhoods"][0]["count"] == 1


def test_upload_and_list_image(client: TestClient, auth_headers, test_idea):
    response = client.post(
        f"/api/ideas/{test_idea.id}/images",
        files={"file": ("test.png", make_png(), "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    image = response.json()
    assert image["idea_id"] == test_idea.id
    assert image["content_hash"]

    response = client.get(f"/api/ideas/{test_idea.id}/images")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_upload_rejects_non_image(client: TestClient, auth_headers, test_idea):
    response = client.post(
        f"/api/ideas/{test_idea.id}/images",
        files={"file": ("notes.txt", b"just some text", "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_delete_image(client: TestClient, auth_headers, test_idea):
    created = client.post(
        f"/api/ideas/{test_idea.id}/images",
        files={"file": ("test.png", make_png(), "image/png")},
        headers=auth_headers,
    ).json()

    response = client.delete(
        f"/api/ideas/{test_idea.id}/images/{created['id']}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["deleted"] is True

    response = client.get(f"/api/ideas/{test_idea.id}/images")
    assert response.json() == []
