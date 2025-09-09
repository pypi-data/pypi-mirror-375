"""Replace merge strategy that creates complete replacement classes."""

from typing import Dict, Any, Union, List, Optional
from csscade.strategies.base import MergeStrategy
from csscade.models import CSSProperty, CSSRule
from csscade.property_merger import PropertyMerger
from csscade.parser.css_parser import CSSParser
from csscade.generator.output import OutputFormatter
from csscade.generator.naming import ClassNameGenerator
from csscade.handlers.selector_utils import (
    split_pseudo_selector, 
    rebuild_selector_with_base,
    clone_rule_with_new_selector
)


class ReplaceMergeStrategy(MergeStrategy):
    """
    Replace merge strategy that creates a complete replacement class.
    This strategy creates a new class with all non-conflicting properties
    from the source plus the override properties.
    """
    
    def __init__(self, conflict_resolution=None, naming=None):
        """
        Initialize the replace merge strategy.
        
        Args:
            conflict_resolution: Optional conflict resolution configuration
            naming: Optional naming configuration
        """
        super().__init__(conflict_resolution, naming)
        self.merger = PropertyMerger()
        self.parser = CSSParser()
        self.formatter = OutputFormatter()
        
        # Use naming config if provided
        naming_config = naming or {}
        self.name_generator = ClassNameGenerator(
            strategy=naming_config.get('strategy', 'hash'),
            prefix=naming_config.get('prefix', 'css-'),
            suffix=naming_config.get('suffix', ''),
            hash_length=naming_config.get('hash_length', 8)
        )
    
    def merge(
        self,
        source: Union[str, CSSRule, Dict[str, str], List[CSSProperty]],
        override: Union[Dict[str, str], List[CSSProperty], str],
        component_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Merge CSS properties by creating a complete replacement class.
        
        Args:
            source: Source CSS (can be rule, properties, or string)
            override: Override properties
            component_id: Optional component ID for unique class naming
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with:
                - css: New replacement class with all merged properties
                - add: List of classes to add (the new replacement class)
                - remove: List of classes to remove (original class)
                - inline: None (no inline styles needed)
        """
        self.validate_input(source, override)
        
        # Parse source to determine type
        if isinstance(source, CSSRule):
            source_rule = source
        elif isinstance(source, str) and '{' in source:
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
        
        # Check if selector has pseudo-class/element
        base_selector, pseudo_part = split_pseudo_selector(source_rule.selector)
        
        # Merge all properties
        merged_rule = self.merger.merge_rules(source_rule, override)
        
        # Generate replacement class name
        replacement_class_name = self.name_generator.generate_for_mode(
            mode="replace",
            base_selector=base_selector,
            properties=merged_rule.properties,
            component_id=component_id
        )
        
        # Remove leading . or # from class name for clean output
        clean_class_name = replacement_class_name.lstrip('.#')
        
        css_rules = []
        warnings = []
        
        if pseudo_part:
            # Handle pseudo selector case - need to create both base and pseudo rules
            
            # 1. Create base rule (empty for now, would copy from original base if found)
            base_rule = CSSRule(
                selector=replacement_class_name,
                properties=[]  # Would copy from original base rule if found
            )
            css_rules.append(self.formatter.format_rule(base_rule, format="css"))
            
            # Add comprehensive warning about empty base rule
            warnings.append(
                f"Base rule {replacement_class_name} created empty. The base rule is empty because we need access to " +
                f"the original {base_selector} rule (without {pseudo_part}) to clone its properties. " +
                f"In a production system, you should: " +
                f"1) Parse all CSS rules at once, " +
                f"2) Find related rules ({base_selector}, {base_selector}:hover, {base_selector}:focus, etc.), " +
                f"3) Clone all related rules with the new base class name. " +
                f"For now, provide base styles separately or ensure your CSS includes the base rule."
            )
            
            # 2. Create pseudo rule with merged properties
            pseudo_selector = rebuild_selector_with_base(replacement_class_name, pseudo_part)
            pseudo_rule = CSSRule(
                selector=pseudo_selector,
                properties=merged_rule.properties
            )
            css_rules.append(self.formatter.format_rule(pseudo_rule, format="css"))
        else:
            # Regular selector without pseudo - original behavior
            replacement_rule = CSSRule(
                selector=replacement_class_name,
                properties=merged_rule.properties
            )
            css_rules.append(self.formatter.format_rule(replacement_rule, format="css"))
        
        # Format the output
        css_output = "\n".join(css_rules) if css_rules else None
        
        result = self.prepare_result(
            css=css_output,
            add_classes=[clean_class_name],  # Use clean class name
            remove_classes=[base_selector.lstrip('.#')],  # Remove original base selector
            inline_styles=None
        )
        
        # Add warnings if any
        if warnings:
            result["warnings"] = warnings
            
        return result
    
    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        return "replace"