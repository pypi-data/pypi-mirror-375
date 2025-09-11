"""Replace merge strategy that creates complete replacement classes."""

from typing import Dict, Any, Union, List, Optional
from csscade.strategies.base import MergeStrategy
from csscade.models import CSSProperty, CSSRule
from csscade.property_merger import PropertyMerger
from csscade.parser.css_parser import CSSParser
from csscade.generator.output import OutputFormatter
from csscade.generator.naming import ClassNameGenerator
from csscade.utils.rule_matcher import RuleMatcher
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
    
    def __init__(self, conflict_resolution=None, naming=None, rule_selection='first', shorthand_strategy='cascade', validation=None):
        """
        Initialize the replace merge strategy.
        
        Args:
            conflict_resolution: Optional conflict resolution configuration
            naming: Optional naming configuration
            rule_selection: Rule selection mode ('first' or 'all')
            shorthand_strategy: Shorthand handling strategy ('cascade', 'smart', 'expand')
            validation: Validation configuration
        """
        super().__init__(conflict_resolution, naming, rule_selection, validation)
        # Initialize PropertyMerger with important and shorthand strategies
        important_strategy = conflict_resolution.get('important', 'match') if conflict_resolution else 'match'
        self.merger = PropertyMerger(important_strategy=important_strategy, shorthand_strategy=shorthand_strategy)
        self.parser = CSSParser()
        self.formatter = OutputFormatter()
        self.rule_matcher = RuleMatcher()
        
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
        apply_to: Union[str, List[str]] = 'all',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Merge CSS properties by creating a complete replacement class.
        
        Args:
            source: Source CSS (can be rule, properties, or string)
            override: Override properties
            component_id: Optional component ID for unique class naming
            apply_to: Which rules to apply overrides to
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with:
                - css: List of CSS strings for the replacement class
                - add: List containing the new replacement class name
                - remove: List containing original class name to remove
                - preserve: Empty list
                - warnings: List of warnings
                - info: List of info messages
        """
        self.validate_input(source, override)
        
        # Parse source to determine type
        rules_to_process = []
        
        if isinstance(source, CSSRule):
            rules_to_process = [source]
        elif isinstance(source, str) and '{' in source:
            all_rules = self.parser.parse_rule_string(source)
            if not all_rules:
                raise ValueError("No valid CSS rule found in source")
            
            # Select rules based on rule_selection parameter
            if self.rule_selection == 'first':
                rules_to_process = [all_rules[0]]
            else:  # 'all'
                rules_to_process = all_rules
        else:
            # Source is properties only, need a selector
            selector = kwargs.get('selector', '.default')
            if isinstance(source, str):
                props = self.parser.parse_properties_string(source)
            elif isinstance(source, dict):
                props = self.parser.parse_properties_dict(source)
            else:
                props = source
            rules_to_process = [CSSRule(selector=selector, properties=props)]
        
        # Parse override properties once
        if isinstance(override, str):
            override_props = self.parser.parse_properties_string(override)
        elif isinstance(override, dict):
            override_props = self.parser.parse_properties_dict(override)
        else:
            override_props = override
        
        # Group rules by base selector for replace mode
        # We create ONE replacement class per base selector group
        base_groups = self.rule_matcher.group_related_rules(rules_to_process)
        
        css_outputs = []
        warnings = []
        info = []
        add_classes = []
        remove_classes = []
        
        for base_selector, related_rules in base_groups.items():
            # Generate new class name for this replacement
            new_class_name = self.name_generator.generate_for_mode(
                mode="replace",
                base_selector=base_selector,
                properties=override_props,
                component_id=component_id
            )
            
            # Clean class names for output
            clean_class_name = new_class_name.lstrip('.#')
            add_classes.append(clean_class_name)
            remove_classes.append(base_selector.lstrip('.#'))
            
            # Check if we have a base rule (no pseudo-selectors)
            base_rule = None
            pseudo_rules = []
            
            for rule in related_rules:
                if ':' not in rule.selector:
                    base_rule = rule
                else:
                    pseudo_rules.append(rule)
            
            # If no base rule exists, create an empty one with warning
            if not base_rule:
                warnings.append(f"No base rule found for {base_selector}. Creating empty base class.")
                base_rule = CSSRule(selector=base_selector, properties=[])
            
            # Process base rule
            if self.rule_matcher.should_apply_override(base_rule.selector, apply_to):
                # Merge base properties with overrides
                merged_props, merge_info, merge_warnings = self.merger.merge(base_rule.properties, override_props)
                replacement_base_rule = CSSRule(selector=new_class_name, properties=merged_props)
                css_outputs.append(self.formatter.format_rule(replacement_base_rule, format="css"))
                info.append(f"Created replacement class {new_class_name} with merged properties")
                info.extend(merge_info)
                warnings.extend(merge_warnings)
            else:
                # Create base replacement class with original properties only
                replacement_base_rule = CSSRule(selector=new_class_name, properties=base_rule.properties)
                css_outputs.append(self.formatter.format_rule(replacement_base_rule, format="css"))
                info.append(f"Created replacement class {new_class_name} preserving original properties")
            
            # Process all pseudo-selector rules
            for pseudo_rule in pseudo_rules:
                # Extract pseudo part from selector
                _, pseudo_part = split_pseudo_selector(pseudo_rule.selector)
                new_pseudo_selector = rebuild_selector_with_base(new_class_name, pseudo_part)
                
                # Check if overrides should apply to this pseudo rule
                if self.rule_matcher.should_apply_override(pseudo_rule.selector, apply_to):
                    # Merge properties for this pseudo state
                    merged_props, merge_info, merge_warnings = self.merger.merge(pseudo_rule.properties, override_props)
                    replacement_pseudo_rule = CSSRule(selector=new_pseudo_selector, properties=merged_props)
                    info.append(f"Applied overrides to {new_pseudo_selector}")
                    info.extend(merge_info)
                    warnings.extend(merge_warnings)
                else:
                    # Preserve original properties for this pseudo state
                    replacement_pseudo_rule = CSSRule(selector=new_pseudo_selector, properties=pseudo_rule.properties)
                    info.append(f"Preserved {new_pseudo_selector} without overrides")
                
                css_outputs.append(self.formatter.format_rule(replacement_pseudo_rule, format="css"))
        
        # Add warning if only processing first rule but there were more
        if self.rule_selection == 'first' and isinstance(source, str) and '{' in source:
            all_rules = self.parser.parse_rule_string(source)
            if len(all_rules) > 1:
                warnings.append(f"Only processed first rule. {len(all_rules)-1} additional rules ignored. Set rule_selection='all' to process all rules.")
        
        return self.prepare_result(
            css=css_outputs,
            add_classes=add_classes,
            remove_classes=remove_classes,
            warnings=warnings,
            info=info
        )
    
    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        return "replace"