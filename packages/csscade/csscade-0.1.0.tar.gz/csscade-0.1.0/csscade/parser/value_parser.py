"""Parser for complex CSS values."""

import re
from typing import List, Dict, Tuple, Optional, Any, Union


class ValueParser:
    """Parse and manipulate complex CSS values."""
    
    def __init__(self):
        """Initialize the value parser."""
        # Patterns for different value types
        self.patterns = {
            'transform_function': re.compile(r'(\w+)\(([^)]+)\)'),
            'color_rgb': re.compile(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)'),
            'color_rgba': re.compile(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)'),
            'color_hex': re.compile(r'^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$'),
            'gradient': re.compile(r'(linear|radial|conic)-gradient\([^)]+\)'),
            'url': re.compile(r'url\(["\']?([^"\']+)["\']?\)'),
            'calc': re.compile(r'calc\([^)]+\)'),
            'var': re.compile(r'var\(--[\w-]+(?:,\s*[^)]+)?\)'),
            'shadow': re.compile(r'(?:inset\s+)?(?:-?\d+(?:\.\d+)?(?:px|em|rem|%)\s*){2,4}(?:\s+[\w#]+)?'),
        }
    
    def parse_transform(self, value: str) -> List[Tuple[str, str]]:
        """
        Parse transform value into individual functions.
        
        Args:
            value: Transform CSS value
            
        Returns:
            List of (function_name, arguments) tuples
        """
        transforms = []
        matches = self.patterns['transform_function'].findall(value)
        
        for func, args in matches:
            transforms.append((func, args.strip()))
        
        return transforms
    
    def merge_transforms(
        self,
        base: str,
        override: str,
        merge_mode: str = 'replace'
    ) -> str:
        """
        Merge two transform values.
        
        Args:
            base: Base transform value
            override: Override transform value
            merge_mode: 'replace' or 'combine'
            
        Returns:
            Merged transform value
        """
        if merge_mode == 'replace':
            # Parse both transforms
            base_transforms = dict(self.parse_transform(base))
            override_transforms = dict(self.parse_transform(override))
            
            # Merge dictionaries
            merged = {**base_transforms, **override_transforms}
            
            # Reconstruct transform string
            return ' '.join(f'{func}({args})' for func, args in merged.items())
        else:
            # Combine mode - append transforms
            return f'{base} {override}'.strip()
    
    def parse_shadow(self, value: str) -> List[Dict[str, Any]]:
        """
        Parse box-shadow or text-shadow value.
        
        Args:
            value: Shadow CSS value
            
        Returns:
            List of shadow dictionaries
        """
        shadows = []
        
        # Split by comma (multiple shadows) but respect parentheses
        shadow_parts = self.split_list_value(value, ',')
        
        for shadow in shadow_parts:
            shadow = shadow.strip()
            parsed = {
                'inset': False,
                'x': '0',
                'y': '0',
                'blur': '0',
                'spread': None,
                'color': None
            }
            
            # Check for inset
            if shadow.startswith('inset'):
                parsed['inset'] = True
                shadow = shadow[5:].strip()
            
            # Extract values
            parts = shadow.split()
            numbers = []
            color = None
            
            for part in parts:
                if any(unit in part for unit in ['px', 'em', 'rem', '%']) or \
                   part.lstrip('-').isdigit():
                    numbers.append(part)
                else:
                    color = part
            
            # Assign numbers to properties
            if len(numbers) >= 2:
                parsed['x'] = numbers[0]
                parsed['y'] = numbers[1]
            if len(numbers) >= 3:
                parsed['blur'] = numbers[2]
            if len(numbers) >= 4:
                parsed['spread'] = numbers[3]
            
            if color:
                parsed['color'] = color
            
            shadows.append(parsed)
        
        return shadows
    
    def merge_shadows(
        self,
        base: str,
        override: str,
        merge_mode: str = 'replace'
    ) -> str:
        """
        Merge two shadow values.
        
        Args:
            base: Base shadow value
            override: Override shadow value
            merge_mode: 'replace', 'append', or 'merge'
            
        Returns:
            Merged shadow value
        """
        if merge_mode == 'replace':
            return override
        elif merge_mode == 'append':
            return f'{base}, {override}'
        else:
            # Merge mode - parse and combine intelligently
            base_shadows = self.parse_shadow(base)
            override_shadows = self.parse_shadow(override)
            
            # For simplicity, replace matching indices
            result_shadows = base_shadows.copy()
            for i, shadow in enumerate(override_shadows):
                if i < len(result_shadows):
                    result_shadows[i] = shadow
                else:
                    result_shadows.append(shadow)
            
            # Reconstruct shadow string
            shadow_strs = []
            for shadow in result_shadows:
                parts = []
                if shadow['inset']:
                    parts.append('inset')
                parts.append(shadow['x'])
                parts.append(shadow['y'])
                if shadow['blur'] != '0':
                    parts.append(shadow['blur'])
                if shadow['spread']:
                    parts.append(shadow['spread'])
                if shadow['color']:
                    parts.append(shadow['color'])
                shadow_strs.append(' '.join(parts))
            
            return ', '.join(shadow_strs)
    
    def parse_gradient(self, value: str) -> Dict[str, Any]:
        """
        Parse gradient value.
        
        Args:
            value: Gradient CSS value
            
        Returns:
            Dictionary with gradient information
        """
        result = {
            'type': None,
            'angle': None,
            'position': None,
            'stops': []
        }
        
        # Detect gradient type
        if value.startswith('linear-gradient'):
            result['type'] = 'linear'
            # Find the opening and closing parentheses
            start = value.index('(') + 1
            end = value.rindex(')')
            content = value[start:end].strip()
            
            # Split content respecting parentheses
            parts = self.split_list_value(content, ',')
            
            # Check if first part is angle or direction
            if parts and ('deg' in parts[0] or parts[0].startswith('to ')):
                result['angle'] = parts[0].strip()
                parts = parts[1:]
            
            result['stops'] = [p.strip() for p in parts]
            return result
            
        elif value.startswith('radial-gradient'):
            result['type'] = 'radial'
            result['shape'] = None  # Initialize shape
            # Find the opening and closing parentheses
            start = value.index('(') + 1
            end = value.rindex(')')
            content = value[start:end].strip()
            
            # Split content respecting parentheses
            parts = self.split_list_value(content, ',')
            
            # Check for shape/position in first part
            if parts and ('circle' in parts[0] or 'ellipse' in parts[0] or 'at ' in parts[0]):
                first = parts[0].strip()
                if 'circle' in first:
                    result['shape'] = 'circle'
                elif 'ellipse' in first:
                    result['shape'] = 'ellipse'
                    
                at_idx = first.find('at ')
                if at_idx != -1:
                    # Extract just the position
                    position_part = first[at_idx + 3:].strip()
                    result['position'] = position_part
                    
                parts = parts[1:]
            
            result['stops'] = [p.strip() for p in parts]
            return result
        else:
            return result
    
    def parse_color(self, value: str) -> Dict[str, Any]:
        """
        Parse color value.
        
        Args:
            value: Color CSS value
            
        Returns:
            Dictionary with color information
        """
        result = {
            'type': 'unknown',
            'value': value,
            'r': None,
            'g': None,
            'b': None,
            'a': 1.0,
            'hex': None
        }
        
        # Check for hex color
        hex_match = self.patterns['color_hex'].match(value)
        if hex_match:
            result['type'] = 'hex'
            result['hex'] = hex_match.group(1)
            # Convert to RGB
            hex_val = hex_match.group(1)
            if len(hex_val) == 3:
                hex_val = ''.join([c*2 for c in hex_val])
            result['r'] = int(hex_val[0:2], 16)
            result['g'] = int(hex_val[2:4], 16)
            result['b'] = int(hex_val[4:6], 16)
            return result
        
        # Check for rgb()
        rgb_match = self.patterns['color_rgb'].match(value)
        if rgb_match:
            result['type'] = 'rgb'
            result['r'] = int(rgb_match.group(1))
            result['g'] = int(rgb_match.group(2))
            result['b'] = int(rgb_match.group(3))
            return result
        
        # Check for rgba()
        rgba_match = self.patterns['color_rgba'].match(value)
        if rgba_match:
            result['type'] = 'rgba'
            result['r'] = int(rgba_match.group(1))
            result['g'] = int(rgba_match.group(2))
            result['b'] = int(rgba_match.group(3))
            result['a'] = float(rgba_match.group(4))
            return result
        
        # Named color or other
        result['type'] = 'named'
        return result
    
    def parse_calc(self, value: str) -> Dict[str, Any]:
        """
        Parse calc() expression.
        
        Args:
            value: calc() CSS value
            
        Returns:
            Dictionary with calc information
        """
        if not value.startswith('calc('):
            return {'type': 'invalid', 'value': value}
        
        expression = value[5:-1].strip()
        
        return {
            'type': 'calc',
            'expression': expression,
            'value': value
        }
    
    def parse_url(self, value: str) -> Optional[str]:
        """
        Extract URL from url() value.
        
        Args:
            value: url() CSS value
            
        Returns:
            Extracted URL or None
        """
        match = self.patterns['url'].match(value)
        if match:
            return match.group(1)
        return None
    
    def is_complex_value(self, value: str) -> bool:
        """
        Check if a value is complex (contains functions, multiple values, etc.).
        
        Args:
            value: CSS value
            
        Returns:
            True if complex, False otherwise
        """
        # Check for functions
        if '(' in value and ')' in value:
            return True
        
        # Check for multiple values (comma-separated)
        if ',' in value:
            return True
        
        # Check for multiple shadow values
        parts = value.split()
        if len(parts) > 3:
            # Might be a shadow or complex value
            return True
        
        return False
    
    def normalize_value(self, value: str) -> str:
        """
        Normalize a CSS value (trim, lowercase units, etc.).
        
        Args:
            value: CSS value
            
        Returns:
            Normalized value
        """
        value = value.strip()
        
        # Normalize zero values
        if value == '0px' or value == '0em' or value == '0rem' or value == '0%':
            return '0'
        
        # Normalize hex colors to lowercase
        if self.patterns['color_hex'].match(value):
            return value.lower()
        
        return value
    
    def split_list_value(self, value: str, separator: str = ',') -> List[str]:
        """
        Split a list value respecting parentheses.
        
        Args:
            value: CSS value with list
            separator: Separator character
            
        Returns:
            List of values
        """
        parts = []
        current = []
        paren_depth = 0
        
        for char in value:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == separator and paren_depth == 0:
                parts.append(''.join(current).strip())
                current = []
                continue
            
            current.append(char)
        
        if current:
            parts.append(''.join(current).strip())
        
        return parts