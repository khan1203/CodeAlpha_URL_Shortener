"""
Pydantic schemas used for request validation and response serialization.
These are separate from the DB model (app/models/url.py) on purpose, so the
API's public "contract" can evolve independently of how data is stored.
"""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class URLCreateRequest(BaseModel):
    original_url: HttpUrl = Field(..., description="The long URL to shorten")

    model_config = {
        "json_schema_extra": {
            "examples": [{"original_url": "https://www.example.com/some/very/long/path"}]
        }
    }


class URLCreateResponse(BaseModel):
    original_url: str
    short_code: str
    short_url: str
    created_at: datetime


class URLInfoResponse(BaseModel):
    original_url: str
    short_code: str
    short_url: str
    created_at: datetime
    clicks: int
