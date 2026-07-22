"""
Business logic layer. Routers should stay "thin" (parse request, call a
service, return response) and put the actual logic here so it's testable
and reusable independent of the web framework.
"""

from pymongo.errors import DuplicateKeyError

from app.core.config import settings
from app.core.database import get_url_collection
from app.models.url import URLDocument
from app.utils.shortcode import generate_short_code

MAX_GENERATION_ATTEMPTS = 5


class ShortCodeGenerationError(Exception):
    """Raised when we fail to generate a unique short code after several tries."""


async def create_short_url(original_url: str) -> dict:
    collection = get_url_collection()

    for _ in range(MAX_GENERATION_ATTEMPTS):
        short_code = generate_short_code(settings.short_code_length)
        document = URLDocument(original_url=original_url, short_code=short_code)
        try:
            await collection.insert_one(document.to_dict())
            return document.to_dict()
        except DuplicateKeyError:
            # Extremely unlikely collision on short_code - just retry with a new one.
            continue

    raise ShortCodeGenerationError(
        "Could not generate a unique short code, please try again."
    )


async def get_url_by_short_code(short_code: str) -> dict | None:
    collection = get_url_collection()
    return await collection.find_one({"short_code": short_code})


async def increment_click_count(short_code: str) -> None:
    collection = get_url_collection()
    await collection.update_one({"short_code": short_code}, {"$inc": {"clicks": 1}})


def build_short_url(short_code: str) -> str:
    return f"{settings.base_url.rstrip('/')}/{short_code}"
