"""
Represents how a URL mapping is stored in MongoDB.

We keep this as a plain dict-producing dataclass-like model rather than a
full ODM, since Motor works directly with dicts. This keeps the dependency
list small while still giving us a single source of truth for the document
"shape".
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class URLDocument:
    original_url: str
    short_code: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    clicks: int = 0

    def to_dict(self) -> dict:
        return {
            "original_url": self.original_url,
            "short_code": self.short_code,
            "created_at": self.created_at,
            "clicks": self.clicks,
        }
