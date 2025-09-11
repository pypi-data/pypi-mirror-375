"""Base strategy class for CSS merging strategies."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Union, List, Optional
from csscade.models import CSSProperty, CSSRule
from csscade.validation.syntax_validator import CSSValidator


class MergeStrategy(ABC):
    """Abstract base class for CSS merge strategies."""
    
    def __init__(
        self, 
        conflict_resolution: Optional[Dict[str, Any]] = None,
        naming: Optional[Dict[str, Any]] = None,
        rule_selection: str = 'first',
        validation: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the merge strategy.
        
        Args:
            conflict_resolution: Conflict resolution configuration
            naming: Naming configuration for class generation
            rule_selection: Rule selection mode ('first' or 'all')
            validation: Validation configuration
        """
        self.conflict_resolution = conflict_resolution or {}
        self.naming = naming or {}
        self.rule_selection = rule_selection
        
        # Setup validation
        self.validation_config = validation or {}
        self.validator = None
        if self.validation_config.get('enabled', False):
            strict = self.validation_config.get('strict', False)
            self.validator = CSSValidator(strict=strict)
    
    @abstractmethod
    def merge(
        self,
        source: Union[str, CSSRule, Dict[str, str], List[CSSProperty]],
        override: Union[Dict[str, str], List[CSSProperty], str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Merge CSS properties according to the strategy.
        
        Args:
            source: Source CSS (can be rule, properties, or string)
            override: Override properties
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            Dictionary with merge results including:
                - css: Generated CSS string (optional)
                - add: Classes to add (optional)
                - remove: Classes to remove (optional)
                - preserve: Classes to preserve (optional)
                - inline: Inline styles to apply (optional)
                - important: Important styles to apply (optional)
                - warnings: Warning messages (optional)
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        Get the name of this strategy.
        
        Returns:
            Strategy name
        """
        pass
    
    def validate_properties(self, properties: Union[Dict[str, str], List[CSSProperty]]) -> List[str]:
        """
        Validate CSS properties and return warnings.
        
        Args:
            properties: Properties to validate
            
        Returns:
            List of warning messages
        """
        warnings = []
        
        if not self.validator:
            return warnings
            
        # Clear previous warnings
        self.validator.warnings = []
        
        # Convert to dict if needed
        if isinstance(properties, list):
            prop_dict = {prop.name: prop.value for prop in properties}
        else:
            prop_dict = properties
        
        # Check each property
        for prop_name, prop_value in prop_dict.items():
            # Check property name
            if self.validation_config.get('check_properties', True):
                # Skip vendor prefixes if allowed
                if prop_name.startswith(('-webkit-', '-moz-', '-ms-', '-o-')):
                    if not self.validation_config.get('allow_vendor', True):
                        warnings.append(f"Vendor prefix not allowed: '{prop_name}'")
                # Skip custom properties if allowed
                elif prop_name.startswith('--'):
                    if not self.validation_config.get('allow_custom', True):
                        warnings.append(f"Custom property not allowed: '{prop_name}'")
                else:
                    # Validate standard property
                    self.validator.validate_property_name(prop_name)
            
            # Check property value (if enabled)
            if self.validation_config.get('check_values', False):
                # Basic value validation for colors
                if 'color' in prop_name or prop_name in ['background', 'border']:
                    # Extract color value (simplified)
                    color_val = prop_value.split()[0] if ' ' in prop_value else prop_value
                    if not self.validator.validate_color_value(color_val):
                        # Don't warn for potential CSS variables
                        if not color_val.startswith('var('):
                            warnings.append(f"Invalid color value for '{prop_name}': '{color_val}'")
        
        # Add validator warnings
        warnings.extend(self.validator.warnings)
        
        # Check for duplicates
        if self.validation_config.get('check_duplicates', True):
            seen = set()
            for prop_name in prop_dict.keys():
                base_name = prop_name.split('-')[0] if '-' in prop_name else prop_name
                if base_name in seen and base_name in ['margin', 'padding', 'border']:
                    warnings.append(f"Potential duplicate/conflicting property: '{prop_name}' (base: '{base_name}')")
                seen.add(base_name)
        
        return warnings
    
    def validate_input(
        self,
        source: Any,
        override: Any
    ) -> bool:
        """
        Validate input parameters.
        
        Args:
            source: Source input
            override: Override input
            
        Returns:
            True if valid, raises exception otherwise
        """
        if source is None:
            raise ValueError("Source cannot be None")
        if override is None:
            raise ValueError("Override cannot be None")
        return True
    
    def prepare_result(
        self,
        css: Optional[Union[str, List[str]]] = None,
        add_classes: Optional[List[str]] = None,
        remove_classes: Optional[List[str]] = None,
        preserve_classes: Optional[List[str]] = None,
        inline_styles: Optional[Dict[str, str]] = None,
        important_styles: Optional[Dict[str, str]] = None,
        warnings: Optional[List[str]] = None,
        info: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Prepare the result dictionary.
        
        Args:
            css: Generated CSS (string or list of strings)
            add_classes: Classes to add
            remove_classes: Classes to remove
            preserve_classes: Classes to preserve
            inline_styles: Inline styles
            important_styles: Important styles
            warnings: Warning messages
            info: Informational messages
            
        Returns:
            Formatted result dictionary
        """
        result = {}
        
        # Ensure css is always a list for consistency
        if css is not None:
            if isinstance(css, str):
                result["css"] = [css] if css else []
            else:
                result["css"] = css
        else:
            result["css"] = []
        
        # Lists that can be empty or have content
        result["add"] = add_classes if add_classes else []
        result["remove"] = remove_classes if remove_classes else []
        result["preserve"] = preserve_classes if preserve_classes else []
        
        # Always include warnings and info (empty lists if none)
        result["warnings"] = warnings if warnings else []
        result["info"] = info if info else []
        
        # Optional dictionaries
        if inline_styles:
            result["inline"] = inline_styles
        if important_styles:
            result["important"] = important_styles
            
        return result