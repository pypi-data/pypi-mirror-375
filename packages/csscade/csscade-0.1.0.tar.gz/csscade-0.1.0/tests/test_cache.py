"""Tests for caching functionality."""

import pytest
from csscade.cache import LRUCache, CSSCache


class TestLRUCache:
    """Test cases for LRU cache."""
    
    def test_basic_operations(self):
        """Test basic cache operations."""
        cache = LRUCache(max_size=3)
        
        # Test put and get
        cache.put('key1', 'value1')
        assert cache.get('key1') == 'value1'
        assert cache.get('key2') is None
        
        # Test cache stats
        stats = cache.stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['size'] == 1
    
    def test_lru_eviction(self):
        """Test LRU eviction policy."""
        cache = LRUCache(max_size=3)
        
        # Fill cache
        cache.put('key1', 'value1')
        cache.put('key2', 'value2')
        cache.put('key3', 'value3')
        
        # Access key1 to make it recently used
        cache.get('key1')
        
        # Add new item, should evict key2 (least recently used)
        cache.put('key4', 'value4')
        
        assert cache.get('key1') == 'value1'  # Still present
        assert cache.get('key2') is None       # Evicted
        assert cache.get('key3') == 'value3'   # Still present
        assert cache.get('key4') == 'value4'   # New item
    
    def test_cache_update(self):
        """Test updating cached values."""
        cache = LRUCache(max_size=3)
        
        cache.put('key1', 'value1')
        cache.put('key1', 'updated')
        
        assert cache.get('key1') == 'updated'
        assert cache.stats()['size'] == 1
    
    def test_cache_clear(self):
        """Test clearing the cache."""
        cache = LRUCache(max_size=3)
        
        cache.put('key1', 'value1')
        cache.put('key2', 'value2')
        
        cache.clear()
        
        assert cache.get('key1') is None
        assert cache.stats()['size'] == 0
        assert cache.stats()['hits'] == 0
        assert cache.stats()['misses'] == 1
    
    def test_hit_rate_calculation(self):
        """Test hit rate calculation."""
        cache = LRUCache(max_size=3)
        
        cache.put('key1', 'value1')
        
        # 3 hits, 2 misses
        cache.get('key1')  # hit
        cache.get('key1')  # hit
        cache.get('key1')  # hit
        cache.get('key2')  # miss
        cache.get('key3')  # miss
        
        stats = cache.stats()
        assert stats['hits'] == 3
        assert stats['misses'] == 2
        assert stats['hit_rate'] == 0.6


class TestCSSCache:
    """Test cases for CSS cache."""
    
    def test_parse_cache(self):
        """Test caching parsed CSS."""
        cache = CSSCache()
        
        css_string = ".button { color: blue; }"
        parsed_result = {'selector': '.button', 'properties': {'color': 'blue'}}
        
        # Cache miss
        assert cache.get_parsed(css_string) is None
        
        # Cache the result
        cache.cache_parsed(css_string, parsed_result)
        
        # Cache hit
        assert cache.get_parsed(css_string) == parsed_result
    
    def test_merge_cache(self):
        """Test caching merge results."""
        cache = CSSCache()
        
        source = {'color': 'red'}
        override = {'color': 'blue'}
        mode = 'permanent'
        result = {'css': '.class { color: blue; }'}
        
        # Cache miss
        assert cache.get_merge(source, override, mode) is None
        
        # Cache the result
        cache.cache_merge(source, override, mode, result)
        
        # Cache hit
        assert cache.get_merge(source, override, mode) == result
        
        # Different mode should be cache miss
        assert cache.get_merge(source, override, 'component') is None
    
    def test_class_name_cache(self):
        """Test caching class names."""
        cache = CSSCache()
        
        properties = {'color': 'blue', 'padding': '10px'}
        strategy = 'hash'
        class_name = 'btn-abc123'
        
        # Cache miss
        assert cache.get_class_name(properties, strategy) is None
        
        # Cache the result
        cache.cache_class_name(properties, strategy, class_name)
        
        # Cache hit
        assert cache.get_class_name(properties, strategy) == class_name
        
        # Different strategy should be cache miss
        assert cache.get_class_name(properties, 'semantic') is None
    
    def test_key_generation(self):
        """Test cache key generation for complex inputs."""
        cache = CSSCache()
        
        # Test with different input types
        dict_input = {'color': 'blue', 'margin': '10px'}
        list_input = [('color', 'blue'), ('margin', '10px')]
        string_input = "color: blue; margin: 10px;"
        
        # Each should generate different keys
        key1 = cache._generate_key('test', dict_input)
        key2 = cache._generate_key('test', list_input)
        key3 = cache._generate_key('test', string_input)
        
        assert key1 != key2
        assert key2 != key3
        assert key1 != key3
        
        # Same input should generate same key
        key4 = cache._generate_key('test', dict_input)
        assert key1 == key4
    
    def test_clear_all_caches(self):
        """Test clearing all caches."""
        cache = CSSCache()
        
        # Add items to different caches
        cache.cache_parsed('.test {}', {'selector': '.test'})
        cache.cache_merge({'a': '1'}, {'b': '2'}, 'mode', {'result': 'test'})
        cache.cache_class_name({'color': 'red'}, 'hash', 'class-123')
        
        # Verify items are cached
        assert cache.parse_cache.stats()['size'] == 1
        assert cache.merge_cache.stats()['size'] == 1
        assert cache.class_name_cache.stats()['size'] == 1
        
        # Clear all
        cache.clear_all()
        
        # Verify all caches are empty
        assert cache.parse_cache.stats()['size'] == 0
        assert cache.merge_cache.stats()['size'] == 0
        assert cache.class_name_cache.stats()['size'] == 0
    
    def test_cache_stats(self):
        """Test getting statistics for all caches."""
        cache = CSSCache()
        
        # Generate some cache activity
        cache.cache_parsed('css1', 'result1')
        cache.get_parsed('css1')  # hit
        cache.get_parsed('css2')  # miss
        
        cache.cache_merge('s1', 'o1', 'm1', 'r1')
        cache.get_merge('s1', 'o1', 'm1')  # hit
        
        stats = cache.stats()
        
        assert 'parse' in stats
        assert 'merge' in stats
        assert 'class_name' in stats
        
        assert stats['parse']['hits'] == 1
        assert stats['parse']['misses'] == 1
        assert stats['merge']['hits'] == 1