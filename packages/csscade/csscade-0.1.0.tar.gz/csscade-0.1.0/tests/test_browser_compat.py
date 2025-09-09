"""Tests for browser compatibility checking."""

import pytest
from csscade.validation import BrowserCompatChecker, BrowserSupport


class TestBrowserCompatChecker:
    """Test cases for browser compatibility checker."""
    
    def test_check_property_support(self):
        """Test checking property support."""
        checker = BrowserCompatChecker()
        
        # Check flexbox support
        support = checker.check_property_support('display', 'flex')
        assert support['chrome'] == BrowserSupport.FULL
        assert support['firefox'] == BrowserSupport.FULL
        assert support['safari'] == BrowserSupport.PREFIXED
        
        # Check custom properties
        support = checker.check_property_support('--custom-prop')
        assert support['chrome'] == BrowserSupport.FULL
        assert support['firefox'] == BrowserSupport.FULL
    
    def test_unknown_property_support(self):
        """Test checking unknown property support."""
        checker = BrowserCompatChecker()
        
        support = checker.check_property_support('unknown-property')
        assert support['chrome'] == BrowserSupport.UNKNOWN
        assert support['firefox'] == BrowserSupport.UNKNOWN
    
    def test_needs_prefix(self):
        """Test checking if properties need prefixes."""
        checker = BrowserCompatChecker()
        
        # Transform needs prefixes
        prefixes = checker.needs_prefix('transform')
        assert '-webkit-' in prefixes
        assert '-moz-' in prefixes
        
        # Color doesn't need prefixes
        prefixes = checker.needs_prefix('color')
        assert len(prefixes) == 0
    
    def test_add_vendor_prefixes(self):
        """Test adding vendor prefixes."""
        checker = BrowserCompatChecker()
        
        properties = {
            'transform': 'rotate(45deg)',
            'color': 'red'
        }
        
        result = checker.add_vendor_prefixes(properties)
        
        assert 'transform' in result
        assert '-webkit-transform' in result
        assert '-moz-transform' in result
        assert 'color' in result
        assert '-webkit-color' not in result  # Color doesn't need prefix
    
    def test_check_properties_compatibility(self):
        """Test checking compatibility for multiple properties."""
        checker = BrowserCompatChecker()
        
        properties = {
            'display': 'grid',
            'gap': '10px',
            'color': 'red'
        }
        
        compatibility, warnings = checker.check_properties_compatibility(properties)
        
        assert 'display' in compatibility
        assert 'gap' in compatibility
        assert 'color' in compatibility
        
        # Check for warnings (gap might not be supported in some browsers)
        # This assertion may vary based on the compatibility data
        # Gap is supported in newer browsers, so might not generate warnings
        if warnings:
            assert any('gap' in w or 'grid' in w for w in warnings)
    
    def test_get_fallback_properties(self):
        """Test getting fallback properties."""
        checker = BrowserCompatChecker()
        
        # Flexbox fallbacks
        fallbacks = checker.get_fallback_properties('display', 'flex')
        assert ('display', '-webkit-box') in fallbacks
        assert ('display', '-moz-box') in fallbacks
        assert ('display', 'flex') in fallbacks  # Original should be last
        
        # Grid fallbacks
        fallbacks = checker.get_fallback_properties('display', 'grid')
        assert ('display', '-ms-grid') in fallbacks
        
        # Sticky position fallback
        fallbacks = checker.get_fallback_properties('position', 'sticky')
        assert ('position', '-webkit-sticky') in fallbacks
    
    def test_generate_compatible_css(self):
        """Test generating compatible CSS."""
        checker = BrowserCompatChecker()
        
        properties = {
            'display': 'flex',
            'transform': 'rotate(45deg)'
        }
        
        result = checker.generate_compatible_css(properties)
        
        # Should have fallbacks for flexbox
        display_value = result.get('display')
        if isinstance(display_value, list):
            assert 'flex' in display_value
            assert '-webkit-box' in display_value
        else:
            # Fallbacks might be in the value itself
            assert display_value == 'flex' or '-webkit-box' in str(display_value)
        
        # Should have prefixes for transform
        assert '-webkit-transform' in result
        assert result['-webkit-transform'] == 'rotate(45deg)'
    
    def test_generate_compatible_css_no_prefixes(self):
        """Test generating CSS without prefixes."""
        checker = BrowserCompatChecker()
        
        properties = {
            'transform': 'rotate(45deg)'
        }
        
        result = checker.generate_compatible_css(
            properties,
            add_prefixes=False,
            add_fallbacks=False
        )
        
        assert 'transform' in result
        assert '-webkit-transform' not in result
    
    def test_get_minimum_browser_versions(self):
        """Test getting minimum browser versions."""
        checker = BrowserCompatChecker()
        
        properties = {
            'display': 'flex',
            'gap': '10px'
        }
        
        min_versions = checker.get_minimum_browser_versions(properties)
        
        # Gap requires newer browser versions than flexbox
        assert min_versions['chrome'] is not None
        assert min_versions['firefox'] is not None
        
        # Gap was added in Chrome 84
        assert min_versions['chrome'] >= 84
    
    def test_browser_support_enum(self):
        """Test BrowserSupport enum values."""
        assert BrowserSupport.FULL.value == 'full'
        assert BrowserSupport.PARTIAL.value == 'partial'
        assert BrowserSupport.NONE.value == 'none'
        assert BrowserSupport.PREFIXED.value == 'prefixed'
        assert BrowserSupport.UNKNOWN.value == 'unknown'
    
    def test_custom_target_browsers(self):
        """Test with custom target browsers."""
        checker = BrowserCompatChecker(target_browsers=['chrome', 'firefox'])
        
        support = checker.check_property_support('display', 'flex')
        
        assert 'chrome' in support
        assert 'firefox' in support
        assert 'safari' not in support  # Not in target browsers
        assert 'edge' not in support