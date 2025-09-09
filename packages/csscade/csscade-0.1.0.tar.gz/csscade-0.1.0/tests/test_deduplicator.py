"""Tests for style deduplication."""

import pytest
from csscade.optimization import StyleRegistry, PropertyOptimizer


class TestStyleRegistry:
    """Test cases for style registry."""
    
    def test_register_new_style(self):
        """Test registering a new style."""
        registry = StyleRegistry()
        
        properties = {'color': 'blue', 'padding': '10px'}
        class_name, is_new = registry.register(properties)
        
        assert is_new is True
        assert class_name.startswith('style-')
        assert registry.get_properties(class_name) == properties
    
    def test_register_duplicate_style(self):
        """Test registering duplicate styles."""
        registry = StyleRegistry()
        
        properties = {'color': 'blue', 'padding': '10px'}
        
        # First registration
        class1, is_new1 = registry.register(properties)
        assert is_new1 is True
        
        # Second registration with same properties
        class2, is_new2 = registry.register(properties)
        assert is_new2 is False
        assert class1 == class2  # Should return same class name
        
        # Check reference count
        assert registry.reference_count[class1] == 2
    
    def test_register_with_custom_name(self):
        """Test registering with custom class name."""
        registry = StyleRegistry()
        
        properties = {'color': 'red'}
        class_name, is_new = registry.register(properties, 'custom-class')
        
        assert class_name == 'custom-class'
        assert is_new is True
    
    def test_find_similar_styles(self):
        """Test finding similar styles."""
        registry = StyleRegistry()
        
        # Register some styles
        registry.register({'color': 'blue', 'padding': '10px'})
        registry.register({'color': 'blue', 'padding': '10px', 'margin': '5px'})
        registry.register({'color': 'red', 'border': '1px solid'})
        
        # Find similar to a new style
        test_props = {'color': 'blue', 'padding': '10px'}
        similar = registry.find_similar(test_props, threshold=0.8)
        
        assert len(similar) >= 1  # Should find at least one similar style
    
    def test_deduplicate_batch(self):
        """Test batch deduplication."""
        registry = StyleRegistry()
        
        styles = [
            {'color': 'blue'},
            {'color': 'red'},
            {'color': 'blue'},  # Duplicate
            {'color': 'green'},
            {'color': 'red'}    # Duplicate
        ]
        
        result = registry.deduplicate_batch(styles)
        
        assert len(result) == 5  # All styles processed
        
        # Check that duplicates have empty properties
        assert result[0][1] == {'color': 'blue'}  # New
        assert result[1][1] == {'color': 'red'}   # New
        assert result[2][1] == {}                 # Duplicate
        assert result[3][1] == {'color': 'green'} # New
        assert result[4][1] == {}                 # Duplicate
    
    def test_registry_stats(self):
        """Test registry statistics."""
        registry = StyleRegistry()
        
        # Register styles with duplicates
        registry.register({'color': 'blue'})
        registry.register({'color': 'blue'})
        registry.register({'color': 'red'})
        registry.register({'color': 'blue'})
        
        stats = registry.get_stats()
        
        assert stats['unique_styles'] == 2
        assert stats['total_references'] == 4
        assert stats['deduplication_ratio'] == 0.5
        assert stats['most_reused'][1] == 3  # blue style used 3 times
    
    def test_clear_registry(self):
        """Test clearing the registry."""
        registry = StyleRegistry()
        
        registry.register({'color': 'blue'})
        registry.register({'color': 'red'})
        
        registry.clear()
        
        assert len(registry.styles) == 0
        assert len(registry.class_to_properties) == 0
        assert len(registry.reference_count) == 0


class TestPropertyOptimizer:
    """Test cases for property optimizer."""
    
    def test_optimize_margin_shorthand(self):
        """Test optimizing margin to shorthand."""
        optimizer = PropertyOptimizer()
        
        # All four values same
        properties = {
            'margin-top': '10px',
            'margin-right': '10px',
            'margin-bottom': '10px',
            'margin-left': '10px'
        }
        
        result = optimizer.optimize_properties(properties)
        assert result == {'margin': '10px'}
        
        # Vertical and horizontal same
        properties = {
            'margin-top': '10px',
            'margin-right': '20px',
            'margin-bottom': '10px',
            'margin-left': '20px'
        }
        
        result = optimizer.optimize_properties(properties)
        assert result == {'margin': '10px 20px'}
    
    def test_optimize_padding_shorthand(self):
        """Test optimizing padding to shorthand."""
        optimizer = PropertyOptimizer()
        
        properties = {
            'padding-top': '5px',
            'padding-right': '10px',
            'padding-bottom': '15px',
            'padding-left': '20px'
        }
        
        result = optimizer.optimize_properties(properties)
        assert result == {'padding': '5px 10px 15px 20px'}
    
    def test_partial_shorthand_not_optimized(self):
        """Test that partial shorthand properties are not combined."""
        optimizer = PropertyOptimizer()
        
        # Only two margin properties
        properties = {
            'margin-top': '10px',
            'margin-left': '20px',
            'color': 'blue'
        }
        
        result = optimizer.optimize_properties(properties)
        
        assert 'margin' not in result
        assert result['margin-top'] == '10px'
        assert result['margin-left'] == '20px'
        assert result['color'] == 'blue'
    
    def test_mixed_properties(self):
        """Test optimizing mixed properties."""
        optimizer = PropertyOptimizer()
        
        properties = {
            'margin-top': '10px',
            'margin-right': '10px',
            'margin-bottom': '10px',
            'margin-left': '10px',
            'color': 'blue',
            'font-size': '14px'
        }
        
        result = optimizer.optimize_properties(properties)
        
        assert result == {
            'margin': '10px',
            'color': 'blue',
            'font-size': '14px'
        }
    
    def test_remove_defaults(self):
        """Test removing default values."""
        optimizer = PropertyOptimizer()
        
        properties = {
            'margin': '0',      # Default
            'padding': '10px',  # Not default
            'border': 'none',   # Default
            'color': 'blue'     # Not a default property
        }
        
        result = optimizer.remove_defaults(properties)
        
        assert 'margin' not in result
        assert 'border' not in result
        assert result['padding'] == '10px'
        assert result['color'] == 'blue'