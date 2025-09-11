"""Utility functions for CSS selector handling."""

import re
from typing import Tuple, Optional, List, Dict
from csscade.models import CSSRule, CSSProperty


def split_pseudo_selector(selector: str) -> Tuple[str, Optional[str]]:
    """
    Split a selector into base and pseudo parts.
    
    Args:
        selector: CSS selector like '.btn:hover' or '.btn'
        
    Returns:
        Tuple of (base_selector, pseudo_part) where pseudo_part may be None
        
    Examples:
        '.btn:hover' -> ('.btn', ':hover')
        '.btn' -> ('.btn', None)
        'a:visited:hover' -> ('a', ':visited:hover')
    """
    # Find the first : that starts a pseudo-class or pseudo-element
    match = re.match(r'^([^:]+)(:.+)?$', selector)
    if match:
        base = match.group(1).strip()
        pseudo = match.group(2) if match.group(2) else None
        return base, pseudo
    return selector, None


def rebuild_selector_with_base(base: str, pseudo: Optional[str]) -> str:
    """
    Rebuild a selector with a new base but preserve pseudo parts.
    
    Args:
        base: New base selector
        pseudo: Pseudo-class/element part (can be None)
        
    Returns:
        Combined selector
        
    Examples:
        ('.btn-override', ':hover') -> '.btn-override:hover'
        ('.btn-override', None) -> '.btn-override'
    """
    if pseudo:
        return f"{base}{pseudo}"
    return base


def find_related_rules(rules: List[CSSRule], base_selector: str) -> Dict[str, CSSRule]:
    """
    Find all rules related to a base selector (including pseudo-class variations).
    
    Args:
        rules: List of CSS rules to search
        base_selector: Base selector to match (e.g., '.btn')
        
    Returns:
        Dictionary mapping full selectors to their rules
        
    Example:
        Given rules for '.btn', '.btn:hover', '.btn:focus'
        and base_selector='.btn'
        Returns: {
            '.btn': <rule>,
            '.btn:hover': <rule>,
            '.btn:focus': <rule>
        }
    """
    related = {}
    
    for rule in rules:
        rule_base, _ = split_pseudo_selector(rule.selector)
        if rule_base == base_selector:
            related[rule.selector] = rule
    
    return related


def clone_rule_with_new_selector(rule: CSSRule, new_selector: str) -> CSSRule:
    """
    Clone a CSS rule with a new selector.
    
    Args:
        rule: Original CSS rule
        new_selector: New selector for the cloned rule
        
    Returns:
        New CSSRule with cloned properties
    """
    # Clone properties
    cloned_props = [
        CSSProperty(prop.name, prop.value, prop.important)
        for prop in rule.properties
    ]
    
    return CSSRule(new_selector, cloned_props)