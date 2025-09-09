"""Tests for CSS data models."""

import pytest
from csscade.models import CSSProperty, CSSRule


class TestCSSProperty:
    """Tests for CSSProperty class."""
    
    def test_property_creation(self):
        """Test creating a CSS property."""
        prop = CSSProperty("color", "red", False)
        assert prop.name == "color"
        assert prop.value == "red"
        assert prop.important is False
    
    def test_property_with_important(self):
        """Test creating a CSS property with !important."""
        prop = CSSProperty("color", "blue", True)
        assert prop.important is True
        assert str(prop) == "color: blue !important"
    
    def test_property_string_representation(self):
        """Test string representation of CSS property."""
        prop1 = CSSProperty("color", "red", False)
        assert str(prop1) == "color: red"
        
        prop2 = CSSProperty("padding", "10px", True)
        assert str(prop2) == "padding: 10px !important"
    
    def test_property_equality(self):
        """Test equality comparison between properties."""
        prop1 = CSSProperty("color", "red", False)
        prop2 = CSSProperty("color", "red", False)
        prop3 = CSSProperty("color", "blue", False)
        prop4 = CSSProperty("color", "red", True)
        
        assert prop1 == prop2
        assert prop1 != prop3
        assert prop1 != prop4
    
    def test_property_hashable(self):
        """Test that properties are hashable."""
        prop1 = CSSProperty("color", "red", False)
        prop2 = CSSProperty("color", "red", False)
        prop3 = CSSProperty("color", "blue", False)
        
        property_set = {prop1, prop2, prop3}
        assert len(property_set) == 2  # prop1 and prop2 are equal
    
    def test_property_to_dict(self):
        """Test converting property to dictionary."""
        prop = CSSProperty("margin", "10px", True)
        expected = {
            "name": "margin",
            "value": "10px",
            "important": True
        }
        assert prop.to_dict() == expected
    
    def test_property_from_dict(self):
        """Test creating property from dictionary."""
        data = {
            "name": "padding",
            "value": "20px",
            "important": False
        }
        prop = CSSProperty.from_dict(data)
        assert prop.name == "padding"
        assert prop.value == "20px"
        assert prop.important is False


class TestCSSRule:
    """Tests for CSSRule class."""
    
    def test_rule_creation(self):
        """Test creating a CSS rule."""
        rule = CSSRule(".btn", [])
        assert rule.selector == ".btn"
        assert rule.properties == []
    
    def test_rule_with_properties(self):
        """Test creating a CSS rule with properties."""
        props = [
            CSSProperty("color", "red", False),
            CSSProperty("padding", "10px", False)
        ]
        rule = CSSRule(".btn", props)
        assert len(rule.properties) == 2
        assert rule.properties[0].name == "color"
    
    def test_rule_string_representation(self):
        """Test string representation of CSS rule."""
        rule1 = CSSRule(".btn", [])
        assert str(rule1) == ".btn {}"
        
        rule2 = CSSRule(".btn", [
            CSSProperty("color", "red", False),
            CSSProperty("padding", "10px", False)
        ])
        assert str(rule2) == ".btn { color: red; padding: 10px; }"
    
    def test_add_property(self):
        """Test adding a property to a rule."""
        rule = CSSRule(".btn", [])
        prop = CSSProperty("color", "blue", False)
        
        rule.add_property(prop)
        assert len(rule.properties) == 1
        assert rule.properties[0] == prop
    
    def test_remove_property(self):
        """Test removing a property from a rule."""
        rule = CSSRule(".btn", [
            CSSProperty("color", "red", False),
            CSSProperty("padding", "10px", False)
        ])
        
        removed = rule.remove_property("color")
        assert removed is True
        assert len(rule.properties) == 1
        assert rule.properties[0].name == "padding"
        
        removed = rule.remove_property("margin")
        assert removed is False
        assert len(rule.properties) == 1
    
    def test_get_property(self):
        """Test getting a property by name."""
        rule = CSSRule(".btn", [
            CSSProperty("color", "red", False),
            CSSProperty("padding", "10px", False)
        ])
        
        prop = rule.get_property("color")
        assert prop is not None
        assert prop.value == "red"
        
        prop = rule.get_property("margin")
        assert prop is None
    
    def test_has_property(self):
        """Test checking if rule has a property."""
        rule = CSSRule(".btn", [
            CSSProperty("color", "red", False)
        ])
        
        assert rule.has_property("color") is True
        assert rule.has_property("padding") is False
    
    def test_rule_to_dict(self):
        """Test converting rule to dictionary."""
        rule = CSSRule(".btn", [
            CSSProperty("color", "red", False),
            CSSProperty("padding", "10px", True)
        ])
        
        expected = {
            "selector": ".btn",
            "properties": [
                {"name": "color", "value": "red", "important": False},
                {"name": "padding", "value": "10px", "important": True}
            ]
        }
        assert rule.to_dict() == expected
    
    def test_rule_from_dict(self):
        """Test creating rule from dictionary."""
        data = {
            "selector": ".card",
            "properties": [
                {"name": "background", "value": "white", "important": False},
                {"name": "border", "value": "1px solid black", "important": True}
            ]
        }
        
        rule = CSSRule.from_dict(data)
        assert rule.selector == ".card"
        assert len(rule.properties) == 2
        assert rule.properties[0].name == "background"
        assert rule.properties[1].important is True
    
    def test_get_properties_dict(self):
        """Test getting properties as simple dictionary."""
        rule = CSSRule(".btn", [
            CSSProperty("color", "red", False),
            CSSProperty("padding", "10px", True)
        ])
        
        props_dict = rule.get_properties_dict()
        expected = {
            "color": "red",
            "padding": "10px"
        }
        assert props_dict == expected
    
    def test_merge_properties(self):
        """Test merging properties into a rule."""
        rule = CSSRule(".btn", [
            CSSProperty("color", "red", False),
            CSSProperty("padding", "10px", False)
        ])
        
        new_props = [
            CSSProperty("color", "blue", False),  # Override existing
            CSSProperty("margin", "5px", False)   # Add new
        ]
        
        rule.merge_properties(new_props)
        
        assert len(rule.properties) == 3
        color_prop = rule.get_property("color")
        assert color_prop.value == "blue"
        assert rule.has_property("margin") is True
        assert rule.has_property("padding") is True