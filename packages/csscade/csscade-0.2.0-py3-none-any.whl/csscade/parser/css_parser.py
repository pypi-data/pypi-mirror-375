"""CSS parsing functionality using cssutils."""

import cssutils
from typing import List, Dict, Any, Union, Optional
from csscade.models import CSSProperty, CSSRule
from csscade.utils.exceptions import CSSParseError

# Configure cssutils to be less verbose
cssutils.log.setLevel(100)  # Suppress warnings


class CSSParser:
    """Parser for CSS strings and dictionaries."""
    
    def __init__(self) -> None:
        """Initialize the CSS parser."""
        self.parser = cssutils.CSSParser()
    
    def parse_properties_string(self, css_string: str) -> List[CSSProperty]:
        """
        Parse a CSS properties string to a list of CSSProperty objects.
        
        Args:
            css_string: CSS properties string (e.g., "color: red; padding: 10px;")
        
        Returns:
            List of CSSProperty objects
        
        Raises:
            CSSParseError: If the CSS string cannot be parsed
        """
        try:
            # Parse as a style declaration (properties only)
            style = cssutils.parseStyle(css_string)
            properties = []
            
            for prop in style:
                # Check if property has !important
                important = prop.priority == "important"
                properties.append(
                    CSSProperty(
                        name=prop.name,
                        value=prop.value,
                        important=important
                    )
                )
            
            return properties
        except Exception as e:
            raise CSSParseError(f"Failed to parse CSS properties: {e}")
    
    def parse_properties_dict(self, properties_dict: Dict[str, str]) -> List[CSSProperty]:
        """
        Parse a dictionary of CSS properties to a list of CSSProperty objects.
        
        Args:
            properties_dict: Dictionary mapping property names to values
        
        Returns:
            List of CSSProperty objects
        """
        properties = []
        
        for name, value in properties_dict.items():
            # Check if value contains !important
            important = False
            if isinstance(value, str) and value.strip().endswith("!important"):
                important = True
                # Remove !important from value
                value = value.replace("!important", "").strip()
            
            properties.append(
                CSSProperty(name=name, value=value, important=important)
            )
        
        return properties
    
    def parse_rule_string(self, css_string: str) -> List[CSSRule]:
        """
        Parse a CSS rule string to CSSRule objects.
        
        Args:
            css_string: CSS rule string (e.g., ".btn { color: red; }")
        
        Returns:
            List of CSSRule objects
        
        Raises:
            CSSParseError: If the CSS string cannot be parsed
        """
        try:
            # Parse the CSS string as a stylesheet
            sheet = cssutils.parseString(css_string)
            rules = []
            
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    # Get the selector text
                    selector = rule.selectorText
                    
                    # Parse properties
                    properties = []
                    for prop in rule.style:
                        important = prop.priority == "important"
                        properties.append(
                            CSSProperty(
                                name=prop.name,
                                value=prop.value,
                                important=important
                            )
                        )
                    
                    rules.append(CSSRule(selector=selector, properties=properties))
            
            return rules
        except Exception as e:
            raise CSSParseError(f"Failed to parse CSS rules: {e}")
    
    def parse(self, css_input: Union[str, Dict[str, str]]) -> Union[List[CSSProperty], List[CSSRule]]:
        """
        Parse CSS input (string or dict) to appropriate data structures.
        
        Args:
            css_input: CSS string or dictionary of properties
        
        Returns:
            List of CSSProperty or CSSRule objects
        
        Raises:
            CSSParseError: If the input cannot be parsed
        """
        if isinstance(css_input, dict):
            return self.parse_properties_dict(css_input)
        elif isinstance(css_input, str):
            # Try to determine if it's a rule or just properties
            css_input = css_input.strip()
            
            # If it contains a selector (has curly braces), parse as rule
            if "{" in css_input and "}" in css_input:
                return self.parse_rule_string(css_input)
            else:
                # Parse as properties only
                return self.parse_properties_string(css_input)
        else:
            raise CSSParseError(f"Invalid input type: {type(css_input)}")
    
    def properties_to_css_string(self, properties: List[CSSProperty]) -> str:
        """
        Convert a list of CSSProperty objects to a CSS string.
        
        Args:
            properties: List of CSSProperty objects
        
        Returns:
            CSS properties string
        """
        if not properties:
            return ""
        
        return "; ".join(str(prop) for prop in properties) + ";"
    
    def properties_to_dict(self, properties: List[CSSProperty]) -> Dict[str, str]:
        """
        Convert a list of CSSProperty objects to a dictionary.
        
        Args:
            properties: List of CSSProperty objects
        
        Returns:
            Dictionary mapping property names to values
        """
        result = {}
        for prop in properties:
            value = prop.value
            if prop.important:
                value += " !important"
            result[prop.name] = value
        return result
    
    def rule_to_css_string(self, rule: CSSRule) -> str:
        """
        Convert a CSSRule object to a CSS string.
        
        Args:
            rule: CSSRule object
        
        Returns:
            CSS rule string
        """
        return str(rule)
    
    def validate_property_name(self, property_name: str) -> bool:
        """
        Validate if a property name is a valid CSS property.
        
        Args:
            property_name: CSS property name to validate
        
        Returns:
            True if valid, False otherwise
        """
        # Common CSS properties list (can be extended)
        # Since cssutils accepts any property name, we need a manual list
        valid_properties = {
            # Layout
            "display", "position", "top", "right", "bottom", "left", "float", "clear",
            "z-index", "overflow", "overflow-x", "overflow-y", "visibility",
            
            # Box model
            "width", "height", "max-width", "max-height", "min-width", "min-height",
            "margin", "margin-top", "margin-right", "margin-bottom", "margin-left",
            "padding", "padding-top", "padding-right", "padding-bottom", "padding-left",
            "border", "border-top", "border-right", "border-bottom", "border-left",
            "border-width", "border-style", "border-color", "border-radius",
            
            # Typography
            "color", "font", "font-family", "font-size", "font-weight", "font-style",
            "line-height", "text-align", "text-decoration", "text-transform",
            "letter-spacing", "word-spacing", "white-space",
            
            # Background
            "background", "background-color", "background-image", "background-repeat",
            "background-position", "background-size", "background-attachment",
            
            # Flexbox
            "flex", "flex-direction", "flex-wrap", "justify-content", "align-items",
            "align-content", "flex-grow", "flex-shrink", "flex-basis", "order",
            
            # Grid
            "grid", "grid-template", "grid-template-columns", "grid-template-rows",
            "grid-gap", "grid-column", "grid-row",
            
            # Transform and animation
            "transform", "transition", "animation", "opacity",
            
            # Other common properties
            "box-shadow", "text-shadow", "cursor", "pointer-events", "user-select"
        }
        
        # Check if it's a valid property or a vendor-prefixed property
        if property_name in valid_properties:
            return True
        
        # Check for vendor prefixes
        if property_name.startswith(("-webkit-", "-moz-", "-ms-", "-o-")):
            # Remove prefix and check if base property is valid
            base_property = property_name.split("-", 2)[2] if "-" in property_name[1:] else ""
            return base_property in valid_properties
        
        return False
    
    def validate_css_string(self, css_string: str) -> bool:
        """
        Validate if a CSS string is syntactically correct.
        
        Args:
            css_string: CSS string to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Try parsing as a stylesheet first
            if "{" in css_string and "}" in css_string:
                sheet = cssutils.parseString(css_string)
                # Check if any valid rules were parsed
                return len(list(sheet)) > 0
            else:
                # Try parsing as style properties
                style = cssutils.parseStyle(css_string)
                # Check if the style is valid by seeing if it parses anything
                # or if it's empty (which is also valid)
                return css_string.strip() == "" or len(list(style)) > 0 or ":" in css_string
        except:
            return False