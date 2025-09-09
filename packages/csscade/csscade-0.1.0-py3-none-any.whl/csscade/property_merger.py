"""Property-level merging logic for CSS."""

from typing import List, Dict, Union
from csscade.models import CSSProperty, CSSRule
from csscade.resolvers.conflict_detector import ConflictDetector
from csscade.parser.css_parser import CSSParser


class PropertyMerger:
    """Handles merging of CSS properties with conflict resolution."""
    
    def __init__(self):
        """Initialize the property merger."""
        self.conflict_detector = ConflictDetector()
        self.parser = CSSParser()
    
    def merge_properties(
        self,
        source: List[CSSProperty],
        override: List[CSSProperty]
    ) -> List[CSSProperty]:
        """
        Merge two lists of CSS properties, with override taking precedence.
        
        Args:
            source: Base list of CSS properties
            override: Properties to override/add
            
        Returns:
            Merged list of CSS properties
        """
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
        
        # Then apply overrides
        for prop in override:
            # Remove any conflicting properties
            affected = self.conflict_detector.get_affected_properties(prop.name)
            for affected_prop in affected:
                if affected_prop != prop.name and affected_prop in merged_props:
                    del merged_props[affected_prop]
            
            # Add the override property
            merged_props[prop.name] = prop
        
        # Return as a list maintaining order
        return list(merged_props.values())
    
    def merge(
        self,
        source: Union[Dict[str, str], List[CSSProperty], str],
        override: Union[Dict[str, str], List[CSSProperty], str]
    ) -> List[CSSProperty]:
        """
        Merge CSS properties from various input formats.
        
        Args:
            source: Base CSS properties (dict, list, or string)
            override: Override CSS properties (dict, list, or string)
            
        Returns:
            Merged list of CSS properties
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
        
        # Parse override into list of properties
        if isinstance(override, str):
            override_props = self.parser.parse_properties_string(override)
        elif isinstance(override, dict):
            override_props = self.parser.parse_properties_dict(override)
        elif isinstance(override, list):
            override_props = override
        else:
            override_props = []
        
        return self.merge_properties(source_props, override_props)
    
    def merge_rules(
        self,
        source_rule: CSSRule,
        override_properties: Union[Dict[str, str], List[CSSProperty], str]
    ) -> CSSRule:
        """
        Merge override properties into a CSS rule.
        
        Args:
            source_rule: Base CSS rule
            override_properties: Properties to override/add
            
        Returns:
            New CSS rule with merged properties
        """
        # Parse override properties
        if isinstance(override_properties, str):
            override_props = self.parser.parse_properties_string(override_properties)
        elif isinstance(override_properties, dict):
            override_props = self.parser.parse_properties_dict(override_properties)
        else:
            override_props = override_properties
        
        # Merge properties
        merged_props = self.merge_properties(source_rule.properties, override_props)
        
        # Create new rule with merged properties
        return CSSRule(selector=source_rule.selector, properties=merged_props)