"""Tests for media query handler."""

import pytest
from csscade.handlers.media import MediaQueryHandler
from csscade.models import CSSProperty, CSSRule


class TestMediaQueryHandler:
    """Test cases for MediaQueryHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = MediaQueryHandler()
    
    def test_parse_media_query_min_width(self):
        """Test parsing media query with min-width."""
        result = self.handler.parse_media_query("@media (min-width: 768px)")
        
        assert result['query'] == "(min-width: 768px)"
        assert 'min-width' in result['features']
        assert result['features']['min-width']['value'] == 768
        assert result['features']['min-width']['unit'] == 'px'
        assert 'min-width: 768px' in result['conditions']
    
    def test_parse_media_query_max_width(self):
        """Test parsing media query with max-width."""
        result = self.handler.parse_media_query("@media (max-width: 1200px)")
        
        assert 'max-width' in result['features']
        assert result['features']['max-width']['value'] == 1200
        assert result['features']['max-width']['unit'] == 'px'
    
    def test_parse_media_query_orientation(self):
        """Test parsing media query with orientation."""
        result = self.handler.parse_media_query("@media (orientation: landscape)")
        
        assert 'orientation' in result['features']
        assert result['features']['orientation'] == 'landscape'
        assert 'orientation: landscape' in result['conditions']
    
    def test_parse_media_query_with_type(self):
        """Test parsing media query with media type."""
        result = self.handler.parse_media_query("@media screen and (min-width: 768px)")
        
        assert result['media_type'] == 'screen'
        assert 'min-width' in result['features']
    
    def test_parse_media_query_complex(self):
        """Test parsing complex media query."""
        result = self.handler.parse_media_query(
            "@media screen and (min-width: 768px) and (max-width: 1024px)"
        )
        
        assert result['media_type'] == 'screen'
        assert 'min-width' in result['features']
        assert 'max-width' in result['features']
        assert len(result['conditions']) == 2
    
    def test_handle_media_query_preserve(self):
        """Test handling media query with preserve strategy."""
        result = self.handler.handle_media_query_merge(
            media_query="(min-width: 768px)",
            selector=".responsive",
            properties={"padding": "20px", "margin": "10px"},
            strategy="preserve"
        )
        
        assert result['css'] is not None
        assert "@media (min-width: 768px)" in result['css']
        assert ".responsive" in result['css']
        assert "padding: 20px" in result['css']
        assert "margin: 10px" in result['css']
        assert len(result['warnings']) > 0
    
    def test_handle_media_query_duplicate(self):
        """Test handling media query with duplicate strategy."""
        result = self.handler.handle_media_query_merge(
            media_query="(min-width: 768px)",
            selector=".btn",
            properties={"color": "blue"},
            strategy="duplicate"
        )
        
        assert result['css'] is not None
        # Should have both base and media query versions
        assert "@media (min-width: 768px)" in result['css']
        assert result['css'].count(".btn") == 2  # One base, one in media
        assert "duplicated" in result['warnings'][0]
    
    def test_handle_media_query_inline(self):
        """Test handling media query with inline strategy."""
        result = self.handler.handle_media_query_merge(
            media_query="(min-width: 768px)",
            selector=".responsive",
            properties={"font-size": "16px"},
            strategy="inline"
        )
        
        assert result.get('css') is None
        assert result['inline'] == {"font-size": "16px"}
        assert len(result['warnings']) > 0
        assert "inline styles" in result['warnings'][0]
    
    def test_handle_with_property_list(self):
        """Test handling with CSSProperty list."""
        properties = [
            CSSProperty("color", "blue"),
            CSSProperty("padding", "10px", important=True)
        ]
        
        result = self.handler.handle_media_query_merge(
            media_query="@media print",
            selector=".printable",
            properties=properties,
            strategy="preserve"
        )
        
        assert "@media print" in result['css']
        assert "color: blue" in result['css']
        assert "padding: 10px !important" in result['css']
    
    def test_extract_rules_from_media(self):
        """Test extracting rules from media queries in CSS."""
        css_text = """
        .normal { color: black; }
        
        @media (min-width: 768px) {
            .responsive { padding: 20px; }
            .container { width: 100%; }
        }
        
        @media print {
            .no-print { display: none; }
        }
        """
        
        results = self.handler.extract_rules_from_media(css_text)
        
        assert len(results) == 2
        
        # Check first media query
        media1, rules1 = results[0]
        assert "(min-width: 768px)" in media1
        assert len(rules1) >= 1  # At least one rule extracted
        assert any('.responsive' in rule.selector for rule in rules1)
        
        # Check second media query
        media2, rules2 = results[1]
        assert "print" in media2
        assert len(rules2) >= 1
        assert any('.no-print' in rule.selector for rule in rules2)
    
    def test_merge_media_queries(self):
        """Test merging multiple media queries."""
        queries = [
            ("@media (min-width: 768px)", [
                CSSRule(".btn", [CSSProperty("padding", "10px")])
            ]),
            ("@media (min-width: 768px)", [
                CSSRule(".card", [CSSProperty("margin", "5px")])
            ]),
            ("@media print", [
                CSSRule(".no-print", [CSSProperty("display", "none")])
            ])
        ]
        
        result = self.handler.merge_media_queries(queries)
        
        # Should group same media queries
        assert result.count("@media (min-width: 768px)") == 1
        assert result.count("@media print") == 1
        assert ".btn" in result
        assert ".card" in result
        assert ".no-print" in result
    
    def test_is_media_query(self):
        """Test checking if selector is media query."""
        assert self.handler.is_media_query("@media (min-width: 768px)") is True
        assert self.handler.is_media_query("@media print") is True
        assert self.handler.is_media_query(".btn") is False
        assert self.handler.is_media_query("@keyframes") is False
    
    def test_get_breakpoint_info_standard(self):
        """Test getting breakpoint info for standard sizes."""
        # Test medium breakpoint
        info = self.handler.get_breakpoint_info("@media (min-width: 768px)")
        assert info['type'] == 'md'
        assert info['min'] == 768
        assert info['max'] is None
        
        # Test large breakpoint
        info = self.handler.get_breakpoint_info("@media (min-width: 992px)")
        assert info['type'] == 'lg'
        assert info['min'] == 992
    
    def test_get_breakpoint_info_custom(self):
        """Test getting breakpoint info for custom sizes."""
        info = self.handler.get_breakpoint_info("@media (min-width: 850px)")
        assert info['type'] == 'custom'
        assert info['min'] == 850
    
    def test_get_breakpoint_info_range(self):
        """Test getting breakpoint info for range."""
        info = self.handler.get_breakpoint_info(
            "@media (min-width: 768px) and (max-width: 1024px)"
        )
        assert info['min'] == 768
        assert info['max'] == 1024
    
    def test_get_breakpoint_info_orientation(self):
        """Test getting breakpoint info with orientation."""
        info = self.handler.get_breakpoint_info(
            "@media (orientation: portrait)"
        )
        assert info['orientation'] == 'portrait'
        assert info['min'] is None
        assert info['max'] is None