"""Tests for shorthand/longhand resolver."""

import pytest
from csscade.handlers.shorthand import ShorthandResolver
from csscade.models import CSSProperty


class TestShorthandResolver:
    """Test cases for ShorthandResolver."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.resolver = ShorthandResolver()
    
    def test_expand_margin_single_value(self):
        """Test expanding margin with single value."""
        result = self.resolver.expand_shorthand('margin', '10px')
        
        assert len(result) == 4
        assert result[0] == CSSProperty('margin-top', '10px')
        assert result[1] == CSSProperty('margin-right', '10px')
        assert result[2] == CSSProperty('margin-bottom', '10px')
        assert result[3] == CSSProperty('margin-left', '10px')
    
    def test_expand_margin_two_values(self):
        """Test expanding margin with two values."""
        result = self.resolver.expand_shorthand('margin', '10px 20px')
        
        assert len(result) == 4
        assert result[0] == CSSProperty('margin-top', '10px')
        assert result[1] == CSSProperty('margin-right', '20px')
        assert result[2] == CSSProperty('margin-bottom', '10px')
        assert result[3] == CSSProperty('margin-left', '20px')
    
    def test_expand_margin_three_values(self):
        """Test expanding margin with three values."""
        result = self.resolver.expand_shorthand('margin', '10px 20px 30px')
        
        assert len(result) == 4
        assert result[0] == CSSProperty('margin-top', '10px')
        assert result[1] == CSSProperty('margin-right', '20px')
        assert result[2] == CSSProperty('margin-bottom', '30px')
        assert result[3] == CSSProperty('margin-left', '20px')
    
    def test_expand_margin_four_values(self):
        """Test expanding margin with four values."""
        result = self.resolver.expand_shorthand('margin', '10px 20px 30px 40px')
        
        assert len(result) == 4
        assert result[0] == CSSProperty('margin-top', '10px')
        assert result[1] == CSSProperty('margin-right', '20px')
        assert result[2] == CSSProperty('margin-bottom', '30px')
        assert result[3] == CSSProperty('margin-left', '40px')
    
    def test_expand_padding(self):
        """Test expanding padding shorthand."""
        result = self.resolver.expand_shorthand('padding', '5px 10px')
        
        assert len(result) == 4
        assert result[0] == CSSProperty('padding-top', '5px')
        assert result[1] == CSSProperty('padding-right', '10px')
        assert result[2] == CSSProperty('padding-bottom', '5px')
        assert result[3] == CSSProperty('padding-left', '10px')
    
    def test_expand_border_simple(self):
        """Test expanding simple border shorthand."""
        result = self.resolver.expand_shorthand('border', '1px solid red')
        
        # Should expand to width, style, and color for all sides
        prop_dict = {prop.name: prop.value for prop in result}
        
        assert 'border-top-width' in prop_dict
        assert prop_dict['border-top-width'] == '1px'
        assert 'border-top-style' in prop_dict
        assert prop_dict['border-top-style'] == 'solid'
        assert 'border-top-color' in prop_dict
        assert prop_dict['border-top-color'] == 'red'
    
    def test_expand_border_partial(self):
        """Test expanding partial border shorthand."""
        result = self.resolver.expand_shorthand('border', 'solid')
        
        # Should only expand style
        prop_dict = {prop.name: prop.value for prop in result}
        
        assert 'border-top-style' in prop_dict
        assert prop_dict['border-top-style'] == 'solid'
        assert 'border-top-width' not in prop_dict
        assert 'border-top-color' not in prop_dict
    
    def test_expand_border_radius_single(self):
        """Test expanding border-radius with single value."""
        result = self.resolver.expand_shorthand('border-radius', '5px')
        
        assert len(result) == 4
        assert result[0] == CSSProperty('border-top-left-radius', '5px')
        assert result[1] == CSSProperty('border-top-right-radius', '5px')
        assert result[2] == CSSProperty('border-bottom-right-radius', '5px')
        assert result[3] == CSSProperty('border-bottom-left-radius', '5px')
    
    def test_expand_border_radius_two_values(self):
        """Test expanding border-radius with two values."""
        result = self.resolver.expand_shorthand('border-radius', '5px 10px')
        
        assert len(result) == 4
        assert result[0] == CSSProperty('border-top-left-radius', '5px')
        assert result[1] == CSSProperty('border-top-right-radius', '10px')
        assert result[2] == CSSProperty('border-bottom-right-radius', '5px')
        assert result[3] == CSSProperty('border-bottom-left-radius', '10px')
    
    def test_expand_background_color(self):
        """Test expanding background with just color."""
        result = self.resolver.expand_shorthand('background', 'red')
        
        assert len(result) == 1
        assert result[0] == CSSProperty('background-color', 'red')
    
    def test_expand_background_none(self):
        """Test expanding background none."""
        result = self.resolver.expand_shorthand('background', 'none')
        
        assert len(result) == 2
        assert CSSProperty('background-color', 'none') in result
        assert CSSProperty('background-image', 'none') in result
    
    def test_expand_flex_single_number(self):
        """Test expanding flex with single number."""
        result = self.resolver.expand_shorthand('flex', '2')
        
        assert len(result) == 3
        assert result[0] == CSSProperty('flex-grow', '2')
        assert result[1] == CSSProperty('flex-shrink', '1')
        assert result[2] == CSSProperty('flex-basis', '0')
    
    def test_expand_flex_none(self):
        """Test expanding flex none."""
        result = self.resolver.expand_shorthand('flex', 'none')
        
        assert len(result) == 3
        assert result[0] == CSSProperty('flex-grow', '0')
        assert result[1] == CSSProperty('flex-shrink', '0')
        assert result[2] == CSSProperty('flex-basis', 'auto')
    
    def test_expand_flex_three_values(self):
        """Test expanding flex with three values."""
        result = self.resolver.expand_shorthand('flex', '2 1 30%')
        
        assert len(result) == 3
        assert result[0] == CSSProperty('flex-grow', '2')
        assert result[1] == CSSProperty('flex-shrink', '1')
        assert result[2] == CSSProperty('flex-basis', '30%')
    
    def test_expand_overflow_single(self):
        """Test expanding overflow with single value."""
        result = self.resolver.expand_shorthand('overflow', 'hidden')
        
        assert len(result) == 2
        assert result[0] == CSSProperty('overflow-x', 'hidden')
        assert result[1] == CSSProperty('overflow-y', 'hidden')
    
    def test_expand_overflow_two_values(self):
        """Test expanding overflow with two values."""
        result = self.resolver.expand_shorthand('overflow', 'hidden scroll')
        
        assert len(result) == 2
        assert result[0] == CSSProperty('overflow-x', 'hidden')
        assert result[1] == CSSProperty('overflow-y', 'scroll')
    
    def test_expand_gap(self):
        """Test expanding gap shorthand."""
        result = self.resolver.expand_shorthand('gap', '10px 20px')
        
        assert len(result) == 2
        assert result[0] == CSSProperty('row-gap', '10px')
        assert result[1] == CSSProperty('column-gap', '20px')
    
    def test_expand_place_content(self):
        """Test expanding place-content shorthand."""
        result = self.resolver.expand_shorthand('place-content', 'center')
        
        assert len(result) == 2
        assert result[0] == CSSProperty('align-content', 'center')
        assert result[1] == CSSProperty('justify-content', 'center')
    
    def test_expand_unknown_property(self):
        """Test expanding unknown property returns as-is."""
        result = self.resolver.expand_shorthand('unknown-property', 'value')
        
        assert len(result) == 1
        assert result[0] == CSSProperty('unknown-property', 'value')
    
    def test_merge_with_shorthand(self):
        """Test merging longhand with existing shorthand."""
        shorthand = CSSProperty('margin', '10px')
        longhand = CSSProperty('margin-top', '20px')
        
        result = self.resolver.merge_with_shorthand(shorthand, longhand)
        
        assert len(result) == 4
        # margin-top should be updated
        assert CSSProperty('margin-top', '20px') in result
        # Others should remain 10px
        assert CSSProperty('margin-right', '10px') in result
        assert CSSProperty('margin-bottom', '10px') in result
        assert CSSProperty('margin-left', '10px') in result
    
    def test_can_combine_to_shorthand(self):
        """Test checking if properties can combine to shorthand."""
        properties = [
            CSSProperty('margin-top', '10px'),
            CSSProperty('margin-right', '10px'),
            CSSProperty('margin-bottom', '10px'),
            CSSProperty('margin-left', '10px')
        ]
        
        result = self.resolver.can_combine_to_shorthand(properties)
        assert result == 'margin'
    
    def test_cannot_combine_partial(self):
        """Test that partial properties cannot combine."""
        properties = [
            CSSProperty('margin-top', '10px'),
            CSSProperty('margin-right', '10px')
        ]
        
        result = self.resolver.can_combine_to_shorthand(properties)
        assert result is None