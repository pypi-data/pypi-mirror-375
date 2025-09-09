"""Hybrid shorthand handler that uses proper expansion for simple shorthands and cascade for compound ones."""

from typing import Dict, List, Set, Tuple, Optional, Any
from csscade.models import CSSProperty


class HybridShorthandHandler:
    """
    Handles CSS shorthand properties using a hybrid approach:
    - Simple shorthands (margin, padding) are properly expanded
    - Compound shorthands (border, background) use CSS cascade
    """
    
    # Simple shorthands that we can reliably expand and recombine
    SIMPLE_SHORTHANDS = {
        'margin', 'padding', 'border-width', 'border-style', 'border-color',
        'border-radius', 'gap', 'overflow', 'inset', 'place-items', 'place-content'
    }
    
    # Compound shorthands that are too complex to handle properly
    COMPOUND_SHORTHANDS = {
        'border', 'background', 'font', 'animation', 'transition', 'transform-origin',
        'text-decoration', 'list-style', 'outline', 'box-shadow', 'flex', 'grid'
    }
    
    # Map simple shorthands to their longhand properties
    SHORTHAND_MAP = {
        'margin': ['margin-top', 'margin-right', 'margin-bottom', 'margin-left'],
        'padding': ['padding-top', 'padding-right', 'padding-bottom', 'padding-left'],
        'border-width': ['border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width'],
        'border-style': ['border-top-style', 'border-right-style', 'border-bottom-style', 'border-left-style'],
        'border-color': ['border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color'],
        'border-radius': ['border-top-left-radius', 'border-top-right-radius', 
                         'border-bottom-right-radius', 'border-bottom-left-radius'],
        'gap': ['row-gap', 'column-gap'],
        'overflow': ['overflow-x', 'overflow-y'],
        'inset': ['top', 'right', 'bottom', 'left']
    }
    
    def __init__(self):
        """Initialize the hybrid shorthand handler."""
        self.info_messages = []
        self.cascade_hacks_used = []
    
    def process_properties(
        self, 
        source: Dict[str, str], 
        override: Dict[str, str]
    ) -> Tuple[Dict[str, str], List[str]]:
        """
        Process source and override properties using hybrid approach.
        
        Args:
            source: Source properties
            override: Override properties
            
        Returns:
            Tuple of (merged properties, info messages)
        """
        self.info_messages = []
        self.cascade_hacks_used = []
        
        result = {}
        expanded_simple = {}
        
        # Step 1: Process source properties
        for prop, value in source.items():
            if prop in self.SIMPLE_SHORTHANDS:
                # Expand simple shorthands
                for longhand_prop, longhand_value in self._expand_simple_shorthand(prop, value).items():
                    expanded_simple[longhand_prop] = longhand_value
            elif prop in self.COMPOUND_SHORTHANDS:
                # Keep compound shorthands as-is
                result[prop] = value
            else:
                # Check if it's a longhand of a simple shorthand
                if self._is_simple_longhand(prop):
                    expanded_simple[prop] = value
                else:
                    result[prop] = value
        
        # Step 2: Apply overrides
        for prop, value in override.items():
            if prop in self.SIMPLE_SHORTHANDS:
                # Check if there's a compound shorthand in source that this relates to
                if self._should_use_cascade_for_simple(prop, source):
                    # Use cascade hack instead of expansion
                    result[prop] = value
                    self._add_cascade_info(prop, source)
                else:
                    # Replace all related longhands
                    for longhand in self.SHORTHAND_MAP.get(prop, []):
                        expanded_simple.pop(longhand, None)
                    # Add new expanded values
                    for longhand_prop, longhand_value in self._expand_simple_shorthand(prop, value).items():
                        expanded_simple[longhand_prop] = longhand_value
                    
            elif prop in self.COMPOUND_SHORTHANDS:
                # Replace the compound shorthand
                result[prop] = value
                # Remove any specific overrides that might conflict
                self._remove_compound_related(result, prop)
                
            else:  # It's a longhand
                if self._is_compound_longhand(prop):
                    # This is where we use the cascade hack
                    result[prop] = value
                    self._add_cascade_info(prop, source)
                elif self._is_simple_longhand(prop):
                    # Properly handle simple longhand
                    expanded_simple[prop] = value
                else:
                    # Regular property
                    result[prop] = value
        
        # Step 3: Combine results
        # Add expanded simple properties
        result.update(expanded_simple)
        
        return result, self.info_messages
    
    def _expand_simple_shorthand(self, prop: str, value: str) -> Dict[str, str]:
        """Expand a simple shorthand to its longhands."""
        longhands = self.SHORTHAND_MAP.get(prop, [])
        if not longhands:
            return {prop: value}
        
        values = self._parse_box_values(value)
        result = {}
        
        if prop in ['margin', 'padding', 'border-width', 'border-style', 'border-color', 'inset']:
            # Box model: top, right, bottom, left
            if len(values) == 1:
                for longhand in longhands:
                    result[longhand] = values[0]
            elif len(values) == 2:
                result[longhands[0]] = values[0]  # top
                result[longhands[1]] = values[1]  # right
                result[longhands[2]] = values[0]  # bottom
                result[longhands[3]] = values[1]  # left
            elif len(values) == 3:
                result[longhands[0]] = values[0]  # top
                result[longhands[1]] = values[1]  # right
                result[longhands[2]] = values[2]  # bottom
                result[longhands[3]] = values[1]  # left (same as right)
            elif len(values) == 4:
                for i, longhand in enumerate(longhands):
                    result[longhand] = values[i]
        elif prop == 'gap':
            # gap: row-gap column-gap
            if len(values) == 1:
                result['row-gap'] = values[0]
                result['column-gap'] = values[0]
            else:
                result['row-gap'] = values[0]
                result['column-gap'] = values[1] if len(values) > 1 else values[0]
        elif prop == 'overflow':
            # overflow: overflow-x overflow-y
            if len(values) == 1:
                result['overflow-x'] = values[0]
                result['overflow-y'] = values[0]
            else:
                result['overflow-x'] = values[0]
                result['overflow-y'] = values[1] if len(values) > 1 else values[0]
        else:
            # Default: apply first value to all
            for longhand in longhands:
                result[longhand] = values[0] if values else value
        
        return result
    
    def _parse_box_values(self, value: str) -> List[str]:
        """Parse space-separated values (e.g., '10px 20px')."""
        # Simple split for now - in production, need proper CSS value parsing
        return value.strip().split()
    
    def _is_simple_longhand(self, prop: str) -> bool:
        """Check if property is a longhand of a simple shorthand."""
        for longhands in self.SHORTHAND_MAP.values():
            if prop in longhands:
                return True
        return False
    
    def _is_compound_longhand(self, prop: str) -> bool:
        """Check if property is related to a compound shorthand."""
        # If it's a simple shorthand itself, it's not a compound longhand
        if prop in self.SIMPLE_SHORTHANDS:
            return False
            
        compound_prefixes = [
            'border-', 'background-', 'font-', 'animation-', 
            'transition-', 'text-decoration-', 'list-style-', 'outline-'
        ]
        
        for prefix in compound_prefixes:
            if prop.startswith(prefix):
                return True
        return False
    
    def _remove_compound_related(self, result: Dict[str, str], compound_prop: str) -> None:
        """Remove properties that would conflict with a compound shorthand."""
        # When setting 'border', remove any 'border-*' properties
        if compound_prop == 'border':
            to_remove = [k for k in result.keys() if k.startswith('border-') and 
                        k not in self.SIMPLE_SHORTHANDS]
            for k in to_remove:
                del result[k]
        # Add more compound shorthand handling as needed
    
    def _should_use_cascade_for_simple(self, prop: str, source: Dict[str, str]) -> bool:
        """Check if a simple shorthand should use cascade hack due to compound parent."""
        # If source has 'border' and we're overriding 'border-width', use cascade
        if prop in ['border-width', 'border-style', 'border-color'] and 'border' in source:
            return True
        # Add more compound/simple relationships as needed
        return False
    
    def _add_cascade_info(self, prop: str, source: Dict[str, str]) -> None:
        """Add info message about cascade hack usage."""
        # Find which compound shorthand this relates to
        compound_parent = None
        if prop.startswith('border-') and 'border' in source:
            compound_parent = 'border'
        elif prop.startswith('background-') and 'background' in source:
            compound_parent = 'background'
        # Add more as needed
        
        if compound_parent and compound_parent not in self.cascade_hacks_used:
            self.cascade_hacks_used.append(compound_parent)
            self.info_messages.append(
                f"Using CSS cascade to override '{prop}' on '{compound_parent}'. "
                f"The override appears after the shorthand in the output, allowing CSS cascade to handle it correctly."
            )