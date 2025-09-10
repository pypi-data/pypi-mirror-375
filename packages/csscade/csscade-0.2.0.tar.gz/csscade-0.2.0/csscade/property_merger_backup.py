"""Property-level merging logic for CSS."""

from typing import List, Dict, Union, Optional, Tuple
from csscade.models import CSSProperty, CSSRule
from csscade.resolvers.conflict_detector import ConflictDetector
from csscade.parser.css_parser import CSSParser
from csscade.utils.important_parser import ImportantParser


class PropertyMerger:
    """Handles merging of CSS properties with conflict resolution."""
    
    def __init__(self, important_strategy: str = 'match'):
        """
        Initialize the property merger.
        
        Args:
            important_strategy: Strategy for handling !important ('match', 'respect', 'override', 'force', 'strip')
        """
        self.conflict_detector = ConflictDetector()
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
        Merge two lists of CSS properties, with override taking precedence.
        
        Args:
            source: Base list of CSS properties
            override: Properties to override/add
            important_strategy: Override the default !important strategy
            
        Returns:
            Merged list of CSS properties
        """
        # Use provided strategy or default
        strategy = important_strategy or self.important_strategy
        
        # Clear messages
        self.info_messages = []
        self.warning_messages = []
        
        # Create a dictionary to track properties by name
        merged_props: Dict[str, CSSProperty] = {}
        
        # First, add all source properties
        for prop in source:
            merged_props[prop.name] = prop
            
            # Check if this property is affected by any shorthand in override
            for override_prop in override:
                if self.conflict_detector.is_shorthand(override_prop.name):
                    longhands = self.conflict_detector.get_longhand_properties(override_prop.name)
                    if prop.name in longhands:
                        # This longhand will be overridden by the shorthand
                        if prop.name in merged_props:
                            del merged_props[prop.name]
        
        # Then apply overrides with !important handling
        for override_prop in override:
            # Check if property exists in source
            original_prop = merged_props.get(override_prop.name)
            
            if strategy == 'respect' and original_prop and original_prop.important:
                # Don't override !important properties in respect mode
                self.info_messages.append(f"Property '{original_prop.name}' has !important and 'respect' mode is active - not overriding")
                continue
            
            # Apply the strategy to determine final importance
            final_prop = self._apply_important_strategy(original_prop, override_prop, strategy)
            
            # Remove any conflicting properties
            if self.conflict_detector.is_shorthand(override_prop.name):
                longhands = self.conflict_detector.get_longhand_properties(override_prop.name)
                for longhand in longhands:
                    if longhand in merged_props:
                        del merged_props[longhand]
            
            merged_props[override_prop.name] = final_prop
        
        return list(merged_props.values())
    
    def _apply_important_strategy(
        self,
        original: Optional[CSSProperty],
        override: CSSProperty,
        strategy: str
    ) -> CSSProperty:
        """
        Apply !important strategy to determine final property.
        
        Args:
            original: Original property (if exists)
            override: Override property
            strategy: Important strategy to apply
            
        Returns:
            Final property with appropriate !important flag
        """
        if strategy == 'match':
            # Default: match original's !important if override doesn't have explicit !important
            if original and original.important and not override.important:
                self.info_messages.append(f"Property '{override.name}' marked !important to match original")
                return CSSProperty(override.name, override.value, True)
            return override
            
        elif strategy == 'override':
            # Override but keep override's !important status
            if original and original.important and not override.important:
                self.warning_messages.append(f"Property '{override.name}' had !important but override doesn't - may not apply")
            return override
            
        elif strategy == 'force':
            # Always add !important
            if not override.important:
                self.info_messages.append(f"Force mode: Adding !important to '{override.name}'")
            return CSSProperty(override.name, override.value, True)
            
        elif strategy == 'strip':
            # Remove !important
            if override.important or (original and original.important):
                self.info_messages.append(f"Strip mode: Removing !important from '{override.name}'")
            return CSSProperty(override.name, override.value, False)
            
        else:
            # Unknown strategy, use default behavior
            return override
    
    def merge(
        self,
        source: Union[Dict[str, str], List[CSSProperty], str],
        override: Union[Dict[str, str], List[CSSProperty], str],
        important_strategy: Optional[str] = None
    ) -> Tuple[List[CSSProperty], List[str], List[str]]:
        """
        Merge CSS properties from various input formats.
        
        Args:
            source: Base CSS properties (dict, list, or string)
            override: Override CSS properties (dict, list, or string)
            important_strategy: Override the default !important strategy
            
        Returns:
            Tuple of (merged properties, info messages, warning messages)
        """
        # Parse source into list of properties
        if isinstance(source, str):
            source_props = self.parser.parse_properties_string(source)
        elif isinstance(source, dict):
            source_props = self.parser.parse_properties_dict(source)
        elif isinstance(source, list):
            source_props = source
        else:
            source_props = []
        
        # Parse override into list of properties, handling !important in values
        if isinstance(override, str):
            override_props = self.parser.parse_properties_string(override)
        elif isinstance(override, dict):
            # Parse dictionary values for !important
            override_props = []
            parsed_overrides = self.important_parser.parse_overrides_dict(override)
            for prop_name, (value, is_important) in parsed_overrides.items():
                override_props.append(CSSProperty(prop_name, value, is_important))
        elif isinstance(override, list):
            override_props = override
        else:
            override_props = []
        
        merged = self.merge_properties(source_props, override_props, important_strategy)
        return merged, self.info_messages, self.warning_messages
    
    def merge_rules(
        self,
        source_rule: CSSRule,
        override_properties: Union[Dict[str, str], List[CSSProperty], str],
        important_strategy: Optional[str] = None
    ) -> Tuple[CSSRule, List[str], List[str]]:
        """
        Merge override properties into a CSS rule.
        
        Args:
            source_rule: Base CSS rule
            override_properties: Properties to override/add
            important_strategy: Override the default !important strategy
            
        Returns:
            Tuple of (new CSS rule with merged properties, info messages, warning messages)
        """
        # Parse override properties
        if isinstance(override_properties, str):
            override_props = self.parser.parse_properties_string(override_properties)
        elif isinstance(override_properties, dict):
            # Parse dictionary values for !important
            override_props = []
            parsed_overrides = self.important_parser.parse_overrides_dict(override_properties)
            for prop_name, (value, is_important) in parsed_overrides.items():
                override_props.append(CSSProperty(prop_name, value, is_important))
        else:
            override_props = override_properties
        
        # Merge properties
        merged_props = self.merge_properties(source_rule.properties, override_props, important_strategy)
        
        # Create new rule with merged properties
        new_rule = CSSRule(selector=source_rule.selector, properties=merged_props)
        return new_rule, self.info_messages, self.warning_messages