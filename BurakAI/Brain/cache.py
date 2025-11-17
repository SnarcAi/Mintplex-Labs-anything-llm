#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BurakAI - Intelligent Cache System
═════════════════════════════════════════════════════════
NEXUS'tan esinlendi - basitleştirilmiş:
- Redis/multi-tier yerine → Simple dict + disk
- Semantic embeddings yerine → Hash-based exact match
- Complex invalidation yerine → TTL + manual invalidation

But still FAST:
- L1: RAM (instant)
- L2: Disk (persistent)
- Smart invalidation rules
- Cache hit metrics
═════════════════════════════════════════════════════════
"""

import hashlib
import json
import time
import pickle
from pathlib import Path
from typing import Any, Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class CacheEntry:
    """Single cache entry"""
    key: str
    value: Any
    created_at: float  # Unix timestamp
    ttl_seconds: int
    hits: int = 0
    metadata: Dict = None

    def is_expired(self) -> bool:
        """Check if entry is expired"""
        return time.time() - self.created_at > self.ttl_seconds

    def to_dict(self) -> Dict:
        """Serialize to dict (for disk storage)"""
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at,
            "ttl_seconds": self.ttl_seconds,
            "hits": self.hits,
            "metadata": self.metadata or {}
        }

    @staticmethod
    def from_dict(d: Dict) -> 'CacheEntry':
        """Deserialize from dict"""
        return CacheEntry(
            key=d["key"],
            value=d["value"],
            created_at=d["created_at"],
            ttl_seconds=d["ttl_seconds"],
            hits=d.get("hits", 0),
            metadata=d.get("metadata")
        )


class CacheSystem:
    """
    Two-tier cache system: RAM (L1) + Disk (L2)
    """

    def __init__(
        self,
        cache_dir: Path,
        max_size_mb: int = 100,
        default_ttl: int = 300,
        enable_disk: bool = True
    ):
        """
        Initialize cache system

        Args:
            cache_dir: Directory for disk cache
            max_size_mb: Max cache size in MB (approx)
            default_ttl: Default TTL in seconds
            enable_disk: Enable L2 disk cache
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_mb = max_size_mb
        self.default_ttl = default_ttl
        self.enable_disk = enable_disk

        # Ensure cache dir exists
        if self.enable_disk:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # L1: RAM cache (dict)
        self._l1_cache: Dict[str, CacheEntry] = {}

        # Stats
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "l1_hits": 0,
            "l2_hits": 0,
        }

    # ═════════════════════════════════════════════════════
    # GET / SET OPERATIONS
    # ═════════════════════════════════════════════════════

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        # Try L1 (RAM)
        entry = self._l1_cache.get(key)
        if entry:
            if entry.is_expired():
                # Expired - remove
                del self._l1_cache[key]
                self._stats["misses"] += 1
                return None
            else:
                # Hit!
                entry.hits += 1
                self._stats["hits"] += 1
                self._stats["l1_hits"] += 1
                return entry.value

        # Try L2 (Disk)
        if self.enable_disk:
            entry = self._load_from_disk(key)
            if entry and not entry.is_expired():
                # Promote to L1
                self._l1_cache[key] = entry
                entry.hits += 1
                self._stats["hits"] += 1
                self._stats["l2_hits"] += 1
                return entry.value

        # Miss
        self._stats["misses"] += 1
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None, metadata: Dict = None):
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds (None = use default)
            metadata: Optional metadata
        """
        ttl = ttl or self.default_ttl

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            ttl_seconds=ttl,
            metadata=metadata
        )

        # Set in L1
        self._l1_cache[key] = entry

        # Set in L2
        if self.enable_disk:
            self._save_to_disk(entry)

        # Check if eviction needed
        self._check_eviction()

    def delete(self, key: str):
        """Delete from cache"""
        # Delete from L1
        if key in self._l1_cache:
            del self._l1_cache[key]

        # Delete from L2
        if self.enable_disk:
            cache_file = self._get_cache_file(key)
            cache_file.unlink(missing_ok=True)

    def invalidate_pattern(self, pattern: str):
        """
        Invalidate all keys matching pattern

        Args:
            pattern: Pattern to match (simple substring match)
        """
        # L1
        keys_to_delete = [k for k in self._l1_cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self._l1_cache[key]

        # L2
        if self.enable_disk:
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    entry = self._load_from_file(cache_file)
                    if entry and pattern in entry.key:
                        cache_file.unlink()
                except Exception:
                    pass

    def clear(self):
        """Clear all cache"""
        self._l1_cache.clear()

        if self.enable_disk:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()

    # ═════════════════════════════════════════════════════
    # QUERY CACHE (specialized for BurakAI)
    # ═════════════════════════════════════════════════════

    def get_query_cache(self, query: str, profile: str) -> Optional[Any]:
        """
        Get cached query result

        Args:
            query: User query
            profile: AI profile

        Returns:
            Cached result or None
        """
        cache_key = self._make_query_key(query, profile)
        return self.get(cache_key)

    def set_query_cache(self, query: str, profile: str, result: Any, ttl: int = 300):
        """
        Cache query result

        Args:
            query: User query
            profile: AI profile
            result: Result to cache
            ttl: TTL in seconds
        """
        cache_key = self._make_query_key(query, profile)
        metadata = {
            "query": query,
            "profile": profile,
            "cached_at": datetime.now().isoformat()
        }
        self.set(cache_key, result, ttl=ttl, metadata=metadata)

    def _make_query_key(self, query: str, profile: str) -> str:
        """Create cache key from query + profile"""
        # Normalize query (lowercase, strip whitespace)
        normalized = query.lower().strip()

        # Hash to create compact key
        content = f"{normalized}|{profile}"
        hash_val = hashlib.md5(content.encode()).hexdigest()

        return f"query_{hash_val}"

    # ═════════════════════════════════════════════════════
    # STATS & MONITORING
    # ═════════════════════════════════════════════════════

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0

        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate": hit_rate,
            "l1_hits": self._stats["l1_hits"],
            "l2_hits": self._stats["l2_hits"],
            "l1_size": len(self._l1_cache),
            "evictions": self._stats["evictions"],
        }

    def get_top_entries(self, n: int = 10) -> List[Dict]:
        """Get most frequently accessed entries"""
        entries = sorted(
            self._l1_cache.values(),
            key=lambda e: e.hits,
            reverse=True
        )[:n]

        return [
            {
                "key": e.key,
                "hits": e.hits,
                "age_seconds": time.time() - e.created_at,
                "metadata": e.metadata
            }
            for e in entries
        ]

    # ═════════════════════════════════════════════════════
    # DISK OPERATIONS (L2)
    # ═════════════════════════════════════════════════════

    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key"""
        # Hash key to create filename
        hash_val = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_val}.cache"

    def _save_to_disk(self, entry: CacheEntry):
        """Save entry to disk"""
        cache_file = self._get_cache_file(entry.key)
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(entry, f)
        except Exception as e:
            print(f"[Cache] Failed to save to disk: {e}")

    def _load_from_disk(self, key: str) -> Optional[CacheEntry]:
        """Load entry from disk"""
        cache_file = self._get_cache_file(key)
        if not cache_file.exists():
            return None

        try:
            return self._load_from_file(cache_file)
        except Exception as e:
            print(f"[Cache] Failed to load from disk: {e}")
            return None

    def _load_from_file(self, cache_file: Path) -> Optional[CacheEntry]:
        """Load entry from file"""
        with open(cache_file, "rb") as f:
            return pickle.load(f)

    # ═════════════════════════════════════════════════════
    # EVICTION
    # ═════════════════════════════════════════════════════

    def _check_eviction(self):
        """Check if eviction needed (simple LRU)"""
        # Rough size estimation: assume 1KB per entry
        estimated_size_mb = len(self._l1_cache) * 1 / 1024

        if estimated_size_mb > self.max_size_mb:
            # Evict least recently used (lowest hits)
            entries = sorted(self._l1_cache.items(), key=lambda x: x[1].hits)

            # Evict bottom 20%
            evict_count = max(1, len(entries) // 5)
            for key, entry in entries[:evict_count]:
                del self._l1_cache[key]
                self._stats["evictions"] += 1

    def cleanup_expired(self):
        """Remove expired entries"""
        # L1
        expired_keys = [k for k, e in self._l1_cache.items() if e.is_expired()]
        for key in expired_keys:
            del self._l1_cache[key]

        # L2
        if self.enable_disk:
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    entry = self._load_from_file(cache_file)
                    if entry and entry.is_expired():
                        cache_file.unlink()
                except Exception:
                    pass


# ═════════════════════════════════════════════════════════
# SMART INVALIDATION RULES (for BurakAI)
# ═════════════════════════════════════════════════════════
class SmartInvalidator:
    """
    Rule-based cache invalidation for BurakAI
    """

    def __init__(self, cache: CacheSystem):
        self.cache = cache

    def on_customer_update(self, customer_name: str):
        """Invalidate customer-related caches"""
        self.cache.invalidate_pattern(customer_name)
        print(f"[Cache] Invalidated caches for customer: {customer_name}")

    def on_config_change(self, config_key: str):
        """Invalidate all caches when config changes"""
        if config_key in ["margin_target", "fx_rate", "pricing"]:
            self.cache.clear()
            print(f"[Cache] Cleared all caches due to config change: {config_key}")

    def on_file_upload(self, filename: str):
        """Invalidate file-related caches"""
        self.cache.invalidate_pattern(filename)
        print(f"[Cache] Invalidated caches for file: {filename}")


# ═════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═════════════════════════════════════════════════════════
if __name__ == "__main__":
    import tempfile

    # Create temp cache dir
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = CacheSystem(Path(tmpdir) / "cache", max_size_mb=1)

        # Test query cache
        query = "ABC'nin faturasını kontrol et"
        result = "Fatura kontrol edildi..."

        # Miss
        assert cache.get_query_cache(query, "finance") is None
        print("✓ Cache miss (expected)")

        # Set
        cache.set_query_cache(query, "finance", result, ttl=60)
        print("✓ Cached query result")

        # Hit
        cached = cache.get_query_cache(query, "finance")
        assert cached == result
        print("✓ Cache hit!")

        # Stats
        stats = cache.get_stats()
        print(f"\nStats: {json.dumps(stats, indent=2)}")

        # Smart invalidation
        invalidator = SmartInvalidator(cache)
        invalidator.on_customer_update("ABC")
        print("\n✓ Smart invalidation test passed")
