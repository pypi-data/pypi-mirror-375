"""
Cache management module for pyobis.
Handles HTTP request caching using requests-cache with filesystem backend.
"""

import logging
import os
import sys
from datetime import timedelta
from pathlib import Path

import requests
import requests_cache

logger = logging.getLogger(__name__)


def _get_cache_dir():
    """
    Get the appropriate cache directory for pyobis.
    Uses XDG_CACHE_HOME on Unix-like systems, %LOCALAPPDATA% on Windows.

    Returns:
        Path: The cache directory path.
    """
    if sys.platform.startswith("win"):
        cache_home = os.environ.get(
            "LOCALAPPDATA",
            str(Path.home() / "AppData" / "Local"),
        )
    else:
        cache_home = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))

    cache_dir = Path(cache_home) / "pyobis"
    return cache_dir


# Global default cache settings
_DEFAULT_CACHE_DIR = _get_cache_dir()
_DEFAULT_EXPIRE_AFTER = 86400  # 1 Day


def get_default_cache(enabled=True):
    """
    Get a default cache instance with standard settings.

    Args:
        enabled (bool): Whether caching is enabled. Defaults to True.

    Returns:
        Cache: A cache instance with default settings.
    """
    return Cache(
        enabled=enabled,
        cache_dir=_DEFAULT_CACHE_DIR,
    )


class Cache:
    """
    Cache manager for pyobis using requests-cache.
    Provides HTTP request caching with filesystem backend.

    The cache is stored in platform-specific locations:
    - Windows: %LOCALAPPDATA%\\pyobis (typically C:\\Users\\<username>\\AppData\\Local\\pyobis)
    - Unix-like (Linux/macOS): $XDG_CACHE_HOME/pyobis or ~/.cache/pyobis
    """

    def __init__(
        self,
        enabled=True,
        cache_dir=None,
        expire_after=_DEFAULT_EXPIRE_AFTER,
    ):
        """
        Initialize the cache manager.

        Args:
            enabled (bool, optional): Whether caching is enabled. Defaults to True.
            cache_dir (str, optional): Directory to store cache files.
                                     Defaults to platform-specific cache directory.
            expire_after (int, optional): Cache expiration time in seconds.
                                        Defaults to 1 day (86400 seconds).
        """
        self.enabled = enabled
        self.cache_dir = Path(cache_dir) if cache_dir else _DEFAULT_CACHE_DIR
        self.expire_after = expire_after

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            # Configure the cache session
            self.session = requests_cache.CachedSession(
                cache_name=str(self.cache_dir / "obis_cache"),
                backend="filesystem",
                expire_after=timedelta(seconds=expire_after),
                allowable_methods=["GET"],
                stale_if_error=True,
                cache_control=True,
                serializer=None,
                use_cache_dir=True,
                use_temp=True,
            )
            logger.info(f"Cache initialized at {self.cache_dir}")
        else:
            # Use a regular requests session when caching is disabled
            self.session = requests.Session()
            logger.info("Cache disabled - using regular requests session")

    def get_session(self):
        """
        Get the session for making requests.

        Returns:
            requests.Session or requests_cache.CachedSession: The session object.
        """
        return self.session

    def clear(self):
        """Clear all cached responses."""
        if self.enabled:
            self.session.cache.clear()
            logger.info("Cache cleared")

    def remove_expired(self):
        """Remove expired cache entries."""
        if self.enabled:
            self.session.cache.delete(expired=True)
            logger.info("Expired cache entries removed")

    def get_cache_info(self):
        """
        Get information about the cache.

        Returns:
            dict: Cache information including path, size, and count.
        """
        if not self.enabled:
            return {
                "cache_enabled": False,
                "cache_path": None,
                "cache_size": 0,
                "cache_count": 0,
                "expire_after": None,
            }

        total_size = 0
        for path in self.cache_dir.rglob("*"):
            if path.is_file():
                total_size += path.stat().st_size

        return {
            "cache_enabled": True,
            "cache_path": str(self.cache_dir),
            "cache_size": total_size,
            "cache_count": (
                len(self.session.cache.responses)
                if hasattr(self.session, "cache")
                else 0
            ),
            "expire_after": timedelta(seconds=self.expire_after),
        }

    def close(self):
        """Close the session and release all resources."""
        if hasattr(self, "session"):
            self.session.close()
            if self.enabled and hasattr(self.session, "cache"):
                self.session.cache.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
