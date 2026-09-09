"""
utils/cache.py
Caching system for Coconut Grading AI
Stores and retrieves cached analysis results for performance
"""

from datetime import datetime, timedelta
from typing import Optional, Any, Dict
import hashlib
import json


class Cache:
    """In-memory cache for analysis results"""
    
    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize cache
        
        Args:
            ttl_seconds: Time to live for cache entries (default 1 hour)
        """
        self.ttl = timedelta(seconds=ttl_seconds)
        self.cache = {}
    
    def _generate_key(self, data: str) -> str:
        """Generate cache key from data hash"""
        return hashlib.md5(data.encode()).hexdigest()
    
    def set(self, key: str, value: Any) -> None:
        """
        Set cache value
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = {
            "value": value,
            "created_at": datetime.now(),
            "ttl": self.ttl
        }
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cache value
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found or expired
        """
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if datetime.now() - entry["created_at"] > entry["ttl"]:
            del self.cache[key]
            return None
        
        return entry["value"]
    
    def exists(self, key: str) -> bool:
        """Check if key exists and hasn't expired"""
        return self.get(key) is not None
    
    def delete(self, key: str) -> bool:
        """Delete cache entry"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if datetime.now() - entry["created_at"] > entry["ttl"]
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def get_size(self) -> int:
        """Get number of cache entries"""
        return len(self.cache)


class ModelCache:
    """Cache for model predictions and results"""
    
    def __init__(self, max_entries: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize model cache
        
        Args:
            max_entries: Maximum cache entries
            ttl_seconds: Time to live for entries
        """
        self.max_entries = max_entries
        self.ttl = timedelta(seconds=ttl_seconds)
        self.cache = {}
        self.access_count = {}
    
    def _get_cache_key(self, image_path: str, model_name: str, confidence: float) -> str:
        """Generate cache key for model prediction"""
        key_str = f"{image_path}_{model_name}_{confidence}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def cache_prediction(self, image_path: str, model_name: str, confidence: float, result: Dict) -> None:
        """
        Cache model prediction result
        
        Args:
            image_path: Path to image
            model_name: Name of model used
            confidence: Confidence threshold used
            result: Prediction result
        """
        key = self._get_cache_key(image_path, model_name, confidence)
        
        # Check if cache is full, remove least accessed item
        if len(self.cache) >= self.max_entries:
            # Find least accessed key
            min_key = min(self.access_count.keys(), key=lambda k: self.access_count[k])
            del self.cache[min_key]
            del self.access_count[min_key]
        
        self.cache[key] = {
            "result": result,
            "created_at": datetime.now(),
            "ttl": self.ttl
        }
        self.access_count[key] = 0
    
    def get_prediction(self, image_path: str, model_name: str, confidence: float) -> Optional[Dict]:
        """
        Get cached prediction result
        
        Args:
            image_path: Path to image
            model_name: Name of model
            confidence: Confidence threshold
        
        Returns:
            Cached result or None
        """
        key = self._get_cache_key(image_path, model_name, confidence)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if datetime.now() - entry["created_at"] > entry["ttl"]:
            del self.cache[key]
            del self.access_count[key]
            return None
        
        # Update access count
        self.access_count[key] += 1
        
        return entry["result"]
    
    def clear(self) -> None:
        """Clear all predictions"""
        self.cache.clear()
        self.access_count.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "total_entries": len(self.cache),
            "max_entries": self.max_entries,
            "ttl_seconds": int(self.ttl.total_seconds())
        }
