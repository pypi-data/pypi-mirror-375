"""CSS syntax and property validation."""

import re
from typing import Dict, List, Optional, Tuple, Set
from csscade.utils.exceptions import CSSValidationError as ValidationError


class CSSValidator:
    """Validate CSS properties and values."""
    
    def __init__(self, strict: bool = False):
        """
        Initialize CSS validator.
        
        Args:
            strict: If True, raise errors; if False, return warnings
        """
        self.strict = strict
        self.warnings: List[str] = []
        
        # Valid CSS properties (common subset)
        self.valid_properties = {
            # Layout
            'display', 'position', 'top', 'right', 'bottom', 'left',
            'float', 'clear', 'z-index', 'overflow', 'overflow-x', 'overflow-y',
            'visibility', 'opacity',
            
            # Box model
            'width', 'height', 'min-width', 'min-height', 'max-width', 'max-height',
            'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
            'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
            'border', 'border-width', 'border-style', 'border-color',
            'border-top', 'border-right', 'border-bottom', 'border-left',
            'border-radius', 'border-top-left-radius', 'border-top-right-radius',
            'border-bottom-right-radius', 'border-bottom-left-radius',
            'box-sizing', 'box-shadow',
            
            # Typography
            'color', 'font', 'font-family', 'font-size', 'font-weight',
            'font-style', 'font-variant', 'line-height', 'letter-spacing',
            'word-spacing', 'text-align', 'text-decoration', 'text-transform',
            'text-indent', 'text-shadow', 'white-space', 'word-wrap', 'word-break',
            
            # Background
            'background', 'background-color', 'background-image', 'background-repeat',
            'background-position', 'background-size', 'background-attachment',
            'background-clip', 'background-origin',
            
            # Flexbox
            'flex', 'flex-grow', 'flex-shrink', 'flex-basis', 'flex-direction',
            'flex-wrap', 'flex-flow', 'justify-content', 'align-items',
            'align-content', 'align-self', 'order', 'gap', 'row-gap', 'column-gap',
            
            # Grid
            'grid', 'grid-template', 'grid-template-columns', 'grid-template-rows',
            'grid-template-areas', 'grid-column', 'grid-row', 'grid-area',
            'grid-gap', 'grid-column-gap', 'grid-row-gap',
            
            # Transform & Animation
            'transform', 'transform-origin', 'transition', 'transition-property',
            'transition-duration', 'transition-timing-function', 'transition-delay',
            'animation', 'animation-name', 'animation-duration', 'animation-timing-function',
            'animation-delay', 'animation-iteration-count', 'animation-direction',
            
            # Other
            'cursor', 'outline', 'outline-width', 'outline-style', 'outline-color',
            'list-style', 'list-style-type', 'list-style-position', 'list-style-image',
            'content', 'quotes', 'counter-reset', 'counter-increment',
            'resize', 'user-select', 'pointer-events'
        }
        
        # Color keywords
        self.color_keywords = {
            'transparent', 'currentcolor',  # lowercase for comparison
            'black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
            'gray', 'grey', 'darkgray', 'darkgrey', 'lightgray', 'lightgrey',
            'maroon', 'navy', 'olive', 'orange', 'purple', 'teal', 'silver',
            'aqua', 'fuchsia', 'lime', 'brown', 'pink', 'gold', 'indigo', 'violet'
        }
        
        # Common units
        self.length_units = {'px', 'em', 'rem', '%', 'vh', 'vw', 'vmin', 'vmax', 'ex', 'ch', 'cm', 'mm', 'in', 'pt', 'pc'}
        
    def validate_property_name(self, property_name: str) -> bool:
        """
        Validate CSS property name.
        
        Args:
            property_name: CSS property name
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValidationError: If strict mode and property invalid
        """
        # Check for vendor prefixes
        if property_name.startswith(('-webkit-', '-moz-', '-ms-', '-o-')):
            base_property = property_name.split('-', 2)[2] if '-' in property_name[1:] else property_name
            is_valid = True  # Allow vendor prefixes
        # Check for custom properties (CSS variables)
        elif property_name.startswith('--'):
            is_valid = True  # CSS variables are always valid
        else:
            is_valid = property_name in self.valid_properties
        
        if not is_valid:
            message = f"Unknown CSS property: '{property_name}'"
            if self.strict:
                raise ValidationError(message)
            else:
                self.warnings.append(message)
                
        return is_valid
    
    def validate_color_value(self, value: str) -> bool:
        """
        Validate CSS color value.
        
        Args:
            value: Color value
            
        Returns:
            True if valid color, False otherwise
        """
        value = value.strip().lower()
        
        # Check color keywords
        if value in self.color_keywords:
            return True
        
        # Check hex colors
        if re.match(r'^#[0-9a-f]{3}$|^#[0-9a-f]{6}$|^#[0-9a-f]{8}$', value):
            return True
        
        # Check rgb/rgba
        if re.match(r'^rgba?\([^)]+\)$', value):
            return True
        
        # Check hsl/hsla
        if re.match(r'^hsla?\([^)]+\)$', value):
            return True
        
        return False
    
    def validate_length_value(self, value: str) -> bool:
        """
        Validate CSS length value.
        
        Args:
            value: Length value
            
        Returns:
            True if valid length, False otherwise
        """
        value = value.strip()
        
        # Check for zero
        if value == '0':
            return True
        
        # Check for calc()
        if value.startswith('calc('):
            return True
        
        # Check for number with unit
        pattern = r'^-?\d+(\.\d+)?(' + '|'.join(self.length_units) + ')$'
        if re.match(pattern, value):
            return True
        
        # Check for keywords
        if value in {'auto', 'inherit', 'initial', 'unset'}:
            return True
        
        return False
    
    def validate_property_value(self, property_name: str, value: str) -> bool:
        """
        Validate CSS property value.
        
        Args:
            property_name: CSS property name
            value: Property value
            
        Returns:
            True if valid, False otherwise
        """
        if not value:
            return False
        
        value = value.strip()
        
        # Allow CSS-wide keywords
        if value in {'inherit', 'initial', 'unset', 'revert'}:
            return True
        
        # Check for CSS variables
        if 'var(' in value:
            return True  # Assume valid if using variables
        
        # Property-specific validation
        if 'color' in property_name or property_name in {'background', 'border', 'outline'}:
            # May contain color values
            if self.validate_color_value(value):
                return True
        
        if property_name in {'width', 'height', 'margin', 'padding', 'top', 'left', 'right', 'bottom'}:
            if self.validate_length_value(value):
                return True
        
        if property_name == 'display':
            valid_displays = {
                'none', 'block', 'inline', 'inline-block', 'flex', 'inline-flex',
                'grid', 'inline-grid', 'table', 'table-row', 'table-cell', 'list-item'
            }
            if value in valid_displays:
                return True
        
        if property_name == 'position':
            if value in {'static', 'relative', 'absolute', 'fixed', 'sticky'}:
                return True
        
        if property_name == 'font-weight':
            if value in {'normal', 'bold', 'lighter', 'bolder'} or value.isdigit():
                return True
        
        # If we can't validate specifically, check if it looks reasonable
        if re.match(r'^[\w\s\-\.,#%\(\)]+$', value):
            return True
        
        return False
    
    def validate_properties(self, properties: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate a dictionary of CSS properties.
        
        Args:
            properties: CSS properties dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        self.warnings = []
        
        for prop_name, prop_value in properties.items():
            # Validate property name
            if not self.validate_property_name(prop_name):
                errors.append(f"Invalid property name: '{prop_name}'")
            
            # Validate property value
            if not self.validate_property_value(prop_name, prop_value):
                message = f"Invalid value for '{prop_name}': '{prop_value}'"
                if self.strict:
                    errors.append(message)
                else:
                    self.warnings.append(message)
        
        is_valid = len(errors) == 0
        return is_valid, errors if errors else self.warnings
    
    def suggest_property_name(self, typo: str) -> Optional[str]:
        """
        Suggest correct property name for a typo.
        
        Args:
            typo: Potentially misspelled property name
            
        Returns:
            Suggested property name or None
        """
        typo_lower = typo.lower()
        
        # Check for exact match with different case
        for prop in self.valid_properties:
            if prop.lower() == typo_lower:
                return prop
        
        # Check for common typos
        typo_map = {
            'colr': 'color',
            'colour': 'color',
            'margn': 'margin',
            'paddin': 'padding',
            'wdth': 'width',
            'widht': 'width',  # Add this common typo
            'hight': 'height',
            'heigth': 'height',
            'backgroud': 'background',
            'bordr': 'border',
            'positon': 'position',
            'z-indx': 'z-index'
        }
        
        if typo_lower in typo_map:
            return typo_map[typo_lower]
        
        # Check Levenshtein distance for close matches
        min_distance = float('inf')
        best_match = None
        
        for prop in self.valid_properties:
            distance = self._levenshtein_distance(typo_lower, prop)
            if distance < min_distance and distance <= 2:  # Max 2 character difference
                min_distance = distance
                best_match = prop
        
        return best_match
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Edit distance
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def clear_warnings(self) -> None:
        """Clear accumulated warnings."""
        self.warnings = []