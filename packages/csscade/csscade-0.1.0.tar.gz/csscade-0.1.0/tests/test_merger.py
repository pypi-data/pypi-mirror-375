"""Tests for the property merger."""

import pytest
from csscade.property_merger import PropertyMerger
from csscade.models import CSSProperty, CSSRule


class TestPropertyMerger:
    """Test cases for PropertyMerger class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.merger = PropertyMerger()
    
    def test_merge_no_conflicts(self):
        """Test merging properties with no conflicts."""
        source = [CSSProperty("color", "red")]
        override = [CSSProperty("padding", "10px")]
        
        result = self.merger.merge_properties(source, override)
        
        assert len(result) == 2
        prop_dict = {p.name: p.value for p in result}
        assert prop_dict["color"] == "red"
        assert prop_dict["padding"] == "10px"
    
    def test_merge_with_simple_conflict(self):
        """Test merging properties with direct conflicts."""
        source = [CSSProperty("color", "red")]
        override = [CSSProperty("color", "blue")]
        
        result = self.merger.merge_properties(source, override)
        
        assert len(result) == 1
        assert result[0].name == "color"
        assert result[0].value == "blue"
    
    def test_merge_multiple_properties_with_conflicts(self):
        """Test merging multiple properties with some conflicts."""
        source = [
            CSSProperty("color", "red"),
            CSSProperty("padding", "5px")
        ]
        override = [CSSProperty("color", "blue")]
        
        result = self.merger.merge_properties(source, override)
        
        assert len(result) == 2
        prop_dict = {p.name: p.value for p in result}
        assert prop_dict["color"] == "blue"
        assert prop_dict["padding"] == "5px"
    
    def test_merge_from_dict(self):
        """Test merging from dictionary inputs."""
        source = {"color": "red", "padding": "10px"}
        override = {"color": "blue"}
        
        result = self.merger.merge(source, override)
        
        assert len(result) == 2
        prop_dict = {p.name: p.value for p in result}
        assert prop_dict["color"] == "blue"
        assert prop_dict["padding"] == "10px"
    
    def test_merge_from_string(self):
        """Test merging from CSS string inputs."""
        source = "color: red; padding: 10px"
        override = "color: blue"
        
        result = self.merger.merge(source, override)
        
        assert len(result) == 2
        prop_dict = {p.name: p.value for p in result}
        assert prop_dict["color"] == "blue"
        assert prop_dict["padding"] == "10px"
    
    def test_merge_mixed_inputs(self):
        """Test merging with mixed input types."""
        source = {"color": "red", "padding": "10px"}
        override = "color: blue; margin: 5px"
        
        result = self.merger.merge(source, override)
        
        assert len(result) == 3
        prop_dict = {p.name: p.value for p in result}
        assert prop_dict["color"] == "blue"
        assert prop_dict["padding"] == "10px"
        assert prop_dict["margin"] == "5px"
    
    def test_merge_with_important(self):
        """Test merging properties with !important flags."""
        source = [CSSProperty("color", "red", important=True)]
        override = [CSSProperty("color", "blue", important=False)]
        
        result = self.merger.merge_properties(source, override)
        
        assert len(result) == 1
        assert result[0].value == "blue"
        assert result[0].important is False
    
    def test_merge_shorthand_override(self):
        """Test shorthand property overriding longhands."""
        source = [
            CSSProperty("margin-top", "10px"),
            CSSProperty("margin-right", "20px"),
            CSSProperty("margin-bottom", "30px"),
            CSSProperty("margin-left", "40px")
        ]
        override = [CSSProperty("margin", "5px")]
        
        result = self.merger.merge_properties(source, override)
        
        # Shorthand should replace all longhands
        assert len(result) == 1
        assert result[0].name == "margin"
        assert result[0].value == "5px"
    
    def test_merge_longhand_override_after_shorthand(self):
        """Test longhand property overriding after shorthand."""
        source = [CSSProperty("margin", "10px")]
        override = [CSSProperty("margin-top", "20px")]
        
        result = self.merger.merge_properties(source, override)
        
        # Both should exist as longhand doesn't fully replace shorthand
        prop_dict = {p.name: p.value for p in result}
        assert "margin-top" in prop_dict
        assert prop_dict["margin-top"] == "20px"
        # margin should be removed as it conflicts with margin-top
        assert "margin" not in prop_dict
    
    def test_merge_rules(self):
        """Test merging properties into a CSS rule."""
        rule = CSSRule(".btn", [
            CSSProperty("color", "red"),
            CSSProperty("padding", "10px")
        ])
        override = {"color": "blue", "margin": "5px"}
        
        result = self.merger.merge_rules(rule, override)
        
        assert result.selector == ".btn"
        assert len(result.properties) == 3
        prop_dict = {p.name: p.value for p in result.properties}
        assert prop_dict["color"] == "blue"
        assert prop_dict["padding"] == "10px"
        assert prop_dict["margin"] == "5px"
    
    def test_empty_source(self):
        """Test merging with empty source."""
        source = []
        override = [CSSProperty("color", "blue")]
        
        result = self.merger.merge_properties(source, override)
        
        assert len(result) == 1
        assert result[0].name == "color"
        assert result[0].value == "blue"
    
    def test_empty_override(self):
        """Test merging with empty override."""
        source = [CSSProperty("color", "red")]
        override = []
        
        result = self.merger.merge_properties(source, override)
        
        assert len(result) == 1
        assert result[0].name == "color"
        assert result[0].value == "red"
    
    def test_both_empty(self):
        """Test merging with both empty."""
        result = self.merger.merge_properties([], [])
        assert len(result) == 0