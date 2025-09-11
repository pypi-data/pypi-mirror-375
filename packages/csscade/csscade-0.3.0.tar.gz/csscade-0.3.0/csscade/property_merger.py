"""Property-level merging logic for CSS with configurable shorthand handling."""

from typing import List, Dict, Union, Optional, Tuple
from csscade.models import CSSProperty, CSSRule
from csscade.resolvers.conflict_detector import ConflictDetector
from csscade.handlers.shorthand import ShorthandResolver
from csscade.parser.css_parser import CSSParser
from csscade.utils.important_parser import ImportantParser


class PropertyMerger:
    """Handles merging of CSS properties with configurable shorthand handling."""
    
    # Properties that benefit from intelligent expansion
    SMART_EXPAND_PROPERTIES = {
        'margin', 'padding',  # These are simple and benefit from smart merging
        # 'border', 'border-width', etc. are NOT here - they cascade by default
    }
    
    def __init__(self, important_strategy: str = 'match', shorthand_strategy: str = 'cascade'):
        """
        Initialize the property merger.
        
        Args:
            important_strategy: Strategy for handling !important ('match', 'respect', 'override', 'force', 'strip')
            shorthand_strategy: Strategy for handling shorthands:
                - 'cascade': Let CSS cascade handle it (default)
                - 'smart': Intelligently expand simple properties only
                - 'expand': Expand all shorthands for intelligent merging
        """
        self.conflict_detector = ConflictDetector()
        self.shorthand_resolver = ShorthandResolver()
        self.parser = CSSParser()
        self.important_parser = ImportantParser()
        self.important_strategy = important_strategy
        self.shorthand_strategy = shorthand_strategy
        self.info_messages = []
        self.warning_messages = []
    
    def merge_properties(
        self,
        source: List[CSSProperty],
        override: List[CSSProperty],
        important_strategy: Optional[str] = None
    ) -> List[CSSProperty]:
        """
        Merge two lists of CSS properties.
        
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
        Merge source and override properties based on strategy.
        
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
        
        # Handle based on shorthand strategy
        if self.shorthand_strategy == 'cascade':
            # Simple cascade mode - just combine properties
            return self._merge_cascade_mode(source, override, strategy)
        elif self.shorthand_strategy == 'smart':
            # Smart mode - expand only simple properties
            return self._merge_smart_mode(source, override, strategy)
        else:  # 'expand'
            # Full expansion mode - expand everything
            return self._merge_expand_mode(source, override, strategy)
    
    def _merge_cascade_mode(
        self,
        source: List[CSSProperty],
        override: List[CSSProperty],
        strategy: str
    ) -> Tuple[List[CSSProperty], List[str], List[str]]:
        """
        Simple cascade mode - combine properties, let CSS cascade handle conflicts.
        """
        # Create a dictionary to track properties by name
        merged_props: Dict[str, CSSProperty] = {}
        
        # Add all source properties
        for prop in source:
            merged_props[prop.name] = prop
        
        # Apply overrides - simply replace if same property name
        for override_prop in override:
            original_prop = merged_props.get(override_prop.name)
            
            # Apply !important strategy
            if strategy == 'respect' and original_prop and hasattr(original_prop, 'important') and original_prop.important:
                self.info_messages.append(
                    f"Property '{override_prop.name}' has !important and 'respect' mode is active - not overriding"
                )
                continue
            
            # Apply important strategy and add/replace property
            final_prop = self._apply_important_strategy(original_prop, override_prop, strategy)
            merged_props[override_prop.name] = final_prop
        
        return list(merged_props.values()), self.info_messages, self.warning_messages
    
    def _merge_smart_mode(
        self,
        source: List[CSSProperty],
        override: List[CSSProperty],
        strategy: str
    ) -> Tuple[List[CSSProperty], List[str], List[str]]:
        """
        Smart mode - intelligently expand only simple properties like margin/padding.
        Complex properties like border use cascade.
        """
        # Separate properties into smart-expand and cascade groups
        source_smart = []
        source_cascade = []
        override_smart = []
        override_cascade = []
        
        for prop in source:
            if self._should_smart_expand(prop.name):
                source_smart.append(prop)
            else:
                source_cascade.append(prop)
        
        for prop in override:
            if self._should_smart_expand(prop.name):
                override_smart.append(prop)
            else:
                override_cascade.append(prop)
        
        # Handle smart properties with expansion
        smart_result = []
        if source_smart or override_smart:
            expanded_source = self._expand_all_properties(source_smart)
            expanded_override = self._expand_all_properties(override_smart)
            merged_longhands = self._merge_longhands(expanded_source, expanded_override, strategy)
            smart_result = self._optimize_to_shorthands(merged_longhands)
        
        # Handle cascade properties simply
        cascade_dict = {}
        for prop in source_cascade:
            cascade_dict[prop.name] = prop
        for prop in override_cascade:
            original = cascade_dict.get(prop.name)
            if strategy == 'respect' and original and hasattr(original, 'important') and original.important:
                self.info_messages.append(
                    f"Property '{prop.name}' has !important and 'respect' mode is active - not overriding"
                )
                continue
            cascade_dict[prop.name] = self._apply_important_strategy(original, prop, strategy)
        
        # Combine results
        all_results = smart_result + list(cascade_dict.values())
        return all_results, self.info_messages, self.warning_messages
    
    def _merge_expand_mode(
        self,
        source: List[CSSProperty],
        override: List[CSSProperty],
        strategy: str
    ) -> Tuple[List[CSSProperty], List[str], List[str]]:
        """
        Full expansion mode - expand all shorthands for intelligent merging.
        """
        # Step 1: Expand all shorthands to longhands
        expanded_source = self._expand_all_properties(source)
        expanded_override = self._expand_all_properties(override)
        
        # Step 2: Merge at the longhand level
        merged_longhands = self._merge_longhands(expanded_source, expanded_override, strategy)
        
        # Step 3: Optimize back to shorthands where possible
        optimized_result = self._optimize_to_shorthands(merged_longhands)
        
        return optimized_result, self.info_messages, self.warning_messages
    
    def _should_smart_expand(self, property_name: str) -> bool:
        """
        Determine if a property should be smartly expanded.
        
        Args:
            property_name: CSS property name
            
        Returns:
            True if property should be expanded, False otherwise
        """
        # Check if it's a simple property that benefits from expansion
        if property_name in self.SMART_EXPAND_PROPERTIES:
            return True
        
        # Check if it's a longhand of a smart property
        for smart_prop in self.SMART_EXPAND_PROPERTIES:
            if property_name.startswith(f"{smart_prop}-"):
                return True
        
        return False
    
    def _expand_all_properties(self, properties: List[CSSProperty]) -> Dict[str, CSSProperty]:
        """
        Expand all properties, converting shorthands to longhands.
        Returns a dictionary mapping property names to CSSProperty objects.
        """
        expanded = {}
        
        for prop in properties:
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
        Only used in smart/expand modes.
        """
        result = []
        processed = set()
        
        # Define shorthand groups that can be combined
        shorthand_groups = [
            (['margin-top', 'margin-right', 'margin-bottom', 'margin-left'], 'margin'),
            (['padding-top', 'padding-right', 'padding-bottom', 'padding-left'], 'padding'),
        ]
        
        # Only try to combine simple properties
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
        if shorthand_name in ['margin', 'padding']:
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
        
        return None