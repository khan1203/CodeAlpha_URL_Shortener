"""
Routes under /api/v1 for managing short URLs (create + look up info).
The actual redirect route lives in app/routers/redirect.py since it sits at
the root path ("/{short_code}") rather than under the API prefix.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.url import URLCreateRequest, URLCreateResponse, URLInfoResponse
from app.services.url_service import (
    ShortCodeGenerationError,
    build_short_url,
    create_short_url,
    get_url_by_short_code,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/urls", tags=["URLs"])


@router.post(
    "/shorten",
    response_model=URLCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a short URL for a given long URL",
)
async def shorten_url(payload: URLCreateRequest) -> URLCreateResponse:
    try:
        document = await create_short_url(str(payload.original_url))
    except ShortCodeGenerationError as exc:
        logger.error("Short code generation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not generate a short URL right now. Please try again.",
        ) from exc

    return URLCreateResponse(
        original_url=document["original_url"],
        short_code=document["short_code"],
        short_url=build_short_url(document["short_code"]),
        created_at=document["created_at"],
    )


@router.get(
    "/{short_code}",
    response_model=URLInfoResponse,
    summary="Get metadata about a short URL (does not redirect)",
)
async def get_url_info(short_code: str) -> URLInfoResponse:
    document = await get_url_by_short_code(short_code)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No URL found for short code '{short_code}'",
        )

    return URLInfoResponse(
        original_url=document["original_url"],
        short_code=document["short_code"],
        short_url=build_short_url(document["short_code"]),
        created_at=document["created_at"],
        clicks=document.get("clicks", 0),
    )
