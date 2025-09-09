"""Tests for CSS conflict detection."""

import pytest
from csscade.resolvers.conflict_detector import ConflictDetector


class TestConflictDetector:
    """Tests for ConflictDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ConflictDetector()
    
    def test_same_property_conflicts(self):
        """Test that the same property always conflicts with itself."""
        assert self.detector.detect_conflict("color", "color") is True
        assert self.detector.detect_conflict("padding", "padding") is True
    
    def test_different_properties_no_conflict(self):
        """Test that different unrelated properties don't conflict."""
        assert self.detector.detect_conflict("color", "padding") is False
        assert self.detector.detect_conflict("margin", "background") is False
    
    def test_shorthand_longhand_conflict(self):
        """Test that shorthand and its longhand properties conflict."""
        # Margin shorthand vs longhand
        assert self.detector.detect_conflict("margin", "margin-top") is True
        assert self.detector.detect_conflict("margin-top", "margin") is True
        
        # Padding shorthand vs longhand
        assert self.detector.detect_conflict("padding", "padding-left") is True
        
        # Border shorthand vs longhand
        assert self.detector.detect_conflict("border", "border-width") is True
        assert self.detector.detect_conflict("border", "border-color") is True
        assert self.detector.detect_conflict("border", "border-top-width") is True
    
    def test_no_conflict_between_different_longhands(self):
        """Test that different longhands of same shorthand don't conflict."""
        assert self.detector.detect_conflict("margin-top", "margin-bottom") is False
        assert self.detector.detect_conflict("padding-left", "padding-right") is False
        assert self.detector.detect_conflict("border-top-width", "border-bottom-color") is False
    
    def test_find_conflicts_in_list(self):
        """Test finding all conflicts in a property list."""
        properties = ["color", "margin", "margin-top", "padding", "color"]
        conflicts = self.detector.find_conflicts(properties)
        
        # Should find: (color, color) and (margin, margin-top)
        assert len(conflicts) == 2
        assert ("color", "color") in conflicts
        assert ("margin", "margin-top") in conflicts
    
    def test_get_affected_properties_for_shorthand(self):
        """Test getting affected properties for a shorthand."""
        affected = self.detector.get_affected_properties("margin")
        
        assert "margin" in affected
        assert "margin-top" in affected
        assert "margin-right" in affected
        assert "margin-bottom" in affected
        assert "margin-left" in affected
        assert len(affected) == 5
    
    def test_get_affected_properties_for_longhand(self):
        """Test getting affected properties for a longhand."""
        affected = self.detector.get_affected_properties("margin-top")
        
        assert "margin-top" in affected
        assert "margin" in affected
    
    def test_get_affected_properties_for_simple(self):
        """Test getting affected properties for a simple property."""
        affected = self.detector.get_affected_properties("color")
        
        assert affected == {"color"}
    
    def test_is_shorthand(self):
        """Test identifying shorthand properties."""
        assert self.detector.is_shorthand("margin") is True
        assert self.detector.is_shorthand("padding") is True
        assert self.detector.is_shorthand("border") is True
        assert self.detector.is_shorthand("background") is True
        
        assert self.detector.is_shorthand("margin-top") is False
        assert self.detector.is_shorthand("color") is False
    
    def test_is_longhand(self):
        """Test identifying longhand properties."""
        assert self.detector.is_longhand("margin-top") is True
        assert self.detector.is_longhand("padding-left") is True
        assert self.detector.is_longhand("border-color") is True
        
        assert self.detector.is_longhand("margin") is False
        assert self.detector.is_longhand("color") is False
    
    def test_get_longhand_properties(self):
        """Test getting longhand properties for a shorthand."""
        longhands = self.detector.get_longhand_properties("margin")
        
        assert "margin-top" in longhands
        assert "margin-right" in longhands
        assert "margin-bottom" in longhands
        assert "margin-left" in longhands
        assert len(longhands) == 4
        
        # Non-shorthand should return empty set
        assert self.detector.get_longhand_properties("color") == set()
    
    def test_get_shorthand_properties(self):
        """Test getting shorthand properties for a longhand."""
        shorthands = self.detector.get_shorthand_properties("margin-top")
        
        assert "margin" in shorthands
        
        # Complex longhands
        border_shorthands = self.detector.get_shorthand_properties("border-top-width")
        assert "border" in border_shorthands
        assert "border-top" in border_shorthands
        assert "border-width" in border_shorthands
        
        # Non-longhand should return empty set
        assert self.detector.get_shorthand_properties("color") == set()
    
    def test_complex_border_relationships(self):
        """Test complex border shorthand relationships."""
        # border is a super-shorthand
        assert self.detector.detect_conflict("border", "border-top") is True
        assert self.detector.detect_conflict("border", "border-width") is True
        assert self.detector.detect_conflict("border", "border-top-width") is True
        
        # border-top is a shorthand for its sides
        assert self.detector.detect_conflict("border-top", "border-top-width") is True
        assert self.detector.detect_conflict("border-top", "border-top-color") is True
        
        # But border-top doesn't conflict with border-bottom
        assert self.detector.detect_conflict("border-top", "border-bottom") is False
    
    def test_flexbox_properties(self):
        """Test flexbox shorthand relationships."""
        assert self.detector.detect_conflict("flex", "flex-grow") is True
        assert self.detector.detect_conflict("flex", "flex-shrink") is True
        assert self.detector.detect_conflict("flex", "flex-basis") is True
        
        assert self.detector.detect_conflict("flex-grow", "flex-shrink") is False
    
    def test_grid_properties(self):
        """Test grid shorthand relationships."""
        assert self.detector.detect_conflict("grid", "grid-template-rows") is True
        assert self.detector.detect_conflict("grid-gap", "grid-row-gap") is True
        assert self.detector.detect_conflict("gap", "row-gap") is True
    
    def test_animation_properties(self):
        """Test animation shorthand relationships."""
        assert self.detector.detect_conflict("animation", "animation-name") is True
        assert self.detector.detect_conflict("animation", "animation-duration") is True
        assert self.detector.detect_conflict("transition", "transition-duration") is True
        
        # Animation and transition are separate
        assert self.detector.detect_conflict("animation", "transition") is False