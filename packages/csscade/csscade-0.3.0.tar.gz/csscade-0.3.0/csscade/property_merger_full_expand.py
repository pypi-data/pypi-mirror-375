"""Property-level merging logic for CSS with intelligent shorthand handling."""

from typing import List, Dict, Union, Optional, Tuple
from csscade.models import CSSProperty, CSSRule
from csscade.resolvers.conflict_detector import ConflictDetector
from csscade.handlers.shorthand import ShorthandResolver
from csscade.parser.css_parser import CSSParser
from csscade.utils.important_parser import ImportantParser


class PropertyMerger:
    """Handles merging of CSS properties with intelligent shorthand/longhand resolution."""
    
    def __init__(self, important_strategy: str = 'match'):
        """
        Initialize the property merger.
        
        Args:
            important_strategy: Strategy for handling !important ('match', 'respect', 'override', 'force', 'strip')
        """
        self.conflict_detector = ConflictDetector()
        self.shorthand_resolver = ShorthandResolver()
        self.parser = CSSParser()
        self.important_parser = ImportantParser()
        self.important_strategy = important_strategy
        self.info_messages = []
        self.warning_messages = []
    
    def merge_properties(
        self,
        source: List[CSSProperty],
        override: List[CSSProperty],
        important_strategy: Optional[str] = None
    ) -> List[CSSProperty]:
        """
        Merge two lists of CSS properties with intelligent shorthand handling.
        
        This is the old interface for backward compatibility.
        Use merge() for the new interface with message returns.
        """
        result, _, _ = self.merge(source, override, important_strategy)
        return result
    
    def merge_rules(
        self,
        source_rule: CSSRule,
        override_props: List[CSSProperty]
    ) -> Tuple[CSSRule, List[str], List[str]]:
        """
        Merge a CSS rule with override properties.
        
        This is the interface expected by strategies.
        
        Args:
            source_rule: Source CSS rule
            override_props: Override properties
            
        Returns:
            Tuple of (merged rule, info messages, warnings)
        """
        merged_props, info, warnings = self.merge(source_rule.properties, override_props)
        merged_rule = CSSRule(selector=source_rule.selector, properties=merged_props)
        return merged_rule, info, warnings
    
    def merge(
        self,
        source: List[CSSProperty],
        override: List[CSSProperty],
        important_strategy: Optional[str] = None
    ) -> Tuple[List[CSSProperty], List[str], List[str]]:
        """
        Merge source and override properties with intelligent shorthand handling.
        
        Key features:
        1. Expands shorthands for intelligent merging
        2. Preserves longhand values when only partial override occurs
        3. Recombines to shorthand when possible for cleaner output
        4. Handles !important conflicts according to strategy
        
        Args:
            source: List of source CSS properties
            override: List of override CSS properties
            important_strategy: Override default !important strategy for this merge
            
        Returns:
            Tuple of (merged properties, info messages, warnings)
        """
        # Reset messages
        self.info_messages = []
        self.warning_messages = []
        
        # Use provided strategy or default
        strategy = important_strategy or self.important_strategy
        
        # Validate strategy
        if strategy not in ['match', 'respect', 'override', 'force', 'strip']:
            self.warning_messages.append(f"Unknown important strategy '{strategy}', using 'match'")
            strategy = 'match'
        
        # Step 1: Expand all shorthands to longhands for intelligent merging
        expanded_source = self._expand_all_properties(source)
        expanded_override = self._expand_all_properties(override)
        
        # Step 2: Merge at the longhand level
        merged_longhands = self._merge_longhands(expanded_source, expanded_override, strategy)
        
        # Step 3: Optimize back to shorthands where possible
        optimized_result = self._optimize_to_shorthands(merged_longhands)
        
        return optimized_result, self.info_messages, self.warning_messages
    
    def _expand_all_properties(self, properties: List[CSSProperty]) -> Dict[str, CSSProperty]:
        """
        Expand all properties, converting shorthands to longhands.
        Returns a dictionary mapping property names to CSSProperty objects.
        """
        expanded = {}
        
        for prop in properties:
            # Check for typos like border-color-top instead of border-top-color
            fixed_name = self._fix_property_name(prop.name)
            if fixed_name != prop.name:
                prop = CSSProperty(name=fixed_name, value=prop.value, important=getattr(prop, 'important', False))
            
            if self.conflict_detector.is_shorthand(prop.name):
                # Expand shorthand to longhands
                try:
                    longhands = self.shorthand_resolver.expand_shorthand(prop.name, prop.value)
                    for longhand in longhands:
                        # Preserve important flag from shorthand
                        if hasattr(prop, 'important') and prop.important:
                            longhand.important = True
                        expanded[longhand.name] = longhand
                except Exception as e:
                    # If expansion fails, keep as-is
                    self.warning_messages.append(f"Could not expand {prop.name}: {e}")
                    expanded[prop.name] = prop
            else:
                # Already a longhand or unrecognized property
                expanded[prop.name] = prop
        
        return expanded
    
    def _fix_property_name(self, name: str) -> str:
        """Fix common property name mistakes."""
        # Fix border property names
        if name.startswith('border-color-'):
            side = name.replace('border-color-', '')
            if side in ['top', 'right', 'bottom', 'left']:
                return f'border-{side}-color'
        elif name.startswith('border-width-'):
            side = name.replace('border-width-', '')
            if side in ['top', 'right', 'bottom', 'left']:
                return f'border-{side}-width'
        elif name.startswith('border-style-'):
            side = name.replace('border-style-', '')
            if side in ['top', 'right', 'bottom', 'left']:
                return f'border-{side}-style'
        return name
    
    def _merge_longhands(
        self,
        source_expanded: Dict[str, CSSProperty],
        override_expanded: Dict[str, CSSProperty],
        strategy: str
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
            if strategy == 'respect' and original_prop and hasattr(original_prop, 'important') and original_prop.important:
                self.info_messages.append(
                    f"Property '{prop_name}' has !important and 'respect' mode is active - not overriding"
                )
                continue
            
            # Determine final property with !important handling
            final_prop = self._apply_important_strategy(original_prop, override_prop, strategy)
            merged[prop_name] = final_prop
        
        return merged
    
    def _apply_important_strategy(
        self,
        original: Optional[CSSProperty],
        override: CSSProperty,
        strategy: str
    ) -> CSSProperty:
        """
        Apply !important strategy to determine final property.
        
        Args:
            original: Original property (may be None)
            override: Override property
            strategy: Important strategy to apply
            
        Returns:
            Final property with appropriate !important flag
        """
        # Parse !important from override value if present
        clean_value, has_important = self.important_parser.parse_value_with_important(override.value)
        
        # Create new property with clean value
        result = CSSProperty(
            name=override.name,
            value=clean_value,
            important=has_important
        )
        
        # Apply strategy
        if strategy == 'match':
            # If original had !important and override doesn't, add it
            if original and hasattr(original, 'important') and original.important and not has_important:
                result.important = True
                self.info_messages.append(f"Property '{override.name}' marked !important to match original")
        
        elif strategy == 'force':
            # Always add !important
            if not result.important:
                result.important = True
                self.info_messages.append(f"Force mode: Adding !important to '{override.name}'")
        
        elif strategy == 'strip':
            # Remove !important
            if result.important:
                result.important = False
                self.info_messages.append(f"Strip mode: Removing !important from '{override.name}'")
        
        elif strategy == 'override':
            # Keep as-is but warn if original had !important
            if original and hasattr(original, 'important') and original.important and not has_important:
                self.warning_messages.append(
                    f"Property '{override.name}' had !important but override doesn't - may not apply"
                )
        
        return result
    
    def _optimize_to_shorthands(self, longhands: Dict[str, CSSProperty]) -> List[CSSProperty]:
        """
        Optimize longhands back to shorthands where possible for cleaner output.
        """
        result = []
        processed = set()
        
        # Define shorthand groups that can be combined
        # Order matters - check more specific patterns first
        shorthand_groups = [
            (['margin-top', 'margin-right', 'margin-bottom', 'margin-left'], 'margin'),
            (['padding-top', 'padding-right', 'padding-bottom', 'padding-left'], 'padding'),
            (['border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width'], 'border-width'),
            (['border-top-style', 'border-right-style', 'border-bottom-style', 'border-left-style'], 'border-style'),
            (['border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color'], 'border-color'),
            (['border-top-left-radius', 'border-top-right-radius', 'border-bottom-right-radius', 'border-bottom-left-radius'], 'border-radius'),
            (['overflow-x', 'overflow-y'], 'overflow'),
            (['row-gap', 'column-gap'], 'gap'),
        ]
        
        for longhand_names, shorthand_name in shorthand_groups:
            # Check if all longhands are present and not yet processed
            if all(name in longhands and name not in processed for name in longhand_names):
                values = [longhands[name].value for name in longhand_names]
                
                # Try to combine into shorthand
                combined_value = self._try_combine_to_shorthand(longhand_names, values, shorthand_name)
                
                if combined_value:
                    # Check if all have same !important status
                    all_important = all(
                        hasattr(longhands[name], 'important') and longhands[name].important 
                        for name in longhand_names
                    )
                    any_important = any(
                        hasattr(longhands[name], 'important') and longhands[name].important 
                        for name in longhand_names
                    )
                    
                    if all_important or not any_important:
                        # Can combine - all have same !important status
                        result.append(CSSProperty(
                            name=shorthand_name,
                            value=combined_value,
                            important=all_important
                        ))
                        for name in longhand_names:
                            processed.add(name)
                        # Only log optimization in verbose mode
                        # self.info_messages.append(f"Optimized {', '.join(longhand_names)} to {shorthand_name}")
                    else:
                        # Mixed !important - keep as longhands
                        for name in longhand_names:
                            if name not in processed:
                                result.append(longhands[name])
                                processed.add(name)
        
        # Add remaining properties
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
            if len(values) == 2:
                x, y = values
                if x == y:
                    return x
                else:
                    return f"{x} {y}"
        
        elif shorthand_name == 'gap':
            if len(values) == 2:
                row, col = values
                if row == col:
                    return row
                else:
                    return f"{row} {col}"
        
        return None