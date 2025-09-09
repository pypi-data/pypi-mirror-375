"""Tests for CSS parser functionality."""

import pytest
from csscade.parser.css_parser import CSSParser
from csscade.models import CSSProperty, CSSRule
from csscade.utils.exceptions import CSSParseError


class TestCSSParser:
    """Tests for CSSParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CSSParser()
    
    def test_parse_properties_string_simple(self):
        """Test parsing simple CSS properties string."""
        css_str = "color: red; padding: 10px;"
        properties = self.parser.parse_properties_string(css_str)
        
        assert len(properties) == 2
        assert properties[0].name == "color"
        assert properties[0].value == "red"
        assert properties[0].important is False
        assert properties[1].name == "padding"
        assert properties[1].value == "10px"
    
    def test_parse_properties_string_with_important(self):
        """Test parsing CSS properties with !important."""
        css_str = "color: blue !important; margin: 5px;"
        properties = self.parser.parse_properties_string(css_str)
        
        assert len(properties) == 2
        assert properties[0].name == "color"
        assert properties[0].value == "blue"
        assert properties[0].important is True
        assert properties[1].important is False
    
    def test_parse_properties_dict_simple(self):
        """Test parsing properties dictionary."""
        props_dict = {"color": "red", "padding": "10px"}
        properties = self.parser.parse_properties_dict(props_dict)
        
        assert len(properties) == 2
        color_prop = next(p for p in properties if p.name == "color")
        assert color_prop.value == "red"
        assert color_prop.important is False
    
    def test_parse_properties_dict_with_important(self):
        """Test parsing properties dictionary with !important."""
        props_dict = {"color": "blue !important", "margin": "5px"}
        properties = self.parser.parse_properties_dict(props_dict)
        
        color_prop = next(p for p in properties if p.name == "color")
        assert color_prop.value == "blue"
        assert color_prop.important is True
        
        margin_prop = next(p for p in properties if p.name == "margin")
        assert margin_prop.important is False
    
    def test_parse_rule_string_simple(self):
        """Test parsing simple CSS rule."""
        css_str = ".btn { color: red; }"
        rules = self.parser.parse_rule_string(css_str)
        
        assert len(rules) == 1
        assert rules[0].selector == ".btn"
        assert len(rules[0].properties) == 1
        assert rules[0].properties[0].name == "color"
        assert rules[0].properties[0].value == "red"
    
    def test_parse_rule_string_multiple_properties(self):
        """Test parsing CSS rule with multiple properties."""
        css_str = ".btn { color: red; padding: 10px; margin: 5px; }"
        rules = self.parser.parse_rule_string(css_str)
        
        assert len(rules) == 1
        assert len(rules[0].properties) == 3
        prop_names = [p.name for p in rules[0].properties]
        assert "color" in prop_names
        assert "padding" in prop_names
        assert "margin" in prop_names
    
    def test_parse_rule_string_multiple_rules(self):
        """Test parsing multiple CSS rules."""
        css_str = ".btn { color: red; } .card { padding: 10px; }"
        rules = self.parser.parse_rule_string(css_str)
        
        assert len(rules) == 2
        assert rules[0].selector == ".btn"
        assert rules[1].selector == ".card"
    
    def test_parse_auto_detect_properties(self):
        """Test auto-detecting and parsing properties string."""
        css_str = "color: red; padding: 10px"
        result = self.parser.parse(css_str)
        
        assert isinstance(result, list)
        assert all(isinstance(p, CSSProperty) for p in result)
        assert len(result) == 2
    
    def test_parse_auto_detect_rule(self):
        """Test auto-detecting and parsing rule string."""
        css_str = ".btn { color: red; }"
        result = self.parser.parse(css_str)
        
        assert isinstance(result, list)
        assert all(isinstance(r, CSSRule) for r in result)
        assert len(result) == 1
        assert result[0].selector == ".btn"
    
    def test_parse_dict_input(self):
        """Test parsing dictionary input."""
        props_dict = {"color": "red", "padding": "10px"}
        result = self.parser.parse(props_dict)
        
        assert isinstance(result, list)
        assert all(isinstance(p, CSSProperty) for p in result)
        assert len(result) == 2
    
    def test_properties_to_css_string(self):
        """Test converting properties to CSS string."""
        properties = [
            CSSProperty("color", "red", False),
            CSSProperty("padding", "10px", True)
        ]
        css_str = self.parser.properties_to_css_string(properties)
        
        assert css_str == "color: red; padding: 10px !important;"
    
    def test_properties_to_dict(self):
        """Test converting properties to dictionary."""
        properties = [
            CSSProperty("color", "red", False),
            CSSProperty("padding", "10px", True)
        ]
        props_dict = self.parser.properties_to_dict(properties)
        
        assert props_dict == {
            "color": "red",
            "padding": "10px !important"
        }
    
    def test_rule_to_css_string(self):
        """Test converting rule to CSS string."""
        rule = CSSRule(".btn", [
            CSSProperty("color", "red", False),
            CSSProperty("padding", "10px", False)
        ])
        css_str = self.parser.rule_to_css_string(rule)
        
        assert css_str == ".btn { color: red; padding: 10px; }"
    
    def test_validate_property_name_valid(self):
        """Test validating valid property names."""
        assert self.parser.validate_property_name("color") is True
        assert self.parser.validate_property_name("padding") is True
        assert self.parser.validate_property_name("margin-top") is True
    
    def test_validate_property_name_invalid(self):
        """Test validating invalid property names."""
        assert self.parser.validate_property_name("colr") is False
        assert self.parser.validate_property_name("not-a-property") is False
    
    def test_validate_css_string_valid(self):
        """Test validating valid CSS strings."""
        assert self.parser.validate_css_string("color: red;") is True
        assert self.parser.validate_css_string(".btn { color: red; }") is True
    
    def test_validate_css_string_invalid(self):
        """Test validating invalid CSS strings."""
        assert self.parser.validate_css_string("not valid css") is False
        assert self.parser.validate_css_string(".btn { }") is True  # Empty but valid
    
    def test_parse_complex_values(self):
        """Test parsing complex CSS values."""
        css_str = "box-shadow: 0 2px 4px rgba(0,0,0,0.1); transform: rotate(45deg);"
        properties = self.parser.parse_properties_string(css_str)
        
        assert len(properties) == 2
        shadow_prop = next(p for p in properties if p.name == "box-shadow")
        assert "rgba" in shadow_prop.value
        
        transform_prop = next(p for p in properties if p.name == "transform")
        assert "rotate" in transform_prop.value
    
    def test_parse_invalid_css_raises_error(self):
        """Test that invalid CSS raises appropriate error."""
        with pytest.raises(CSSParseError):
            self.parser.parse(123)  # Invalid type
    
    def test_empty_properties_string(self):
        """Test parsing empty properties string."""
        properties = self.parser.parse_properties_string("")
        assert properties == []
    
    def test_empty_properties_dict(self):
        """Test parsing empty properties dictionary."""
        properties = self.parser.parse_properties_dict({})
        assert properties == []