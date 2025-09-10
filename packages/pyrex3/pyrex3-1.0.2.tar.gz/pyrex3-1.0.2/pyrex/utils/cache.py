"""
Advanced caching system for compiled binaries and execution results.
This module provides intelligent caching with dependency tracking,
automatic cleanup, and performance monitoring.
"""

import json
import logging
import pickle
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Set, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a single cache entry with metadata."""

    key: str
    timestamp: float
    last_accessed: float
    access_count: int
    size_bytes: int
    language: str
    variables_hash: str


class CacheManager:
    """
    Advanced caching manager with intelligent cleanup and monitoring.
    Features:
    - LRU eviction with access tracking
    - Automatic cleanup of expired entries
    - Memory usage monitoring
    - Thread-safe operations
    - Persistent cache index
    """
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        max_entries: int = 1000,
        max_size_mb: int = 500,
        ttl_hours: int = 24,
    ) -> None:
        """
        Initialize the cache manager.
        Args:
            cache_dir: Custom cache directory (None for system temp)
            max_entries: Maximum number of cached entries
            max_size_mb: Maximum cache size in megabytes
            ttl_hours: Time to live for entries in hours
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path(tempfile.gettempdir()) / "pyrex_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_entries = max_entries
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl_seconds = ttl_hours * 3600
        self._lock = threading.RLock()
        self._index: Dict[str, CacheEntry] = {}
        self._load_index()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "cleanups": 0,
        }
        self._last_cleanup = time.time()
        self._cleanup_interval = 3600  # 1h
        logger.debug(f"Initialized cache manager: {self.cache_dir}")

    def _load_index(self) -> None:
        """Load the cache index from disk."""
        index_file = self.cache_dir / "cache_index.json"
        if not index_file.exists():
            return
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key, entry_data in data.items():
                if isinstance(entry_data, dict):
                    self._index[key] = CacheEntry(**entry_data)
            logger.debug(f"Loaded {len(self._index)} cache entries from index")
        except (json.JSONDecodeError, FileNotFoundError, TypeError) as e:
            logger.warning(f"Failed to load cache index: {e}")
            self._index.clear()

    def _save_index(self) -> None:
        """Save the cache index to disk."""
        index_file = self.cache_dir / "cache_index.json"
        try:
            data = {key: asdict(entry) for key, entry in self._index.items()}
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, sort_keys=True)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")

    def _get_cache_file_path(self, key: str) -> Path:
        """Get the file path for a cache entry."""
        subdir = key[:2]
        cache_subdir = self.cache_dir / subdir
        cache_subdir.mkdir(exist_ok=True)
        return cache_subdir / f"{key}.pkl"

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if a cache entry has expired."""
        return time.time() - entry.timestamp > self.ttl_seconds

    def _cleanup_expired(self) -> None:
        """Remove expired cache entries."""
        current_time = time.time()
        expired_keys = []
        for key, entry in self._index.items():
            if current_time - entry.timestamp > self.ttl_seconds:
                expired_keys.append(key)
        for key in expired_keys:
            self._remove_entry(key)
        if expired_keys:
            self._stats["cleanups"] += len(expired_keys)
            logger.debug(
                f"Cleaned up {len(expired_keys)} expired cache entries"
            )

    def _enforce_size_limits(self) -> None:
        """Enforce cache size and entry count limits."""
        if len(self._index) <= self.max_entries:
            total_size = sum(entry.size_bytes for entry in self._index.values())
            if total_size <= self.max_size_bytes:
                return
        sorted_entries = sorted(
            self._index.items(),
            key=lambda x: (x[1].last_accessed, x[1].access_count)
        )
        current_size = sum(entry.size_bytes for entry in self._index.values())
        entries_removed = 0
        for key, entry in sorted_entries:
            if (
                len(self._index) <= self.max_entries and
                current_size <= self.max_size_bytes
            ):
                break
            self._remove_entry(key)
            current_size -= entry.size_bytes
            entries_removed += 1
        if entries_removed > 0:
            self._stats["evictions"] += entries_removed
            logger.debug(
                f"Evicted {entries_removed} cache entries to enforce limits"
            )

    def _remove_entry(self, key: str) -> None:
        """Remove a single cache entry."""
        if key not in self._index:
            return
        cache_file = self._get_cache_file_path(key)
        cache_file.unlink(missing_ok=True)
        del self._index[key]

    def _maybe_cleanup(self) -> None:
        """Perform cleanup if it's been long enough."""
        current_time = time.time()
        if current_time - self._last_cleanup > self._cleanup_interval:
            self._cleanup_expired()
            self._enforce_size_limits()
            self._save_index()
            self._last_cleanup = current_time

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        Args:
            key: Cache key
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            self._maybe_cleanup()
            if key not in self._index:
                self._stats["misses"] += 1
                return None
            entry = self._index[key]
            if self._is_expired(entry):
                self._remove_entry(key)
                self._stats["misses"] += 1
                return None
            cache_file = self._get_cache_file_path(key)
            if not cache_file.exists():
                self._remove_entry(key)
                self._stats["misses"] += 1
                return None
            try:
                with open(cache_file, "rb") as f:
                    value = pickle.load(f)
                entry.last_accessed = time.time()
                entry.access_count += 1
                self._stats["hits"] += 1
                return value
            except (pickle.UnpicklingError, FileNotFoundError, EOFError) as e:
                logger.warning(f"Failed to load cache entry {key}: {e}")
                self._remove_entry(key)
                self._stats["misses"] += 1
                return None

    def set(
        self,
        key: str,
        value: Any,
        language: str = "unknown",
        variables_hash: str = "",
    ) -> None:
        """
        Store a value in the cache.
        Args:
            key: Cache key
            value: Value to cache
            language: Programming language for categorization
            variables_hash: Hash of variables used
        """
        with self._lock:
            self._maybe_cleanup()
            cache_file = self._get_cache_file_path(key)
            try:
                with open(cache_file, "wb") as f:
                    pickle.dump(value, f)
                file_size = cache_file.stat().st_size
                current_time = time.time()
                entry = CacheEntry(
                    key=key,
                    timestamp=current_time,
                    last_accessed=current_time,
                    access_count=1,
                    size_bytes=file_size,
                    language=language,
                    variables_hash=variables_hash,
                )
                self._index[key] = entry
                self._enforce_size_limits()
                logger.debug(f"Cached entry {key} ({file_size} bytes)")
            except Exception as e:
                logger.error(f"Failed to cache entry {key}: {e}")
                cache_file.unlink(missing_ok=True)
                if key in self._index:
                    del self._index[key]
                raise

    def clear(self, language: Optional[str] = None) -> None:
        """
        Clear cache entries.
        Args:
            language: If specified, only clear entries for this language
        """
        with self._lock:
            keys_to_remove = []
            if language:
                keys_to_remove = [
                    key for key, entry in self._index.items()
                    if entry.language == language
                ]
            else:
                keys_to_remove = list(self._index.keys())
            for key in keys_to_remove:
                self._remove_entry(key)
            for subdir in self.cache_dir.iterdir():
                if subdir.is_dir() and not any(subdir.iterdir()):
                    subdir.rmdir()
            self._save_index()
            logger.info(f"Cleared {len(keys_to_remove)} cache entries")

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        with self._lock:
            total_size = sum(entry.size_bytes for entry in self._index.values())
            language_stats = {}
            for entry in self._index.values():
                lang = entry.language
                if lang not in language_stats:
                    language_stats[lang] = {"count": 0, "size": 0}
                language_stats[lang]["count"] += 1
                language_stats[lang]["size"] += entry.size_bytes
            current_time = time.time()
            age_buckets = {"<1h": 0, "1-6h": 0, "6-24h": 0, ">24h": 0}
            for entry in self._index.values():
                age_hours = (current_time - entry.timestamp) / 3600
                if age_hours < 1:
                    age_buckets["<1h"] += 1
                elif age_hours < 6:
                    age_buckets["1-6h"] += 1
                elif age_hours < 24:
                    age_buckets["6-24h"] += 1
                else:
                    age_buckets[">24h"] += 1
            return {
                "entries": len(self._index),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "cache_dir": str(self.cache_dir),
                "limits":
                    {
                        "max_entries": self.max_entries,
                        "max_size_mb": self.max_size_bytes // (1024 * 1024),
                        "ttl_hours": self.ttl_seconds // 3600,
                    },
                "performance": self._stats.copy(),
                "hit_rate":
                    (
                        self._stats["hits"] /
                        (self._stats["hits"] + self._stats["misses"]) if
                        (self._stats["hits"] + self._stats["misses"]) > 0 else 0
                    ),
                "languages": language_stats,
                "age_distribution": age_buckets,
            }
