"""Tests for value parser."""

import pytest
from csscade.parser.value_parser import ValueParser


class TestValueParser:
    """Test cases for ValueParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ValueParser()
    
    def test_parse_transform_single(self):
        """Test parsing single transform function."""
        result = self.parser.parse_transform('rotate(45deg)')
        
        assert len(result) == 1
        assert result[0] == ('rotate', '45deg')
    
    def test_parse_transform_multiple(self):
        """Test parsing multiple transform functions."""
        result = self.parser.parse_transform('rotate(45deg) scale(2) translateX(10px)')
        
        assert len(result) == 3
        assert result[0] == ('rotate', '45deg')
        assert result[1] == ('scale', '2')
        assert result[2] == ('translateX', '10px')
    
    def test_merge_transforms_replace(self):
        """Test merging transforms with replace mode."""
        base = 'rotate(45deg) scale(2)'
        override = 'rotate(90deg)'
        
        result = self.parser.merge_transforms(base, override, 'replace')
        
        # Should have rotate(90deg) and scale(2)
        assert 'rotate(90deg)' in result
        assert 'scale(2)' in result
        assert 'rotate(45deg)' not in result
    
    def test_merge_transforms_combine(self):
        """Test merging transforms with combine mode."""
        base = 'rotate(45deg)'
        override = 'scale(2)'
        
        result = self.parser.merge_transforms(base, override, 'combine')
        
        assert result == 'rotate(45deg) scale(2)'
    
    def test_parse_shadow_simple(self):
        """Test parsing simple shadow."""
        result = self.parser.parse_shadow('2px 4px 6px black')
        
        assert len(result) == 1
        shadow = result[0]
        assert shadow['x'] == '2px'
        assert shadow['y'] == '4px'
        assert shadow['blur'] == '6px'
        assert shadow['color'] == 'black'
        assert shadow['inset'] is False
    
    def test_parse_shadow_inset(self):
        """Test parsing inset shadow."""
        result = self.parser.parse_shadow('inset 0 1px 2px rgba(0,0,0,0.5)')
        
        assert len(result) == 1
        shadow = result[0]
        assert shadow['inset'] is True
        assert shadow['x'] == '0'
        assert shadow['y'] == '1px'
        assert shadow['blur'] == '2px'
    
    def test_parse_shadow_multiple(self):
        """Test parsing multiple shadows."""
        result = self.parser.parse_shadow('2px 2px red, 4px 4px blue')
        
        assert len(result) == 2
        assert result[0]['color'] == 'red'
        assert result[1]['color'] == 'blue'
    
    def test_merge_shadows_replace(self):
        """Test merging shadows with replace mode."""
        base = '2px 2px red'
        override = '4px 4px blue'
        
        result = self.parser.merge_shadows(base, override, 'replace')
        
        assert result == '4px 4px blue'
    
    def test_merge_shadows_append(self):
        """Test merging shadows with append mode."""
        base = '2px 2px red'
        override = '4px 4px blue'
        
        result = self.parser.merge_shadows(base, override, 'append')
        
        assert result == '2px 2px red, 4px 4px blue'
    
    def test_parse_gradient_linear(self):
        """Test parsing linear gradient."""
        result = self.parser.parse_gradient('linear-gradient(45deg, red, blue)')
        
        assert result['type'] == 'linear'
        assert result['angle'] == '45deg'
        assert 'red' in result['stops']
        assert 'blue' in result['stops']
    
    def test_parse_gradient_radial(self):
        """Test parsing radial gradient."""
        result = self.parser.parse_gradient('radial-gradient(circle at center, red, blue)')
        
        assert result['type'] == 'radial'
        assert result['shape'] == 'circle'
        assert result['position'] == 'center'
    
    def test_parse_color_hex(self):
        """Test parsing hex color."""
        result = self.parser.parse_color('#ff0000')
        
        assert result['type'] == 'hex'
        assert result['hex'] == 'ff0000'
        assert result['r'] == 255
        assert result['g'] == 0
        assert result['b'] == 0
    
    def test_parse_color_hex_short(self):
        """Test parsing short hex color."""
        result = self.parser.parse_color('#f00')
        
        assert result['type'] == 'hex'
        assert result['hex'] == 'f00'
        assert result['r'] == 255
        assert result['g'] == 0
        assert result['b'] == 0
    
    def test_parse_color_rgb(self):
        """Test parsing rgb color."""
        result = self.parser.parse_color('rgb(255, 128, 0)')
        
        assert result['type'] == 'rgb'
        assert result['r'] == 255
        assert result['g'] == 128
        assert result['b'] == 0
    
    def test_parse_color_rgba(self):
        """Test parsing rgba color."""
        result = self.parser.parse_color('rgba(255, 128, 0, 0.5)')
        
        assert result['type'] == 'rgba'
        assert result['r'] == 255
        assert result['g'] == 128
        assert result['b'] == 0
        assert result['a'] == 0.5
    
    def test_parse_color_named(self):
        """Test parsing named color."""
        result = self.parser.parse_color('red')
        
        assert result['type'] == 'named'
        assert result['value'] == 'red'
    
    def test_parse_calc(self):
        """Test parsing calc expression."""
        result = self.parser.parse_calc('calc(100% - 20px)')
        
        assert result['type'] == 'calc'
        assert result['expression'] == '100% - 20px'
        assert result['value'] == 'calc(100% - 20px)'
    
    def test_parse_url(self):
        """Test parsing URL."""
        result = self.parser.parse_url('url("image.png")')
        assert result == 'image.png'
        
        result = self.parser.parse_url("url('image.png')")
        assert result == 'image.png'
        
        result = self.parser.parse_url('url(image.png)')
        assert result == 'image.png'
    
    def test_is_complex_value(self):
        """Test checking if value is complex."""
        assert self.parser.is_complex_value('rotate(45deg)') is True
        assert self.parser.is_complex_value('2px 4px 6px 8px') is True
        assert self.parser.is_complex_value('red, blue') is True
        assert self.parser.is_complex_value('10px') is False
        assert self.parser.is_complex_value('red') is False
    
    def test_normalize_value(self):
        """Test normalizing values."""
        assert self.parser.normalize_value('  10px  ') == '10px'
        assert self.parser.normalize_value('0px') == '0'
        assert self.parser.normalize_value('0em') == '0'
        assert self.parser.normalize_value('#FF0000') == '#ff0000'
        assert self.parser.normalize_value('10px') == '10px'
    
    def test_split_list_value(self):
        """Test splitting list values."""
        result = self.parser.split_list_value('red, blue, green')
        assert result == ['red', 'blue', 'green']
        
        # Test with parentheses
        result = self.parser.split_list_value('rgb(255, 0, 0), blue')
        assert result == ['rgb(255, 0, 0)', 'blue']
        
        # Test with nested functions
        result = self.parser.split_list_value('linear-gradient(45deg, red, blue), url(image.png)')
        assert len(result) == 2
        assert 'linear-gradient' in result[0]
        assert 'url' in result[1]