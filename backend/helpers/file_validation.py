"""
Lightweight, dependency-free file type detection.

The upstream project relies on ``python-magic`` which requires the native
libmagic library. On some Windows setups importing it blocks indefinitely, so
image validation is done by inspecting well-known magic bytes instead.
"""

from typing import Optional


def detect_image_mime(content: bytes) -> Optional[str]:
    """Return the detected image MIME type, or None if unsupported.

    Supports JPEG, PNG, GIF and WebP.
    """
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if content[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if (
        len(content) >= 12
        and content[:4] == b"RIFF"
        and content[8:12] == b"WEBP"
    ):
        return "image/webp"
    return None
