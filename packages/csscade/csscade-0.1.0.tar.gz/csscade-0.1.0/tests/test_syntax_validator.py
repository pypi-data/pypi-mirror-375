"""Tests for CSS syntax validation."""

import pytest
from csscade.validation import CSSValidator
from csscade.utils.exceptions import CSSValidationError as ValidationError


class TestCSSValidator:
    """Test cases for CSS validator."""
    
    def test_validate_valid_property_names(self):
        """Test validating valid property names."""
        validator = CSSValidator()
        
        valid_properties = [
            'color', 'background-color', 'margin', 'padding-top',
            'display', 'position', 'z-index', 'transform'
        ]
        
        for prop in valid_properties:
            assert validator.validate_property_name(prop) is True
    
    def test_validate_invalid_property_names(self):
        """Test validating invalid property names."""
        validator = CSSValidator(strict=False)
        
        invalid_properties = ['colr', 'margn', 'paddin', 'unknown-prop']
        
        for prop in invalid_properties:
            assert validator.validate_property_name(prop) is False
            assert len(validator.warnings) > 0
    
    def test_validate_vendor_prefixes(self):
        """Test validating vendor-prefixed properties."""
        validator = CSSValidator()
        
        prefixed_properties = [
            '-webkit-transform', '-moz-box-shadow',
            '-ms-flex', '-o-transition'
        ]
        
        for prop in prefixed_properties:
            assert validator.validate_property_name(prop) is True
    
    def test_validate_custom_properties(self):
        """Test validating CSS custom properties (variables)."""
        validator = CSSValidator()
        
        custom_properties = [
            '--primary-color', '--main-spacing',
            '--border-width-large'
        ]
        
        for prop in custom_properties:
            assert validator.validate_property_name(prop) is True
    
    def test_strict_mode_raises_error(self):
        """Test that strict mode raises ValidationError."""
        validator = CSSValidator(strict=True)
        
        with pytest.raises(ValidationError) as exc:
            validator.validate_property_name('invalid-property')
        
        assert 'Unknown CSS property' in str(exc.value)
    
    def test_validate_color_values(self):
        """Test validating color values."""
        validator = CSSValidator()
        
        valid_colors = [
            'red', 'blue', '#fff', '#ffffff', '#00000080',
            'rgb(255, 0, 0)', 'rgba(255, 0, 0, 0.5)',
            'hsl(120, 100%, 50%)', 'hsla(120, 100%, 50%, 0.5)',
            'transparent', 'currentColor'
        ]
        
        for color in valid_colors:
            assert validator.validate_color_value(color) is True
        
        invalid_colors = ['notacolor', '#gg0000']
        
        for color in invalid_colors:
            assert validator.validate_color_value(color) is False
    
    def test_validate_length_values(self):
        """Test validating length values."""
        validator = CSSValidator()
        
        valid_lengths = [
            '0', '10px', '2em', '50%', '100vh', '5rem',
            '-10px', '0.5em', 'auto', 'inherit',
            'calc(100% - 20px)'
        ]
        
        for length in valid_lengths:
            assert validator.validate_length_value(length) is True
        
        invalid_lengths = ['10', 'px', '10 px']
        
        for length in invalid_lengths:
            assert validator.validate_length_value(length) is False
    
    def test_validate_property_values(self):
        """Test validating property values."""
        validator = CSSValidator()
        
        # Test color properties
        assert validator.validate_property_value('color', 'red') is True
        assert validator.validate_property_value('background-color', '#fff') is True
        
        # Test length properties
        assert validator.validate_property_value('width', '100px') is True
        assert validator.validate_property_value('margin', '10px') is True
        
        # Test display values
        assert validator.validate_property_value('display', 'block') is True
        assert validator.validate_property_value('display', 'flex') is True
        
        # Test position values
        assert validator.validate_property_value('position', 'absolute') is True
        assert validator.validate_property_value('position', 'sticky') is True
        
        # Test CSS-wide keywords
        assert validator.validate_property_value('color', 'inherit') is True
        assert validator.validate_property_value('width', 'initial') is True
    
    def test_validate_properties_dict(self):
        """Test validating a dictionary of properties."""
        validator = CSSValidator()
        
        valid_props = {
            'color': 'blue',
            'margin': '10px',
            'display': 'flex'
        }
        
        is_valid, errors = validator.validate_properties(valid_props)
        assert is_valid is True
        assert len(errors) == 0
        
        invalid_props = {
            'colr': 'red',  # Typo
            'margin': '10px',
            'display': 'flexbox'  # Invalid value
        }
        
        is_valid, errors = validator.validate_properties(invalid_props)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_suggest_property_name(self):
        """Test property name suggestions for typos."""
        validator = CSSValidator()
        
        # Test common typos
        assert validator.suggest_property_name('colr') == 'color'
        assert validator.suggest_property_name('margn') == 'margin'
        assert validator.suggest_property_name('paddin') == 'padding'
        assert validator.suggest_property_name('backgroud') == 'background'
        
        # Test case insensitive
        assert validator.suggest_property_name('COLOR') == 'color'
        
        # Test close matches
        assert validator.suggest_property_name('widht') == 'width'
        assert validator.suggest_property_name('heigth') == 'height'
    
    def test_levenshtein_distance(self):
        """Test Levenshtein distance calculation."""
        validator = CSSValidator()
        
        assert validator._levenshtein_distance('color', 'color') == 0
        assert validator._levenshtein_distance('color', 'colr') == 1
        assert validator._levenshtein_distance('margin', 'margn') == 1
        assert validator._levenshtein_distance('abc', 'xyz') == 3
    
    def test_clear_warnings(self):
        """Test clearing warnings."""
        validator = CSSValidator(strict=False)
        
        validator.validate_property_name('invalid')
        assert len(validator.warnings) > 0
        
        validator.clear_warnings()
        assert len(validator.warnings) == 0