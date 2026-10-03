from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class Commit:
    """One commit node in the Mini Git DAG."""

    hash: str
    message: str
    author: str
    timestamp: str
    parents: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, hash_value: str, message: str, author: str, parents: list[str]) -> "Commit":
        timestamp = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        return cls(hash=hash_value, message=message, author=author, timestamp=timestamp, parents=list(parents))
