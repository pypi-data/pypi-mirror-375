"""Enhanced property merger with intelligent shorthand/longhand handling."""

from typing import Dict, List, Optional, Tuple
from csscade.models import CSSProperty
from csscade.resolvers.conflict_detector import ConflictDetector
from csscade.handlers.shorthand import ShorthandResolver
from csscade.utils.important_parser import ImportantParser


class EnhancedPropertyMerger:
    """
    Enhanced property merger that intelligently handles shorthand/longhand conflicts.
    
    Key improvements:
    1. Expands shorthands when needed for intelligent merging
    2. Preserves longhand values when only partial override occurs
    3. Recombines to shorthand when possible for cleaner output
    """
    
    def __init__(self, important_strategy: str = 'match'):
        """Initialize the enhanced property merger."""
        self.conflict_detector = ConflictDetector()
        self.shorthand_resolver = ShorthandResolver()
        self.important_parser = ImportantParser()
        self.important_strategy = important_strategy
        self.warnings = []
        self.info_messages = []
    
    def merge(
        self,
        source: List[CSSProperty],
        override: List[CSSProperty]
    ) -> Tuple[List[CSSProperty], List[str], List[str]]:
        """
        Merge source and override properties with intelligent shorthand handling.
        
        Args:
            source: List of source CSS properties
            override: List of override CSS properties
            
        Returns:
            Tuple of (merged properties, info messages, warnings)
        """
        self.warnings = []
        self.info_messages = []
        
        # Step 1: Expand all shorthands to longhands for processing
        expanded_source = self._expand_all_properties(source)
        expanded_override = self._expand_all_properties(override)
        
        # Step 2: Merge at the longhand level
        merged_longhands = self._merge_longhands(expanded_source, expanded_override)
        
        # Step 3: Try to recombine longhands back to shorthands where possible
        optimized_result = self._optimize_to_shorthands(merged_longhands)
        
        return optimized_result, self.info_messages, self.warnings
    
    def _expand_all_properties(self, properties: List[CSSProperty]) -> Dict[str, CSSProperty]:
        """
        Expand all properties, converting shorthands to longhands.
        
        Returns a dictionary mapping property names to CSSProperty objects.
        """
        expanded = {}
        
        for prop in properties:
            if self.conflict_detector.is_shorthand(prop.name):
                # Expand shorthand to longhands
                longhands = self.shorthand_resolver.expand_shorthand(prop.name, prop.value)
                for longhand in longhands:
                    # Preserve important flag from shorthand
                    if hasattr(prop, 'important') and prop.important:
                        longhand.important = True
                    expanded[longhand.name] = longhand
            else:
                # Already a longhand or unrecognized property
                expanded[prop.name] = prop
        
        return expanded
    
    def _merge_longhands(
        self,
        source_expanded: Dict[str, CSSProperty],
        override_expanded: Dict[str, CSSProperty]
    ) -> Dict[str, CSSProperty]:
        """
        Merge expanded longhands with proper !important handling.
        """
        merged = {}
        
        # Start with source properties
        merged.update(source_expanded)
        
        # Apply overrides with !important strategy
        for prop_name, override_prop in override_expanded.items():
            original_prop = merged.get(prop_name)
            
            # Apply !important strategy
            if self.important_strategy == 'respect' and original_prop and original_prop.important:
                self.info_messages.append(
                    f"Property '{prop_name}' has !important in source - not overriding (respect mode)"
                )
                continue
            
            # Determine final property with !important handling
            final_prop = self._apply_important_strategy(original_prop, override_prop)
            merged[prop_name] = final_prop
        
        return merged
    
    def _apply_important_strategy(
        self,
        original: Optional[CSSProperty],
        override: CSSProperty
    ) -> CSSProperty:
        """Apply !important strategy to determine final property."""
        # Parse !important from override value if present
        clean_value, has_important = self.important_parser.parse_value_with_important(override.value)
        
        # Create new property with clean value
        result = CSSProperty(
            name=override.name,
            value=clean_value,
            important=has_important
        )
        
        # Apply strategy
        if self.important_strategy == 'match' and original and original.important and not has_important:
            result.important = True
            self.info_messages.append(f"Property '{override.name}' marked !important to match original")
        elif self.important_strategy == 'force':
            result.important = True
            self.info_messages.append(f"Force mode: Adding !important to '{override.name}'")
        elif self.important_strategy == 'strip':
            result.important = False
            if has_important or (original and original.important):
                self.info_messages.append(f"Strip mode: Removing !important from '{override.name}'")
        elif self.important_strategy == 'override' and original and original.important and not has_important:
            self.warnings.append(
                f"Property '{override.name}' had !important but override doesn't - may not apply"
            )
        
        return result
    
    def _optimize_to_shorthands(self, longhands: Dict[str, CSSProperty]) -> List[CSSProperty]:
        """
        Optimize longhands back to shorthands where possible.
        
        This creates cleaner CSS output by combining related longhands.
        """
        result = []
        processed = set()
        
        # Check for common shorthand groups
        shorthand_groups = [
            # Margin
            (['margin-top', 'margin-right', 'margin-bottom', 'margin-left'], 'margin'),
            # Padding  
            (['padding-top', 'padding-right', 'padding-bottom', 'padding-left'], 'padding'),
            # Border width
            (['border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width'], 'border-width'),
            # Border style
            (['border-top-style', 'border-right-style', 'border-bottom-style', 'border-left-style'], 'border-style'),
            # Border color
            (['border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color'], 'border-color'),
            # Border radius
            (['border-top-left-radius', 'border-top-right-radius', 'border-bottom-right-radius', 'border-bottom-left-radius'], 'border-radius'),
            # Overflow
            (['overflow-x', 'overflow-y'], 'overflow'),
            # Gap
            (['row-gap', 'column-gap'], 'gap'),
        ]
        
        for longhand_names, shorthand_name in shorthand_groups:
            # Check if all longhands are present
            if all(name in longhands and name not in processed for name in longhand_names):
                # Get the values
                values = [longhands[name].value for name in longhand_names]
                
                # Check if they can be combined
                combined_value = self._try_combine_to_shorthand(longhand_names, values, shorthand_name)
                
                if combined_value:
                    # Check if all have same !important status
                    all_important = all(longhands[name].important if hasattr(longhands[name], 'important') else False 
                                      for name in longhand_names)
                    any_important = any(longhands[name].important if hasattr(longhands[name], 'important') else False 
                                      for name in longhand_names)
                    
                    if all_important or not any_important:
                        # Can combine - all have same !important status
                        result.append(CSSProperty(
                            name=shorthand_name,
                            value=combined_value,
                            important=all_important
                        ))
                        for name in longhand_names:
                            processed.add(name)
                        self.info_messages.append(f"Combined {', '.join(longhand_names)} to {shorthand_name}")
                    else:
                        # Mixed !important status - keep as longhands
                        for name in longhand_names:
                            if name not in processed:
                                result.append(longhands[name])
                                processed.add(name)
        
        # Add any remaining properties that weren't processed
        for name, prop in longhands.items():
            if name not in processed:
                result.append(prop)
        
        return result
    
    def _try_combine_to_shorthand(
        self,
        longhand_names: List[str],
        values: List[str],
        shorthand_name: str
    ) -> Optional[str]:
        """
        Try to combine longhand values into a shorthand value.
        
        Returns the combined shorthand value, or None if cannot combine.
        """
        if shorthand_name in ['margin', 'padding', 'border-width', 'border-style', 'border-color']:
            # Box model properties
            if len(values) == 4:
                top, right, bottom, left = values
                
                # All same
                if top == right == bottom == left:
                    return top
                # Vertical | Horizontal
                elif top == bottom and left == right:
                    return f"{top} {right}"
                # Top | Horizontal | Bottom
                elif left == right:
                    return f"{top} {right} {bottom}"
                # All different
                else:
                    return f"{top} {right} {bottom} {left}"
        
        elif shorthand_name == 'border-radius':
            # Border radius
            if len(values) == 4:
                tl, tr, br, bl = values
                
                # All same
                if tl == tr == br == bl:
                    return tl
                # Diagonal pairs
                elif tl == br and tr == bl:
                    return f"{tl} {tr}"
                # Three values
                elif tr == bl:
                    return f"{tl} {tr} {br}"
                # All different
                else:
                    return f"{tl} {tr} {br} {bl}"
        
        elif shorthand_name == 'overflow':
            # Overflow
            if len(values) == 2:
                x, y = values
                if x == y:
                    return x
                else:
                    return f"{x} {y}"
        
        elif shorthand_name == 'gap':
            # Gap
            if len(values) == 2:
                row, col = values
                if row == col:
                    return row
                else:
                    return f"{row} {col}"
        
        return None