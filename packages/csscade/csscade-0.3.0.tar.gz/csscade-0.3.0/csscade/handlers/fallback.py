"""Fallback handlers for complex CSS selectors."""

from typing import Dict, List, Any, Optional, Union
from csscade.models import CSSProperty
from csscade.handlers.selector_parser import SelectorParser, SelectorType
from csscade.generator.output import OutputFormatter


class FallbackHandler:
    """Handles fallback strategies for non-mergeable selectors."""
    
    def __init__(self):
        """Initialize the fallback handler."""
        self.selector_parser = SelectorParser()
        self.formatter = OutputFormatter()
    
    def handle_complex_selector(
        self,
        selector: str,
        properties: Union[List[CSSProperty], Dict[str, str]],
        strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle complex selectors that can't be merged normally.
        
        Args:
            selector: CSS selector string
            properties: CSS properties to apply
            strategy: Optional override strategy ('inline', 'important', 'preserve')
            
        Returns:
            Dictionary with fallback solution:
                - css: Generated CSS (if preserving)
                - inline: Inline styles to apply
                - important: Important styles to apply
                - warnings: Warning messages
        """
        # Parse the selector
        parse_result = self.selector_parser.parse(selector)
        
        # Determine fallback strategy
        if strategy:
            fallback_strategy = strategy
        else:
            fallback_strategy = parse_result.get('fallback', 'inline')
        
        # Convert properties to dict if needed
        if isinstance(properties, list):
            prop_dict = {prop.name: prop.value for prop in properties}
        else:
            prop_dict = properties
        
        # Apply the appropriate fallback strategy
        if fallback_strategy == 'inline':
            return self._handle_inline_fallback(selector, prop_dict, parse_result)
        elif fallback_strategy == 'important':
            return self._handle_important_fallback(selector, prop_dict, parse_result)
        elif fallback_strategy == 'preserve':
            return self._handle_preserve_fallback(selector, prop_dict, parse_result)
        else:
            # Default to inline
            return self._handle_inline_fallback(selector, prop_dict, parse_result)
    
    def _handle_inline_fallback(
        self,
        selector: str,
        properties: Dict[str, str],
        parse_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle fallback using inline styles.
        
        Args:
            selector: Original selector
            properties: Properties to apply
            parse_result: Parsed selector information
            
        Returns:
            Result with inline styles and warnings
        """
        warnings = []
        
        # Generate warning based on selector type
        if parse_result['type'] == SelectorType.PSEUDO:
            warnings.append(
                f"Cannot override {parse_result.get('pseudo', 'pseudo-class')} "
                f"with class merge, using inline styles instead"
            )
        elif parse_result['type'] == SelectorType.COMPLEX:
            warnings.append(
                f"Complex selector '{selector}' cannot be merged, "
                f"using inline styles instead"
            )
        elif parse_result['type'] == SelectorType.ATTRIBUTE:
            warnings.append(
                f"Attribute selector '{selector}' cannot be merged, "
                f"using inline styles instead"
            )
        else:
            warnings.append(
                f"Selector '{selector}' cannot be merged, "
                f"using inline styles instead"
            )
        
        return {
            'css': None,
            'inline': properties,
            'warnings': warnings
        }
    
    def _handle_important_fallback(
        self,
        selector: str,
        properties: Dict[str, str],
        parse_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle fallback using !important inline styles.
        
        Args:
            selector: Original selector
            properties: Properties to apply
            parse_result: Parsed selector information
            
        Returns:
            Result with important styles and warnings
        """
        warnings = []
        
        # Check if original has !important
        has_important = any('!important' in str(v) for v in properties.values())
        
        if has_important:
            warnings.append(
                f"Original selector '{selector}' has !important, "
                f"inline override may not work without !important"
            )
        
        # Add warning about using !important
        warnings.append(
            f"Using !important inline styles to override '{selector}'"
        )
        
        # Create important properties
        important_props = {}
        for name, value in properties.items():
            # Remove existing !important if present
            clean_value = value.replace('!important', '').strip()
            important_props[name] = clean_value
        
        return {
            'css': None,
            'inline': None,
            'important': important_props,
            'warnings': warnings
        }
    
    def _handle_preserve_fallback(
        self,
        selector: str,
        properties: Dict[str, str],
        parse_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle fallback by preserving the original selector.
        
        Args:
            selector: Original selector
            properties: Properties to apply
            parse_result: Parsed selector information
            
        Returns:
            Result with preserved CSS and warnings
        """
        warnings = []
        
        # Generate CSS with the original selector
        from csscade.models import CSSRule, CSSProperty
        
        css_properties = []
        for name, value in properties.items():
            # Check for !important
            if '!important' in value:
                clean_value = value.replace('!important', '').strip()
                css_properties.append(CSSProperty(name, clean_value, important=True))
            else:
                css_properties.append(CSSProperty(name, value))
        
        rule = CSSRule(selector, css_properties)
        css_output = self.formatter.format_rule(rule, format="css")
        
        # Add appropriate warning
        if parse_result['type'] == SelectorType.MEDIA:
            warnings.append(
                f"Media query preserved: Override applies to all breakpoints"
            )
        elif parse_result['type'] == SelectorType.KEYFRAMES:
            warnings.append(
                f"Keyframes preserved: Override modifies animation"
            )
        else:
            warnings.append(
                f"Selector '{selector}' preserved with overrides"
            )
        
        return {
            'css': css_output,
            'inline': None,
            'warnings': warnings
        }
    
    def determine_best_fallback(
        self,
        selector: str,
        has_important: bool = False,
        context: Optional[str] = None
    ) -> str:
        """
        Determine the best fallback strategy for a selector.
        
        Args:
            selector: CSS selector
            has_important: Whether properties have !important
            context: Optional context ('component', 'permanent', 'replace')
            
        Returns:
            Best fallback strategy name
        """
        parse_result = self.selector_parser.parse(selector)
        selector_type = parse_result['type']
        
        # Media queries and keyframes should always be preserved
        if selector_type in [SelectorType.MEDIA, SelectorType.KEYFRAMES]:
            return 'preserve'
        
        # If original has !important, we might need !important to override
        if has_important:
            return 'important'
        
        # Pseudo-classes typically need inline styles
        if selector_type == SelectorType.PSEUDO:
            # Some pseudo-classes might work with preserve
            pseudo = parse_result.get('pseudo', '')
            if pseudo in [':root', ':first-child', ':last-child']:
                return 'preserve'
            return 'inline'
        
        # Complex selectors usually need inline
        if selector_type == SelectorType.COMPLEX:
            # In component mode, might preserve the complex selector
            if context == 'component':
                return 'preserve'
            return 'inline'
        
        # Default to inline for safety
        return 'inline'
    
    def generate_fallback_warning(
        self,
        selector: str,
        strategy: str,
        reason: Optional[str] = None
    ) -> str:
        """
        Generate a helpful warning message for fallback.
        
        Args:
            selector: CSS selector
            strategy: Fallback strategy used
            reason: Optional specific reason
            
        Returns:
            Warning message string
        """
        parse_result = self.selector_parser.parse(selector)
        selector_type = parse_result['type']
        
        if reason:
            return reason
        
        if selector_type == SelectorType.PSEUDO:
            pseudo = parse_result.get('pseudo', 'pseudo-selector')
            return (f"Cannot merge {pseudo} selector with class override. "
                   f"Using {strategy} fallback strategy.")
        
        if selector_type == SelectorType.COMPLEX:
            return (f"Complex selector '{selector}' requires {strategy} fallback. "
                   f"Consider simplifying selector structure if possible.")
        
        if selector_type == SelectorType.MEDIA:
            return (f"Media query will be preserved. "
                   f"Override will apply to all matching breakpoints.")
        
        if selector_type == SelectorType.ATTRIBUTE:
            return (f"Attribute selector '{selector}' cannot be merged. "
                   f"Using {strategy} fallback.")
        
        return (f"Selector '{selector}' requires {strategy} fallback strategy.")
    
    def can_use_class_override(self, selector: str) -> bool:
        """
        Check if a selector can use class override strategy.
        
        Args:
            selector: CSS selector
            
        Returns:
            True if class override is possible, False otherwise
        """
        return self.selector_parser.can_merge(selector)