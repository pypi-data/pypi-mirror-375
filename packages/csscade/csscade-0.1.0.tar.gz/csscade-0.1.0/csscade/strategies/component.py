"""Component merge strategy that preserves original classes."""

from typing import Dict, Any, Union, List, Optional
from csscade.strategies.base import MergeStrategy
from csscade.models import CSSProperty, CSSRule
from csscade.property_merger import PropertyMerger
from csscade.parser.css_parser import CSSParser
from csscade.generator.output import OutputFormatter
from csscade.generator.naming import ClassNameGenerator
from csscade.resolvers.conflict_detector import ConflictDetector
from csscade.handlers.selector_utils import (
    split_pseudo_selector, 
    rebuild_selector_with_base,
    clone_rule_with_new_selector
)


class ComponentMergeStrategy(MergeStrategy):
    """
    Component merge strategy that creates override classes while preserving originals.
    This strategy creates a new class with only the override properties,
    allowing both original and override classes to be applied.
    """
    
    def __init__(self, conflict_resolution=None, naming=None):
        """
        Initialize the component merge strategy.
        
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
            strategy=naming_config.get('strategy', 'semantic'),
            prefix=naming_config.get('prefix', 'css-'),
            suffix=naming_config.get('suffix', ''),
            hash_length=naming_config.get('hash_length', 8)
        )
        self.conflict_detector = ConflictDetector()
    
    def merge(
        self,
        source: Union[str, CSSRule, Dict[str, str], List[CSSProperty]],
        override: Union[Dict[str, str], List[CSSProperty], str],
        component_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Merge CSS properties by creating an override class.
        
        Args:
            source: Source CSS (can be rule, properties, or string)
            override: Override properties
            component_id: Optional component ID for unique class naming
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with:
                - css: New override class with only conflicting properties
                - add: List of classes to add (the new override class)
                - preserve: List of classes to preserve (original class)
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
        
        # Parse override properties
        if isinstance(override, str):
            override_props = self.parser.parse_properties_string(override)
        elif isinstance(override, dict):
            override_props = self.parser.parse_properties_dict(override)
        else:
            override_props = override
        
        # Check if selector has pseudo-class/element
        base_selector, pseudo_part = split_pseudo_selector(source_rule.selector)
        
        # Generate new base class name for the component
        new_base_name = self.name_generator.generate_for_mode(
            mode="component",
            base_selector=base_selector,
            properties=override_props,
            component_id=component_id
        )
        
        # Remove leading . or # from class name for clean output
        clean_class_name = new_base_name.lstrip('.#')
        
        css_rules = []
        warnings = []
        
        if pseudo_part:
            # Use ConflictResolver if available
            if self.conflict_resolver:
                resolution = self.conflict_resolver.resolve_pseudo_conflict(
                    source_rule, override_props, pseudo_part
                )
                
                if resolution['strategy'] == 'preserve':
                    # Keep pseudo selector, create new rule with pseudo
                    base_rule = CSSRule(
                        selector=new_base_name,
                        properties=[]  # Would copy from original base rule if found
                    )
                    css_rules.append(self.formatter.format_rule(base_rule, format="css"))
                    
                    pseudo_selector = rebuild_selector_with_base(new_base_name, pseudo_part)
                    merged_props = self.merger.merge_properties(
                        source_rule.properties,
                        override_props
                    )
                    pseudo_rule = CSSRule(
                        selector=pseudo_selector,
                        properties=merged_props
                    )
                    css_rules.append(self.formatter.format_rule(pseudo_rule, format="css"))
                    
                    if 'message' in resolution:
                        warnings.append(resolution['message'])
                        
                elif resolution['strategy'] == 'inline':
                    # Convert to inline styles for runtime application
                    base_rule = CSSRule(
                        selector=new_base_name,
                        properties=self.merger.merge_properties(
                            source_rule.properties,
                            override_props
                        )
                    )
                    css_rules.append(self.formatter.format_rule(base_rule, format="css"))
                    
                    # Add inline styles to result
                    result_inline = resolution.get('inline_styles', {})
                    pseudo_state = resolution.get('pseudo_state', pseudo_part)
                    
                    # Store inline styles for the pseudo state
                    if 'message' in resolution:
                        warnings.append(resolution['message'])
                        
                elif resolution['strategy'] == 'force_merge':
                    # Merge without pseudo selector
                    merged_props = self.merger.merge_properties(
                        source_rule.properties,
                        override_props
                    )
                    base_rule = CSSRule(
                        selector=new_base_name,
                        properties=merged_props
                    )
                    css_rules.append(self.formatter.format_rule(base_rule, format="css"))
                    
                    if 'warning' in resolution:
                        warnings.append(resolution['warning'])
                        
                else:
                    # Fallback to original behavior
                    base_rule = CSSRule(
                        selector=new_base_name,
                        properties=[]
                    )
                    css_rules.append(self.formatter.format_rule(base_rule, format="css"))
                    
                    pseudo_selector = rebuild_selector_with_base(new_base_name, pseudo_part)
                    merged_props = self.merger.merge_properties(
                        source_rule.properties,
                        override_props
                    )
                    pseudo_rule = CSSRule(
                        selector=pseudo_selector,
                        properties=merged_props
                    )
                    css_rules.append(self.formatter.format_rule(pseudo_rule, format="css"))
            else:
                # Original behavior when no conflict resolver
                base_rule = CSSRule(
                    selector=new_base_name,
                    properties=[]
                )
                css_rules.append(self.formatter.format_rule(base_rule, format="css"))
                
                warnings.append(
                    f"Base rule {new_base_name} created empty. Configure conflict_resolution " +
                    f"for better pseudo selector handling."
                )
                
                pseudo_selector = rebuild_selector_with_base(new_base_name, pseudo_part)
                merged_props = self.merger.merge_properties(
                    source_rule.properties,
                    override_props
                )
                pseudo_rule = CSSRule(
                    selector=pseudo_selector,
                    properties=merged_props
                )
                css_rules.append(self.formatter.format_rule(pseudo_rule, format="css"))
        else:
            # Regular selector without pseudo - original behavior
            merged_props = self.merger.merge_properties(
                source_rule.properties,
                override_props
            )
            
            override_rule = CSSRule(
                selector=new_base_name,
                properties=merged_props
            )
            css_rules.append(self.formatter.format_rule(override_rule, format="css"))
        
        css_output = "\n".join(css_rules) if css_rules else None
        
        # Prepare result
        result = {
            "css": css_output,
            "add": [clean_class_name],  # Use the clean class name
            "preserve": [base_selector.lstrip('.#')],  # Preserve original base selector
            "inline_styles": None
        }
        
        # Add warnings if any
        if warnings:
            result["warnings"] = warnings
        
        return result
    
    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        return "component"