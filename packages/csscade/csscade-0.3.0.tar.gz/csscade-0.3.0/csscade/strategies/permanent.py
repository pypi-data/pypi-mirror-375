"""Permanent merge strategy that modifies original classes."""

from typing import Dict, Any, Union, List
from csscade.strategies.base import MergeStrategy
from csscade.models import CSSProperty, CSSRule
from csscade.property_merger import PropertyMerger
from csscade.parser.css_parser import CSSParser
from csscade.generator.output import OutputFormatter
from csscade.utils.rule_matcher import RuleMatcher


class PermanentMergeStrategy(MergeStrategy):
    """
    Permanent merge strategy that modifies the original CSS class directly.
    This strategy overwrites properties in the source with override values.
    """
    
    def __init__(self, conflict_resolution=None, naming=None, rule_selection='first', shorthand_strategy='cascade', validation=None):
        """
        Initialize the permanent merge strategy.
        
        Args:
            conflict_resolution: Optional conflict resolution configuration
            naming: Optional naming configuration (not used in permanent mode)
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
        # Note: permanent mode doesn't generate new class names
    
    def merge(
        self,
        source: Union[str, CSSRule, Dict[str, str], List[CSSProperty]],
        override: Union[Dict[str, str], List[CSSProperty], str],
        apply_to: Union[str, List[str]] = 'all',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Merge CSS properties by permanently modifying the original class.
        
        Args:
            source: Source CSS (can be rule, properties, or string)
            override: Override properties
            apply_to: Which rules to apply overrides to
            **kwargs: Additional parameters (unused in this strategy)
            
        Returns:
            Dictionary with:
                - css: List of modified CSS strings
                - add: Empty list (no new classes in permanent mode)
                - remove: Empty list
                - preserve: Empty list (original classes are modified)
                - warnings: List of warnings
                - info: List of info messages
        """
        self.validate_input(source, override)
        
        # Parse source to determine type
        rules_to_process = []
        
        if isinstance(source, CSSRule):
            # Source is already a rule
            rules_to_process = [source]
        elif isinstance(source, str) and '{' in source:
            # Source is a CSS rule string
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
        
        # Process each rule
        css_outputs = []
        warnings = []
        info = []
        
        for rule in rules_to_process:
            # Check if overrides should be applied to this rule
            if self.rule_matcher.should_apply_override(rule.selector, apply_to):
                # Merge properties for this rule
                merged_rule, merge_info, merge_warnings = self.merger.merge_rules(rule, override_props)
                info.append(f"Applied overrides to {rule.selector}")
                # Add any info/warnings from the merge
                info.extend(merge_info)
                warnings.extend(merge_warnings)
            else:
                # Keep rule unchanged
                merged_rule = rule
                info.append(f"Preserved {rule.selector} without changes")
            
            # Format the output
            css_output = self.formatter.format_rule(merged_rule, format="css")
            css_outputs.append(css_output)
        
        # Add warning if only processing first rule but there were more
        if self.rule_selection == 'first' and isinstance(source, str) and '{' in source:
            all_rules = self.parser.parse_rule_string(source)
            if len(all_rules) > 1:
                warnings.append(f"Only processed first rule. {len(all_rules)-1} additional rules ignored. Set rule_selection='all' to process all rules.")
        
        return self.prepare_result(
            css=css_outputs,
            warnings=warnings,
            info=info
        )
    
    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        return "permanent"