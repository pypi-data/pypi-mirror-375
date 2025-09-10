"""Shorthand/longhand property resolution for CSS."""

from typing import Dict, List, Tuple, Optional, Any
from csscade.models import CSSProperty


class ShorthandResolver:
    """Resolves shorthand and longhand CSS property relationships."""
    
    def __init__(self):
        """Initialize the shorthand resolver."""
        # Map of how to expand common shorthands
        self.expansion_rules = {
            'margin': self._expand_box_model,
            'padding': self._expand_box_model,
            'border': self._expand_border,
            'border-width': self._expand_box_model,
            'border-style': self._expand_box_model,
            'border-color': self._expand_box_model,
            'border-radius': self._expand_corners,
            'background': self._expand_background,
            'font': self._expand_font,
            'flex': self._expand_flex,
            'animation': self._expand_animation,
            'transition': self._expand_transition,
            'list-style': self._expand_list_style,
            'text-decoration': self._expand_text_decoration,
            'outline': self._expand_outline,
            'overflow': self._expand_overflow,
            'gap': self._expand_gap,
            'place-content': self._expand_place_content,
            'place-items': self._expand_place_items,
            'place-self': self._expand_place_self,
        }
        
        # Map of how to combine longhands into shorthands
        self.combination_rules = {
            ('margin-top', 'margin-right', 'margin-bottom', 'margin-left'): 'margin',
            ('padding-top', 'padding-right', 'padding-bottom', 'padding-left'): 'padding',
            ('border-width', 'border-style', 'border-color'): 'border',
            ('flex-grow', 'flex-shrink', 'flex-basis'): 'flex',
            ('row-gap', 'column-gap'): 'gap',
        }
    
    def expand_shorthand(self, property_name: str, value: str) -> List[CSSProperty]:
        """
        Expand a shorthand property into its longhand components.
        
        Args:
            property_name: Shorthand property name
            value: Shorthand value
            
        Returns:
            List of longhand properties
        """
        if property_name in self.expansion_rules:
            # Special handling for box model properties
            if property_name in ['margin', 'padding', 'border-width', 'border-style', 'border-color']:
                return self._expand_box_model(value, property_name)
            return self.expansion_rules[property_name](value)
        return [CSSProperty(property_name, value)]
    
    def _expand_box_model(self, value: str, prefix: str = "") -> List[CSSProperty]:
        """
        Expand box model shorthand (margin, padding, border-width, etc.).
        
        Args:
            value: Shorthand value
            prefix: Property prefix (e.g., 'margin', 'padding')
            
        Returns:
            List of expanded properties
        """
        # Clean and split the value
        parts = value.strip().split()
        
        # Use the prefix directly - it's passed from expand_shorthand
        if not prefix:
            prefix = 'margin'  # Default fallback
        
        # Handle border properties differently - they use border-SIDE-PROPERTY pattern
        if prefix.startswith('border-'):
            # For border-width, border-style, border-color
            property_type = prefix.replace('border-', '')  # 'width', 'style', or 'color'
            if len(parts) == 1:
                val = parts[0]
                return [
                    CSSProperty(f'border-top-{property_type}', val),
                    CSSProperty(f'border-right-{property_type}', val),
                    CSSProperty(f'border-bottom-{property_type}', val),
                    CSSProperty(f'border-left-{property_type}', val)
                ]
            elif len(parts) == 2:
                vert, horiz = parts
                return [
                    CSSProperty(f'border-top-{property_type}', vert),
                    CSSProperty(f'border-right-{property_type}', horiz),
                    CSSProperty(f'border-bottom-{property_type}', vert),
                    CSSProperty(f'border-left-{property_type}', horiz)
                ]
            elif len(parts) == 3:
                top, horiz, bottom = parts
                return [
                    CSSProperty(f'border-top-{property_type}', top),
                    CSSProperty(f'border-right-{property_type}', horiz),
                    CSSProperty(f'border-bottom-{property_type}', bottom),
                    CSSProperty(f'border-left-{property_type}', horiz)
                ]
            elif len(parts) == 4:
                top, right, bottom, left = parts
                return [
                    CSSProperty(f'border-top-{property_type}', top),
                    CSSProperty(f'border-right-{property_type}', right),
                    CSSProperty(f'border-bottom-{property_type}', bottom),
                    CSSProperty(f'border-left-{property_type}', left)
                ]
        
        # Regular margin/padding pattern
        if len(parts) == 1:
            # All sides same value
            val = parts[0]
            return [
                CSSProperty(f'{prefix}-top', val),
                CSSProperty(f'{prefix}-right', val),
                CSSProperty(f'{prefix}-bottom', val),
                CSSProperty(f'{prefix}-left', val)
            ]
        elif len(parts) == 2:
            # Vertical | Horizontal
            vert, horiz = parts
            return [
                CSSProperty(f'{prefix}-top', vert),
                CSSProperty(f'{prefix}-right', horiz),
                CSSProperty(f'{prefix}-bottom', vert),
                CSSProperty(f'{prefix}-left', horiz)
            ]
        elif len(parts) == 3:
            # Top | Horizontal | Bottom
            top, horiz, bottom = parts
            return [
                CSSProperty(f'{prefix}-top', top),
                CSSProperty(f'{prefix}-right', horiz),
                CSSProperty(f'{prefix}-bottom', bottom),
                CSSProperty(f'{prefix}-left', horiz)
            ]
        elif len(parts) == 4:
            # Top | Right | Bottom | Left
            top, right, bottom, left = parts
            return [
                CSSProperty(f'{prefix}-top', top),
                CSSProperty(f'{prefix}-right', right),
                CSSProperty(f'{prefix}-bottom', bottom),
                CSSProperty(f'{prefix}-left', left)
            ]
        else:
            # Invalid, return as-is
            return [CSSProperty(prefix, value)]
    
    def _expand_border(self, value: str) -> List[CSSProperty]:
        """
        Expand border shorthand.
        
        Args:
            value: Border shorthand value
            
        Returns:
            List of expanded properties
        """
        # Border can have width, style, and color in any order
        parts = value.strip().split()
        
        width = None
        style = None
        color = None
        
        # Common border styles
        styles = {'none', 'hidden', 'dotted', 'dashed', 'solid', 'double', 
                 'groove', 'ridge', 'inset', 'outset'}
        
        for part in parts:
            # Check if it's a style
            if part in styles:
                style = part
            # Check if it's a width (number with unit or keywords)
            elif any(unit in part for unit in ['px', 'em', 'rem', '%']) or \
                 part in ['thin', 'medium', 'thick']:
                width = part
            # Otherwise assume it's a color
            else:
                color = part
        
        properties = []
        
        if width:
            properties.extend([
                CSSProperty('border-top-width', width),
                CSSProperty('border-right-width', width),
                CSSProperty('border-bottom-width', width),
                CSSProperty('border-left-width', width)
            ])
        
        if style:
            properties.extend([
                CSSProperty('border-top-style', style),
                CSSProperty('border-right-style', style),
                CSSProperty('border-bottom-style', style),
                CSSProperty('border-left-style', style)
            ])
        
        if color:
            properties.extend([
                CSSProperty('border-top-color', color),
                CSSProperty('border-right-color', color),
                CSSProperty('border-bottom-color', color),
                CSSProperty('border-left-color', color)
            ])
        
        return properties if properties else [CSSProperty('border', value)]
    
    def _expand_corners(self, value: str) -> List[CSSProperty]:
        """
        Expand border-radius shorthand.
        
        Args:
            value: Border-radius value
            
        Returns:
            List of expanded properties
        """
        # Handle slash notation for elliptical corners
        if '/' in value:
            horiz, vert = value.split('/')
            horiz_parts = horiz.strip().split()
            vert_parts = vert.strip().split()
            
            # For simplicity, just return as-is for complex elliptical
            return [CSSProperty('border-radius', value)]
        
        parts = value.strip().split()
        
        if len(parts) == 1:
            val = parts[0]
            return [
                CSSProperty('border-top-left-radius', val),
                CSSProperty('border-top-right-radius', val),
                CSSProperty('border-bottom-right-radius', val),
                CSSProperty('border-bottom-left-radius', val)
            ]
        elif len(parts) == 2:
            tl_br, tr_bl = parts
            return [
                CSSProperty('border-top-left-radius', tl_br),
                CSSProperty('border-top-right-radius', tr_bl),
                CSSProperty('border-bottom-right-radius', tl_br),
                CSSProperty('border-bottom-left-radius', tr_bl)
            ]
        elif len(parts) == 3:
            tl, tr_bl, br = parts
            return [
                CSSProperty('border-top-left-radius', tl),
                CSSProperty('border-top-right-radius', tr_bl),
                CSSProperty('border-bottom-right-radius', br),
                CSSProperty('border-bottom-left-radius', tr_bl)
            ]
        elif len(parts) == 4:
            tl, tr, br, bl = parts
            return [
                CSSProperty('border-top-left-radius', tl),
                CSSProperty('border-top-right-radius', tr),
                CSSProperty('border-bottom-right-radius', br),
                CSSProperty('border-bottom-left-radius', bl)
            ]
        else:
            return [CSSProperty('border-radius', value)]
    
    def _expand_background(self, value: str) -> List[CSSProperty]:
        """
        Expand background shorthand.
        
        Args:
            value: Background shorthand value
            
        Returns:
            List of expanded properties
        """
        # Background is complex, for now just handle simple cases
        if value in ['none', 'transparent']:
            return [
                CSSProperty('background-color', value),
                CSSProperty('background-image', 'none')
            ]
        
        # Check if it's just a color
        if not any(keyword in value for keyword in ['url(', 'linear-gradient', 'radial-gradient']):
            return [CSSProperty('background-color', value)]
        
        # Complex background, return as-is
        return [CSSProperty('background', value)]
    
    def _expand_font(self, value: str) -> List[CSSProperty]:
        """
        Expand font shorthand.
        
        Args:
            value: Font shorthand value
            
        Returns:
            List of expanded properties
        """
        # Font shorthand is complex, handle basic cases
        parts = value.strip().split()
        
        properties = []
        
        # Look for font-style (italic, oblique, normal)
        if any(style in parts for style in ['italic', 'oblique', 'normal']):
            for style in ['italic', 'oblique', 'normal']:
                if style in parts:
                    properties.append(CSSProperty('font-style', style))
                    parts.remove(style)
                    break
        
        # Look for font-weight
        weights = ['normal', 'bold', 'bolder', 'lighter', '100', '200', '300', 
                  '400', '500', '600', '700', '800', '900']
        for weight in weights:
            if weight in parts:
                properties.append(CSSProperty('font-weight', weight))
                parts.remove(weight)
                break
        
        # If we have parts left, they might be size/line-height and family
        if parts:
            # Last part(s) should be font-family
            # Second to last might be size/line-height
            return [CSSProperty('font', value)]  # Too complex, keep as shorthand
        
        return properties if properties else [CSSProperty('font', value)]
    
    def _expand_flex(self, value: str) -> List[CSSProperty]:
        """
        Expand flex shorthand.
        
        Args:
            value: Flex shorthand value
            
        Returns:
            List of expanded properties
        """
        parts = value.strip().split()
        
        if len(parts) == 1:
            val = parts[0]
            if val == 'none':
                return [
                    CSSProperty('flex-grow', '0'),
                    CSSProperty('flex-shrink', '0'),
                    CSSProperty('flex-basis', 'auto')
                ]
            elif val == 'auto':
                return [
                    CSSProperty('flex-grow', '1'),
                    CSSProperty('flex-shrink', '1'),
                    CSSProperty('flex-basis', 'auto')
                ]
            elif val.isdigit():
                return [
                    CSSProperty('flex-grow', val),
                    CSSProperty('flex-shrink', '1'),
                    CSSProperty('flex-basis', '0')
                ]
        elif len(parts) == 2:
            grow, shrink = parts
            return [
                CSSProperty('flex-grow', grow),
                CSSProperty('flex-shrink', shrink),
                CSSProperty('flex-basis', '0')
            ]
        elif len(parts) == 3:
            grow, shrink, basis = parts
            return [
                CSSProperty('flex-grow', grow),
                CSSProperty('flex-shrink', shrink),
                CSSProperty('flex-basis', basis)
            ]
        
        return [CSSProperty('flex', value)]
    
    def _expand_animation(self, value: str) -> List[CSSProperty]:
        """Expand animation shorthand."""
        # Animation is very complex, keep as shorthand for now
        return [CSSProperty('animation', value)]
    
    def _expand_transition(self, value: str) -> List[CSSProperty]:
        """Expand transition shorthand."""
        # Transition is complex, keep as shorthand for now
        return [CSSProperty('transition', value)]
    
    def _expand_list_style(self, value: str) -> List[CSSProperty]:
        """Expand list-style shorthand."""
        parts = value.strip().split()
        
        properties = []
        types = ['disc', 'circle', 'square', 'decimal', 'lower-roman', 'upper-roman',
                'lower-alpha', 'upper-alpha', 'none']
        positions = ['inside', 'outside']
        
        for part in parts:
            if part in types:
                properties.append(CSSProperty('list-style-type', part))
            elif part in positions:
                properties.append(CSSProperty('list-style-position', part))
            elif 'url(' in part:
                properties.append(CSSProperty('list-style-image', part))
        
        return properties if properties else [CSSProperty('list-style', value)]
    
    def _expand_text_decoration(self, value: str) -> List[CSSProperty]:
        """Expand text-decoration shorthand."""
        if value in ['none', 'underline', 'overline', 'line-through']:
            return [CSSProperty('text-decoration-line', value)]
        return [CSSProperty('text-decoration', value)]
    
    def _expand_outline(self, value: str) -> List[CSSProperty]:
        """Expand outline shorthand."""
        # Similar to border
        parts = value.strip().split()
        
        width = None
        style = None
        color = None
        
        styles = {'none', 'hidden', 'dotted', 'dashed', 'solid', 'double', 
                 'groove', 'ridge', 'inset', 'outset'}
        
        for part in parts:
            if part in styles:
                style = part
            elif any(unit in part for unit in ['px', 'em', 'rem']) or \
                 part in ['thin', 'medium', 'thick']:
                width = part
            else:
                color = part
        
        properties = []
        if width:
            properties.append(CSSProperty('outline-width', width))
        if style:
            properties.append(CSSProperty('outline-style', style))
        if color:
            properties.append(CSSProperty('outline-color', color))
        
        return properties if properties else [CSSProperty('outline', value)]
    
    def _expand_overflow(self, value: str) -> List[CSSProperty]:
        """Expand overflow shorthand."""
        parts = value.strip().split()
        
        if len(parts) == 1:
            return [
                CSSProperty('overflow-x', parts[0]),
                CSSProperty('overflow-y', parts[0])
            ]
        elif len(parts) == 2:
            return [
                CSSProperty('overflow-x', parts[0]),
                CSSProperty('overflow-y', parts[1])
            ]
        
        return [CSSProperty('overflow', value)]
    
    def _expand_gap(self, value: str) -> List[CSSProperty]:
        """Expand gap shorthand."""
        parts = value.strip().split()
        
        if len(parts) == 1:
            return [
                CSSProperty('row-gap', parts[0]),
                CSSProperty('column-gap', parts[0])
            ]
        elif len(parts) == 2:
            return [
                CSSProperty('row-gap', parts[0]),
                CSSProperty('column-gap', parts[1])
            ]
        
        return [CSSProperty('gap', value)]
    
    def _expand_place_content(self, value: str) -> List[CSSProperty]:
        """Expand place-content shorthand."""
        parts = value.strip().split()
        
        if len(parts) == 1:
            return [
                CSSProperty('align-content', parts[0]),
                CSSProperty('justify-content', parts[0])
            ]
        elif len(parts) == 2:
            return [
                CSSProperty('align-content', parts[0]),
                CSSProperty('justify-content', parts[1])
            ]
        
        return [CSSProperty('place-content', value)]
    
    def _expand_place_items(self, value: str) -> List[CSSProperty]:
        """Expand place-items shorthand."""
        parts = value.strip().split()
        
        if len(parts) == 1:
            return [
                CSSProperty('align-items', parts[0]),
                CSSProperty('justify-items', parts[0])
            ]
        elif len(parts) == 2:
            return [
                CSSProperty('align-items', parts[0]),
                CSSProperty('justify-items', parts[1])
            ]
        
        return [CSSProperty('place-items', value)]
    
    def _expand_place_self(self, value: str) -> List[CSSProperty]:
        """Expand place-self shorthand."""
        parts = value.strip().split()
        
        if len(parts) == 1:
            return [
                CSSProperty('align-self', parts[0]),
                CSSProperty('justify-self', parts[0])
            ]
        elif len(parts) == 2:
            return [
                CSSProperty('align-self', parts[0]),
                CSSProperty('justify-self', parts[1])
            ]
        
        return [CSSProperty('place-self', value)]
    
    def merge_with_shorthand(
        self,
        shorthand: CSSProperty,
        longhand: CSSProperty
    ) -> List[CSSProperty]:
        """
        Merge a longhand property with an existing shorthand.
        
        Args:
            shorthand: Existing shorthand property
            longhand: New longhand property to merge
            
        Returns:
            List of resulting properties
        """
        # Expand the shorthand
        expanded = self.expand_shorthand(shorthand.name, shorthand.value)
        
        # Replace the matching longhand
        result = []
        replaced = False
        for prop in expanded:
            if prop.name == longhand.name:
                result.append(longhand)
                replaced = True
            else:
                result.append(prop)
        
        # If not replaced, add it
        if not replaced:
            result.append(longhand)
        
        return result
    
    def can_combine_to_shorthand(self, properties: List[CSSProperty]) -> Optional[str]:
        """
        Check if a list of properties can be combined into a shorthand.
        
        Args:
            properties: List of CSS properties
            
        Returns:
            Shorthand property name if combinable, None otherwise
        """
        prop_names = tuple(sorted(prop.name for prop in properties))
        
        for longhand_tuple, shorthand in self.combination_rules.items():
            if set(prop_names) == set(longhand_tuple):
                return shorthand
        
        return None