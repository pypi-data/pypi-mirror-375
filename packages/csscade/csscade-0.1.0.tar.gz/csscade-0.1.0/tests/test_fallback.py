"""Tests for fallback handlers."""

import pytest
from csscade.handlers.fallback import FallbackHandler
from csscade.models import CSSProperty


class TestFallbackHandler:
    """Test cases for FallbackHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = FallbackHandler()
    
    def test_handle_pseudo_selector_inline(self):
        """Test handling pseudo-selector with inline fallback."""
        result = self.handler.handle_complex_selector(
            selector=".btn:hover",
            properties={"background": "blue", "color": "white"}
        )
        
        assert result['css'] is None
        assert result['inline'] == {"background": "blue", "color": "white"}
        assert len(result['warnings']) > 0
        assert ":hover" in result['warnings'][0]
    
    def test_handle_complex_selector_inline(self):
        """Test handling complex selector with inline fallback."""
        result = self.handler.handle_complex_selector(
            selector=".parent > .child",
            properties={"padding": "10px"}
        )
        
        assert result['css'] is None
        assert result['inline'] == {"padding": "10px"}
        assert len(result['warnings']) > 0
        assert "Complex selector" in result['warnings'][0]
    
    def test_handle_attribute_selector_inline(self):
        """Test handling attribute selector with inline fallback."""
        result = self.handler.handle_complex_selector(
            selector='[data-test="value"]',
            properties={"color": "red"}
        )
        
        assert result['css'] is None
        assert result['inline'] == {"color": "red"}
        assert len(result['warnings']) > 0
        assert "Attribute selector" in result['warnings'][0]
    
    def test_handle_media_query_preserve(self):
        """Test handling media query with preserve fallback."""
        result = self.handler.handle_complex_selector(
            selector="@media (min-width: 768px)",
            properties={"font-size": "16px"}
        )
        
        assert result['css'] is not None
        assert "@media (min-width: 768px)" in result['css']
        assert "font-size: 16px" in result['css']
        assert result['inline'] is None
        assert len(result['warnings']) > 0
    
    def test_handle_with_important_strategy(self):
        """Test handling with important strategy override."""
        result = self.handler.handle_complex_selector(
            selector=".btn:hover",
            properties={"color": "blue"},
            strategy="important"
        )
        
        assert result['css'] is None
        assert result['inline'] is None
        assert result['important'] == {"color": "blue"}
        assert len(result['warnings']) > 0
        assert "!important" in result['warnings'][-1]
    
    def test_handle_with_preserve_strategy(self):
        """Test handling with preserve strategy override."""
        result = self.handler.handle_complex_selector(
            selector=".parent > .child",
            properties={"margin": "5px"},
            strategy="preserve"
        )
        
        assert result['css'] is not None
        assert ".parent > .child" in result['css']
        assert "margin: 5px" in result['css']
        assert result['inline'] is None
    
    def test_handle_properties_with_important(self):
        """Test handling properties that already have !important."""
        result = self.handler.handle_complex_selector(
            selector=".btn:hover",
            properties={"color": "blue !important"},
            strategy="important"
        )
        
        assert result['important'] == {"color": "blue"}
        assert "!important" not in result['important']['color']
    
    def test_handle_property_list(self):
        """Test handling with CSSProperty list input."""
        properties = [
            CSSProperty("color", "blue"),
            CSSProperty("padding", "10px")
        ]
        
        result = self.handler.handle_complex_selector(
            selector=".btn:hover",
            properties=properties
        )
        
        assert result['inline'] == {"color": "blue", "padding": "10px"}
    
    def test_determine_best_fallback_media(self):
        """Test determining best fallback for media query."""
        strategy = self.handler.determine_best_fallback(
            "@media print"
        )
        assert strategy == "preserve"
    
    def test_determine_best_fallback_keyframes(self):
        """Test determining best fallback for keyframes."""
        strategy = self.handler.determine_best_fallback(
            "@keyframes slideIn"
        )
        assert strategy == "preserve"
    
    def test_determine_best_fallback_pseudo(self):
        """Test determining best fallback for pseudo-class."""
        strategy = self.handler.determine_best_fallback(
            ".btn:hover"
        )
        assert strategy == "inline"
    
    def test_determine_best_fallback_with_important(self):
        """Test determining best fallback when has !important."""
        strategy = self.handler.determine_best_fallback(
            ".btn:hover",
            has_important=True
        )
        assert strategy == "important"
    
    def test_determine_best_fallback_complex_component(self):
        """Test determining best fallback for complex selector in component context."""
        strategy = self.handler.determine_best_fallback(
            ".parent > .child",
            context="component"
        )
        assert strategy == "preserve"
    
    def test_generate_fallback_warning_pseudo(self):
        """Test generating warning for pseudo-selector."""
        warning = self.handler.generate_fallback_warning(
            ".btn:hover",
            "inline"
        )
        
        assert ":hover" in warning
        assert "inline" in warning
    
    def test_generate_fallback_warning_complex(self):
        """Test generating warning for complex selector."""
        warning = self.handler.generate_fallback_warning(
            ".parent > .child",
            "inline"
        )
        
        assert "Complex selector" in warning
        assert "inline" in warning
    
    def test_generate_fallback_warning_media(self):
        """Test generating warning for media query."""
        warning = self.handler.generate_fallback_warning(
            "@media print",
            "preserve"
        )
        
        assert "Media query" in warning
        assert "preserved" in warning
    
    def test_generate_fallback_warning_custom(self):
        """Test generating warning with custom reason."""
        warning = self.handler.generate_fallback_warning(
            ".btn",
            "inline",
            reason="Custom reason for fallback"
        )
        
        assert warning == "Custom reason for fallback"
    
    def test_can_use_class_override_simple(self):
        """Test checking if simple selectors can use class override."""
        assert self.handler.can_use_class_override(".btn") is True
        assert self.handler.can_use_class_override("#header") is True
        assert self.handler.can_use_class_override("div") is True
    
    def test_can_use_class_override_complex(self):
        """Test checking if complex selectors can use class override."""
        assert self.handler.can_use_class_override(".btn:hover") is False
        assert self.handler.can_use_class_override(".parent > .child") is False
        assert self.handler.can_use_class_override("[data-test]") is False