"""Preview cache tests."""

from __future__ import annotations

from auraforge_engine.io.preview_cache import PreviewCache


def test_cache_hit_miss() -> None:
    cache = PreviewCache(max_entries=2)
    key = cache.make_key(b"abc", strength=50, mode="natural")
    assert cache.get(key) is None
    cache.set(key, {"preview": "data"})
    hit = cache.get(key)
    assert hit is not None
    assert hit["preview"] == "data"
    assert cache.stats.hits == 1
    assert cache.stats.misses == 1


def test_cache_eviction() -> None:
    cache = PreviewCache(max_entries=2)
    cache.set("a", {"v": 1})
    cache.set("b", {"v": 2})
    cache.set("c", {"v": 3})
    assert cache.get("a") is None
    assert cache.get("c") is not None
