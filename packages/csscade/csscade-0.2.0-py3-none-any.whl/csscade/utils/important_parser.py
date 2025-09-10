"""Utilities for parsing and handling !important declarations."""

from typing import Tuple, Dict, List
from csscade.models import CSSProperty


class ImportantParser:
    """Handles parsing and processing of !important declarations."""
    
    @staticmethod
    def parse_value_with_important(value: str) -> Tuple[str, bool]:
        """
        Parse a CSS value string to extract the value and !important flag.
        
        Args:
            value: CSS value string (e.g., "blue !important" or "10px")
            
        Returns:
            Tuple of (clean_value, is_important)
        """
        if not value:
            return value, False
        
        value = value.strip()
        
        # Check if value ends with !important
        if value.endswith('!important'):
            # Remove !important and clean up
            clean_value = value[:-10].strip()  # -10 for '!important'
            return clean_value, True
        
        # Also check for ! important (with space)
        if value.endswith('! important'):
            clean_value = value[:-11].strip()  # -11 for '! important'
            return clean_value, True
            
        return value, False
    
    @staticmethod
    def parse_overrides_dict(overrides: Dict[str, str]) -> Dict[str, Tuple[str, bool]]:
        """
        Parse a dictionary of overrides to extract !important flags.
        
        Args:
            overrides: Dictionary of property: value pairs
            
        Returns:
            Dictionary of property: (clean_value, is_important) pairs
        """
        parsed = {}
        for prop, value in overrides.items():
            clean_value, is_important = ImportantParser.parse_value_with_important(value)
            parsed[prop] = (clean_value, is_important)
        return parsed
    
    @staticmethod
    def apply_important_strategy(
        original_prop: CSSProperty,
        override_value: str,
        override_important: bool,
        strategy: str = 'match'
    ) -> Tuple[str, bool, str]:
        """
        Apply !important conflict resolution strategy.
        
        Args:
            original_prop: Original CSS property
            override_value: Override value (without !important)
            override_important: Whether override explicitly has !important
            strategy: Conflict resolution strategy
            
        Returns:
            Tuple of (final_value, should_be_important, info_message)
        """
        info_message = None
        
        if strategy == 'respect':
            # Never override !important properties
            if original_prop.important:
                return original_prop.value, True, "Property has !important and 'respect' mode is active"
            return override_value, override_important, None
            
        elif strategy == 'override':
            # Override but don't add !important unless explicit
            if original_prop.important and not override_important:
                info_message = f"Property '{original_prop.name}' had !important but override doesn't - may not apply"
            return override_value, override_important, info_message
            
        elif strategy == 'match':
            # Default: Match the original's !important status
            if override_important:
                # Explicit !important in override takes precedence
                return override_value, True, None
            elif original_prop.important:
                # Match the original's !important
                info_message = f"Property '{original_prop.name}' marked !important to match original"
                return override_value, True, info_message
            else:
                return override_value, False, None
                
        elif strategy == 'force':
            # Always add !important to overrides
            if not override_important and not original_prop.important:
                info_message = "Force mode: Adding !important to override"
            return override_value, True, info_message
            
        elif strategy == 'strip':
            # Remove all !important declarations
            if original_prop.important or override_important:
                info_message = "Strip mode: Removing !important declaration"
            return override_value, False, info_message
            
        else:
            # Unknown strategy, default to match
            return ImportantParser.apply_important_strategy(
                original_prop, override_value, override_important, 'match'
            )[0:3]
    
    @staticmethod
    def process_property_with_strategy(
        property_name: str,
        override_value: str, 
        override_important: bool,
        original_props: List[CSSProperty],
        strategy: str = 'match'
    ) -> Tuple[CSSProperty, str]:
        """
        Process a single property override with the given strategy.
        
        Args:
            property_name: Name of the property
            override_value: Override value (without !important)
            override_important: Whether override has explicit !important
            original_props: List of original properties
            strategy: Conflict resolution strategy
            
        Returns:
            Tuple of (resulting_property, info_message)
        """
        # Find original property if it exists
        original = None
        for prop in original_props:
            if prop.name == property_name:
                original = prop
                break
        
        if original:
            # Apply strategy to existing property
            final_value, should_be_important, info = ImportantParser.apply_important_strategy(
                original, override_value, override_important, strategy
            )
        else:
            # New property
            if strategy == 'force':
                final_value, should_be_important = override_value, True
                info = "Force mode: Adding !important to new property" if not override_important else None
            elif strategy == 'strip':
                final_value, should_be_important = override_value, False
                info = "Strip mode: Removing !important from new property" if override_important else None
            else:
                # For new properties, use explicit !important if provided
                final_value, should_be_important = override_value, override_important
                info = None
        
        return CSSProperty(property_name, final_value, should_be_important), info