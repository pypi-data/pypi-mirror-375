"""Tests for the selector parser."""

import pytest
from csscade.handlers.selector_parser import SelectorParser, SelectorType


class TestSelectorParser:
    """Test cases for SelectorParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = SelectorParser()
    
    def test_parse_simple_class(self):
        """Test parsing simple class selector."""
        result = self.parser.parse(".btn")
        
        assert result['type'] == SelectorType.SIMPLE
        assert result['subtype'] == 'class'
        assert result['mergeable'] is True
        assert result['fallback'] is None
        assert '.btn' in result['components']
    
    def test_parse_simple_id(self):
        """Test parsing simple ID selector."""
        result = self.parser.parse("#header")
        
        assert result['type'] == SelectorType.SIMPLE
        assert result['subtype'] == 'id'
        assert result['mergeable'] is True
        assert result['fallback'] is None
        assert '#header' in result['components']
    
    def test_parse_simple_tag(self):
        """Test parsing simple tag selector."""
        result = self.parser.parse("div")
        
        assert result['type'] == SelectorType.SIMPLE
        assert result['subtype'] == 'tag'
        assert result['mergeable'] is True
        assert result['fallback'] is None
        assert 'div' in result['components']
    
    def test_parse_pseudo_hover(self):
        """Test parsing :hover pseudo-class."""
        result = self.parser.parse(".btn:hover")
        
        assert result['type'] == SelectorType.PSEUDO
        assert result['mergeable'] is False
        assert result['fallback'] == 'inline'
        assert result['base'] == '.btn'
        assert result['pseudo'] == ':hover'
    
    def test_parse_pseudo_nth_child(self):
        """Test parsing :nth-child pseudo-class."""
        result = self.parser.parse("li:nth-child(2)")
        
        assert result['type'] == SelectorType.PSEUDO
        assert result['mergeable'] is False
        assert result['fallback'] == 'inline'
        assert result['base'] == 'li'
        assert ':nth-child(2)' in result['pseudo']
    
    def test_parse_pseudo_element(self):
        """Test parsing ::before pseudo-element."""
        result = self.parser.parse(".btn::before")
        
        assert result['type'] == SelectorType.PSEUDO
        assert result['mergeable'] is False
        assert result['fallback'] == 'inline'
        assert result['base'] == '.btn'
        assert result['pseudo'] == '::before'
    
    def test_parse_attribute_selector(self):
        """Test parsing attribute selector."""
        result = self.parser.parse('[data-value="test"]')
        
        assert result['type'] == SelectorType.ATTRIBUTE
        assert result['mergeable'] is False
        assert result['fallback'] == 'inline'
    
    def test_parse_complex_descendant(self):
        """Test parsing descendant combinator."""
        result = self.parser.parse(".parent .child")
        
        assert result['type'] == SelectorType.COMPLEX
        assert result['mergeable'] is False
        assert result['fallback'] == 'inline'
        assert len(result['components']) > 1
    
    def test_parse_complex_child(self):
        """Test parsing child combinator."""
        result = self.parser.parse(".parent > .child")
        
        assert result['type'] == SelectorType.COMPLEX
        assert result['mergeable'] is False
        assert result['fallback'] == 'inline'
        assert len(result['components']) >= 3  # parent, >, child
    
    def test_parse_complex_adjacent(self):
        """Test parsing adjacent sibling combinator."""
        result = self.parser.parse(".item + .item")
        
        assert result['type'] == SelectorType.COMPLEX
        assert result['mergeable'] is False
        assert result['fallback'] == 'inline'
    
    def test_parse_complex_general_sibling(self):
        """Test parsing general sibling combinator."""
        result = self.parser.parse(".item ~ .item")
        
        assert result['type'] == SelectorType.COMPLEX
        assert result['mergeable'] is False
        assert result['fallback'] == 'inline'
    
    def test_parse_compound_multiple_classes(self):
        """Test parsing compound selector with multiple classes."""
        result = self.parser.parse(".btn.primary")
        
        assert result['type'] == SelectorType.COMPOUND
        assert result['mergeable'] is True
        assert result['fallback'] is None
    
    def test_parse_compound_tag_class(self):
        """Test parsing compound selector with tag and class."""
        result = self.parser.parse("button.btn")
        
        assert result['type'] == SelectorType.COMPOUND
        assert result['mergeable'] is True
    
    def test_parse_media_query(self):
        """Test parsing media query."""
        result = self.parser.parse("@media (min-width: 768px)")
        
        assert result['type'] == SelectorType.MEDIA
        assert result['mergeable'] is False
        assert result['fallback'] == 'preserve'
    
    def test_parse_keyframes(self):
        """Test parsing keyframes."""
        result = self.parser.parse("@keyframes fadeIn")
        
        assert result['type'] == SelectorType.KEYFRAMES
        assert result['mergeable'] is False
        assert result['fallback'] == 'preserve'
    
    def test_calculate_specificity_class(self):
        """Test specificity calculation for class."""
        result = self.parser.parse(".btn")
        specificity = result['specificity']
        
        assert specificity == (0, 1, 0)  # No IDs, 1 class, no elements
    
    def test_calculate_specificity_id(self):
        """Test specificity calculation for ID."""
        result = self.parser.parse("#header")
        specificity = result['specificity']
        
        assert specificity == (1, 0, 0)  # 1 ID, no classes, no elements
    
    def test_calculate_specificity_complex(self):
        """Test specificity calculation for complex selector."""
        result = self.parser.parse("#header .nav li:hover")
        specificity = result['specificity']
        
        assert specificity == (1, 2, 1)  # 1 ID, 2 classes/pseudo, 1 element
    
    def test_can_merge_simple(self):
        """Test can_merge for simple selectors."""
        assert self.parser.can_merge(".btn") is True
        assert self.parser.can_merge("#header") is True
        assert self.parser.can_merge("div") is True
    
    def test_can_merge_complex(self):
        """Test can_merge for complex selectors."""
        assert self.parser.can_merge(".btn:hover") is False
        assert self.parser.can_merge(".parent > .child") is False
        assert self.parser.can_merge("[data-test]") is False
    
    def test_get_fallback_strategy(self):
        """Test getting fallback strategy."""
        assert self.parser.get_fallback_strategy(".btn:hover") == 'inline'
        assert self.parser.get_fallback_strategy("@media print") == 'preserve'
        assert self.parser.get_fallback_strategy(".parent > .child") == 'inline'
    
    def test_unknown_selector(self):
        """Test parsing unknown/invalid selector."""
        result = self.parser.parse("@unknown rule")
        
        assert result['type'] == SelectorType.UNKNOWN
        assert result['mergeable'] is False
        assert result['fallback'] == 'inline'