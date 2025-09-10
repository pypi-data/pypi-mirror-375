"""Output formatting for CSS properties and rules."""

from typing import List, Dict, Any, Optional, Union
from csscade.models import CSSProperty, CSSRule


class OutputFormatter:
    """Formats CSS properties and rules for different output modes."""
    
    def __init__(
        self,
        indent: str = "  ",
        line_ending: str = "\n",
        compact: bool = False
    ):
        """
        Initialize the output formatter.
        
        Args:
            indent: Indentation string for formatted output
            line_ending: Line ending character(s)
            compact: Whether to use compact formatting
        """
        self.indent = indent if not compact else ""
        self.line_ending = line_ending if not compact else ""
        self.compact = compact
    
    def format_properties(
        self,
        properties: List[CSSProperty],
        format: str = "css"
    ) -> Union[str, Dict[str, str], List[Dict[str, Any]]]:
        """
        Format a list of CSS properties.
        
        Args:
            properties: List of CSS properties
            format: Output format ('css', 'dict', 'list')
            
        Returns:
            Formatted output based on format parameter
        """
        if format == "css":
            return self._format_as_css_string(properties)
        elif format == "dict":
            return self._format_as_dict(properties)
        elif format == "list":
            return self._format_as_list(properties)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def format_rule(
        self,
        rule: CSSRule,
        format: str = "css"
    ) -> Union[str, Dict[str, Any]]:
        """
        Format a CSS rule.
        
        Args:
            rule: CSS rule to format
            format: Output format ('css', 'dict')
            
        Returns:
            Formatted output based on format parameter
        """
        if format == "css":
            return self._format_rule_as_css(rule)
        elif format == "dict":
            return self._format_rule_as_dict(rule)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def format_stylesheet(
        self,
        rules: List[CSSRule],
        minify: bool = False
    ) -> str:
        """
        Format multiple CSS rules as a stylesheet.
        
        Args:
            rules: List of CSS rules
            minify: Whether to minify the output
            
        Returns:
            Formatted CSS stylesheet
        """
        if minify:
            # Save current settings
            old_compact = self.compact
            old_line_ending = self.line_ending
            old_indent = self.indent
            
            # Set minify settings
            self.compact = True
            self.line_ending = ""
            self.indent = ""
            
            # Format rules
            rule_strings = [self._format_rule_as_css(rule) for rule in rules]
            result = "".join(rule_strings)
            
            # Restore settings
            self.compact = old_compact
            self.line_ending = old_line_ending
            self.indent = old_indent
            
            return result
        else:
            rule_strings = [self._format_rule_as_css(rule) for rule in rules]
            return self.line_ending.join(rule_strings)
    
    def _format_as_css_string(self, properties: List[CSSProperty]) -> str:
        """
        Format properties as a CSS string.
        
        Args:
            properties: List of CSS properties
            
        Returns:
            CSS string representation
        """
        if not properties:
            return ""
        
        if self.compact:
            return " ".join(str(prop) + ";" for prop in properties)
        else:
            return "; ".join(str(prop) for prop in properties) + ";"
    
    def _format_as_dict(self, properties: List[CSSProperty]) -> Dict[str, str]:
        """
        Format properties as a dictionary.
        
        Args:
            properties: List of CSS properties
            
        Returns:
            Dictionary of property names to values
        """
        result = {}
        for prop in properties:
            if prop.important:
                result[prop.name] = f"{prop.value} !important"
            else:
                result[prop.name] = prop.value
        return result
    
    def _format_as_list(self, properties: List[CSSProperty]) -> List[Dict[str, Any]]:
        """
        Format properties as a list of dictionaries.
        
        Args:
            properties: List of CSS properties
            
        Returns:
            List of property dictionaries
        """
        return [prop.to_dict() for prop in properties]
    
    def _format_rule_as_css(self, rule: CSSRule) -> str:
        """
        Format a rule as CSS string.
        
        Args:
            rule: CSS rule
            
        Returns:
            CSS string representation
        """
        if not rule.properties:
            return f"{rule.selector} {'{}'}"
        
        if self.compact:
            props_str = " ".join(str(prop) + ";" for prop in rule.properties)
            return f"{rule.selector}{'{' + props_str + '}'}"
        else:
            props_lines = []
            for prop in rule.properties:
                props_lines.append(f"{self.indent}{prop};")
            
            props_str = self.line_ending.join(props_lines)
            return f"{rule.selector} {'{' + self.line_ending + props_str + self.line_ending + '}'}"
    
    def _format_rule_as_dict(self, rule: CSSRule) -> Dict[str, Any]:
        """
        Format a rule as dictionary.
        
        Args:
            rule: CSS rule
            
        Returns:
            Dictionary representation
        """
        return {
            "selector": rule.selector,
            "properties": self._format_as_dict(rule.properties)
        }
    
    def format_inline_styles(
        self,
        properties: Union[List[CSSProperty], Dict[str, str]]
    ) -> str:
        """
        Format properties as inline style attribute value.
        
        Args:
            properties: CSS properties
            
        Returns:
            String suitable for HTML style attribute
        """
        if isinstance(properties, dict):
            # Convert dict to properties list
            props = []
            for name, value in properties.items():
                if value.endswith(" !important"):
                    props.append(CSSProperty(name, value[:-11], important=True))
                else:
                    props.append(CSSProperty(name, value))
        else:
            props = properties
        
        # Format as inline styles (no line breaks, space after semicolon)
        if not props:
            return ""
        
        return " ".join(f"{prop};" for prop in props)
    
    def format_merge_result(
        self,
        css: Optional[str] = None,
        add_classes: Optional[List[str]] = None,
        remove_classes: Optional[List[str]] = None,
        preserve_classes: Optional[List[str]] = None,
        inline_styles: Optional[Dict[str, str]] = None,
        important_styles: Optional[Dict[str, str]] = None,
        warnings: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Format the complete merge result.
        
        Args:
            css: Generated CSS string
            add_classes: Classes to add
            remove_classes: Classes to remove
            preserve_classes: Classes to preserve
            inline_styles: Inline styles to apply
            important_styles: Important styles to apply
            warnings: Warning messages
            
        Returns:
            Formatted merge result dictionary
        """
        result = {}
        
        if css:
            result["css"] = css
        
        if add_classes:
            result["add"] = add_classes
        
        if remove_classes:
            result["remove"] = remove_classes
        
        if preserve_classes:
            result["preserve"] = preserve_classes
        
        if inline_styles:
            result["inline"] = inline_styles
        
        if important_styles:
            result["important"] = important_styles
        
        if warnings:
            result["warnings"] = warnings
        
        return result