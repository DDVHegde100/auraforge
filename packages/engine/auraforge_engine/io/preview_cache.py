"""In-memory LRU cache for enhance preview responses."""

from __future__ import annotations

import hashlib
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    size: int = 0
    max_size: int = 32

    def to_dict(self) -> dict[str, int]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "size": self.size,
            "max_size": self.max_size,
        }


class PreviewCache:
    def __init__(self, max_entries: int = 48) -> None:
        self.max_entries = max_entries
        self._data: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self.stats = CacheStats(max_size=max_entries)

    def make_key(self, file_bytes: bytes, **params: Any) -> str:
        digest = hashlib.sha256(file_bytes).hexdigest()[:20]
        parts = "|".join(f"{k}={params[k]}" for k in sorted(params))
        return f"{digest}:{parts}"

    def get(self, key: str) -> dict[str, Any] | None:
        if key not in self._data:
            self.stats.misses += 1
            return None
        self._data.move_to_end(key)
        self.stats.hits += 1
        return self._data[key]

    def set(self, key: str, value: dict[str, Any]) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        while len(self._data) > self.max_entries:
            self._data.popitem(last=False)
        self.stats.size = len(self._data)

    def clear(self) -> None:
        self._data.clear()
        self.stats.size = 0


PREVIEW_CACHE = PreviewCache()
