"""Permanent merge strategy that modifies original classes."""

from typing import Dict, Any, Union, List
from csscade.strategies.base import MergeStrategy
from csscade.models import CSSProperty, CSSRule
from csscade.property_merger import PropertyMerger
from csscade.parser.css_parser import CSSParser
from csscade.generator.output import OutputFormatter


class PermanentMergeStrategy(MergeStrategy):
    """
    Permanent merge strategy that modifies the original CSS class directly.
    This strategy overwrites properties in the source with override values.
    """
    
    def __init__(self, conflict_resolution=None, naming=None):
        """
        Initialize the permanent merge strategy.
        
        Args:
            conflict_resolution: Optional conflict resolution configuration
            naming: Optional naming configuration (not used in permanent mode)
        """
        super().__init__(conflict_resolution, naming)
        self.merger = PropertyMerger()
        self.parser = CSSParser()
        self.formatter = OutputFormatter()
        # Note: permanent mode doesn't generate new class names
    
    def merge(
        self,
        source: Union[str, CSSRule, Dict[str, str], List[CSSProperty]],
        override: Union[Dict[str, str], List[CSSProperty], str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Merge CSS properties by permanently modifying the original class.
        
        Args:
            source: Source CSS (can be rule, properties, or string)
            override: Override properties
            **kwargs: Additional parameters (unused in this strategy)
            
        Returns:
            Dictionary with:
                - css: Modified CSS with original selector
                - inline: None (no inline styles needed)
                - important: None (no important styles needed)
        """
        self.validate_input(source, override)
        
        # Parse source to determine type
        if isinstance(source, CSSRule):
            # Source is already a rule
            source_rule = source
        elif isinstance(source, str) and '{' in source:
            # Source is a CSS rule string
            rules = self.parser.parse_rule_string(source)
            if not rules:
                raise ValueError("No valid CSS rule found in source")
            source_rule = rules[0]
        else:
            # Source is properties only, need a selector
            selector = kwargs.get('selector', '.default')
            if isinstance(source, str):
                props = self.parser.parse_properties_string(source)
            elif isinstance(source, dict):
                props = self.parser.parse_properties_dict(source)
            else:
                props = source
            source_rule = CSSRule(selector=selector, properties=props)
        
        # Merge properties
        merged_rule = self.merger.merge_rules(source_rule, override)
        
        # Format the output
        css_output = self.formatter.format_rule(merged_rule, format="css")
        
        return self.prepare_result(
            css=css_output,
            inline_styles=None,
            important_styles=None
        )
    
    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        return "permanent"