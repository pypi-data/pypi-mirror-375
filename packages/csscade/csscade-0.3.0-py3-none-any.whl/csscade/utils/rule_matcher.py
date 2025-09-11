"""Rule matching utilities for apply_to parameter support."""

from typing import List, Union, Optional, Dict
import re


class RuleMatcher:
    """Handles matching of CSS rules based on apply_to parameter."""
    
    @staticmethod
    def should_apply_override(
        selector: str,
        apply_to: Union[str, List[str]]
    ) -> bool:
        """
        Determine if overrides should be applied to a given selector.
        
        Args:
            selector: The CSS selector to check
            apply_to: The apply_to parameter value
            
        Returns:
            True if overrides should be applied to this selector
        """
        # Normalize apply_to to list
        if isinstance(apply_to, str):
            apply_targets = [apply_to]
        else:
            apply_targets = apply_to
        
        # Clean selector for comparison
        selector = selector.strip()
        base_selector = RuleMatcher.get_base_selector(selector)
        
        for target in apply_targets:
            target = target.strip()
            
            # Handle special keywords
            if target == 'all':
                return True
            elif target == 'base':
                # Apply only to base selectors (no pseudo-classes)
                if ':' not in selector:
                    return True
                # Continue checking other targets
            elif target == 'states':
                # Apply only to pseudo-class selectors
                if ':' in selector:
                    return True
                # Continue checking other targets
            
            # Handle wildcards
            elif target.startswith('*') or target == '.*':
                if target == '*':
                    return True
                elif target == '.*':
                    # All base classes (no pseudo)
                    return ':' not in selector
                elif ':' in target:
                    # Wildcard for specific pseudo-class (e.g., '*:hover')
                    pseudo = target.split(':')[1]
                    return f':{pseudo}' in selector
            
            # Handle specific selector matching
            elif target == selector:
                # Exact match
                return True
            elif target.startswith(':'):
                # Match by pseudo-class only (e.g., ':hover')
                return target in selector
            # Note: We removed the base_selector match here because it was too broad
            # If user wants to match all states of a base class, they should use wildcards
        
        return False
    
    @staticmethod
    def get_base_selector(selector: str) -> str:
        """
        Extract the base selector without pseudo-classes.
        
        Args:
            selector: Full CSS selector
            
        Returns:
            Base selector without pseudo-classes
        """
        # Remove pseudo-classes and pseudo-elements
        base = re.sub(r':+[\w-]+(\([^)]*\))?', '', selector)
        return base.strip()
    
    @staticmethod
    def get_pseudo_parts(selector: str) -> List[str]:
        """
        Extract all pseudo-class/element parts from a selector.
        
        Args:
            selector: CSS selector
            
        Returns:
            List of pseudo parts (e.g., [':hover', ':focus'])
        """
        pattern = r'(:+[\w-]+(?:\([^)]*\))?)'
        matches = re.findall(pattern, selector)
        return matches
    
    @staticmethod
    def group_related_rules(rules: List) -> Dict[str, List]:
        """
        Group rules by their base selector.
        
        Args:
            rules: List of CSS rules
            
        Returns:
            Dictionary mapping base selectors to lists of related rules
        """
        from collections import defaultdict
        groups = defaultdict(list)
        
        for rule in rules:
            base = RuleMatcher.get_base_selector(rule.selector)
            groups[base].append(rule)
        
        return dict(groups)
    
    @staticmethod
    def normalize_apply_to(apply_to: Union[str, List[str]]) -> List[str]:
        """
        Normalize apply_to parameter to a list.
        
        Args:
            apply_to: The apply_to parameter value
            
        Returns:
            Normalized list of apply targets
        """
        if isinstance(apply_to, str):
            return [apply_to]
        return apply_to if apply_to else ['all']