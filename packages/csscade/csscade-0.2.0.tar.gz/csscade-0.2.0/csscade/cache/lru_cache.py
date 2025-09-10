"""LRU cache implementation for CSS operations."""

from typing import Any, Dict, Optional, Tuple
from collections import OrderedDict
import hashlib
import json


class LRUCache:
    """Least Recently Used cache implementation."""
    
    def __init__(self, max_size: int = 128):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of items to cache
        """
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        
        self.misses += 1
        return None
    
    def put(self, key: str, value: Any) -> None:
        """
        Put item in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if key in self.cache:
            # Update and move to end
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            # Add new item
            self.cache[key] = value
            
            # Remove oldest if over capacity
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
    
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }


class CSSCache:
    """Specialized cache for CSS operations."""
    
    def __init__(self, max_size: int = 128):
        """
        Initialize CSS cache.
        
        Args:
            max_size: Maximum number of items to cache
        """
        self.parse_cache = LRUCache(max_size)
        self.merge_cache = LRUCache(max_size)
        self.class_name_cache = LRUCache(max_size)
    
    @staticmethod
    def _generate_key(*args: Any) -> str:
        """
        Generate cache key from arguments.
        
        Args:
            *args: Arguments to hash
            
        Returns:
            Cache key string
        """
        # Convert arguments to stable string representation
        key_parts = []
        for arg in args:
            if isinstance(arg, (dict, list)):
                key_parts.append(json.dumps(arg, sort_keys=True))
            else:
                key_parts.append(str(arg))
        
        key_str = '|'.join(key_parts)
        
        # Hash for shorter keys
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_parsed(self, css_string: str) -> Optional[Any]:
        """
        Get parsed CSS from cache.
        
        Args:
            css_string: CSS string to parse
            
        Returns:
            Cached parse result or None
        """
        key = self._generate_key('parse', css_string)
        return self.parse_cache.get(key)
    
    def cache_parsed(self, css_string: str, result: Any) -> None:
        """
        Cache parsed CSS.
        
        Args:
            css_string: Original CSS string
            result: Parse result to cache
        """
        key = self._generate_key('parse', css_string)
        self.parse_cache.put(key, result)
    
    def get_merge(
        self,
        source: Any,
        override: Any,
        mode: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get merge result from cache.
        
        Args:
            source: Source CSS
            override: Override CSS
            mode: Merge mode
            
        Returns:
            Cached merge result or None
        """
        key = self._generate_key('merge', source, override, mode)
        return self.merge_cache.get(key)
    
    def cache_merge(
        self,
        source: Any,
        override: Any,
        mode: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Cache merge result.
        
        Args:
            source: Source CSS
            override: Override CSS
            mode: Merge mode
            result: Merge result to cache
        """
        key = self._generate_key('merge', source, override, mode)
        self.merge_cache.put(key, result)
    
    def get_class_name(
        self,
        properties: Dict[str, str],
        strategy: str
    ) -> Optional[str]:
        """
        Get class name from cache.
        
        Args:
            properties: CSS properties
            strategy: Naming strategy
            
        Returns:
            Cached class name or None
        """
        key = self._generate_key('class', properties, strategy)
        return self.class_name_cache.get(key)
    
    def cache_class_name(
        self,
        properties: Dict[str, str],
        strategy: str,
        class_name: str
    ) -> None:
        """
        Cache class name.
        
        Args:
            properties: CSS properties
            strategy: Naming strategy
            class_name: Generated class name
        """
        key = self._generate_key('class', properties, strategy)
        self.class_name_cache.put(key, class_name)
    
    def clear_all(self) -> None:
        """Clear all caches."""
        self.parse_cache.clear()
        self.merge_cache.clear()
        self.class_name_cache.clear()
    
    def stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all caches.
        
        Returns:
            Dictionary with stats for each cache
        """
        return {
            'parse': self.parse_cache.stats(),
            'merge': self.merge_cache.stats(),
            'class_name': self.class_name_cache.stats()
        }