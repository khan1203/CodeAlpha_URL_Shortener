"""
Root-level route: GET /{short_code} redirects the browser to the original
long URL. Kept in its own router (separate from /api/v1/urls) since it lives
at the root path and behaves differently (redirect, not JSON).
"""

import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from app.services.url_service import get_url_by_short_code, increment_click_count

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Redirect"])


@router.get("/{short_code}", include_in_schema=True, summary="Redirect to the original URL")
async def redirect_to_original(short_code: str) -> RedirectResponse:
    document = await get_url_by_short_code(short_code)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No URL found for short code '{short_code}'",
        )

    await increment_click_count(short_code)
    return RedirectResponse(url=document["original_url"], status_code=status.HTTP_307_TEMPORARY_REDIRECT)
