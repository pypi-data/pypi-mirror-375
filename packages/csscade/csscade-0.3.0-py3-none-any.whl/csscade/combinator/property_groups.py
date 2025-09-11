"""Property groups for handling CSS shorthand/longhand conflicts."""

from typing import List, Set

PROPERTY_GROUPS = {
    'padding': [
        'padding', 
        'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
        'padding-block', 'padding-inline',
        'padding-block-start', 'padding-block-end',
        'padding-inline-start', 'padding-inline-end'
    ],
    'margin': [
        'margin',
        'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
        'margin-block', 'margin-inline',
        'margin-block-start', 'margin-block-end',
        'margin-inline-start', 'margin-inline-end'
    ],
    'border': [
        'border',
        'border-width', 'border-style', 'border-color',
        'border-top', 'border-right', 'border-bottom', 'border-left',
        'border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width',
        'border-top-style', 'border-right-style', 'border-bottom-style', 'border-left-style',
        'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color'
    ],
    'border-radius': [
        'border-radius',
        'border-top-left-radius', 'border-top-right-radius',
        'border-bottom-left-radius', 'border-bottom-right-radius'
    ],
    'background': [
        'background',
        'background-color', 'background-image', 'background-position',
        'background-size', 'background-repeat', 'background-origin',
        'background-clip', 'background-attachment',
        'background-position-x', 'background-position-y'
    ],
    'font': [
        'font',
        'font-family', 'font-size', 'font-weight', 'font-style',
        'font-variant', 'font-stretch', 'line-height',
        'font-size-adjust', 'font-kerning', 'font-feature-settings'
    ],
    'flex': [
        'flex',
        'flex-grow', 'flex-shrink', 'flex-basis',
        'flex-direction', 'flex-wrap', 'flex-flow'
    ],
    'grid': [
        'grid',
        'grid-template', 'grid-template-rows', 'grid-template-columns',
        'grid-template-areas', 'grid-auto-rows', 'grid-auto-columns',
        'grid-auto-flow', 'grid-row', 'grid-column',
        'grid-row-start', 'grid-row-end', 'grid-column-start', 'grid-column-end',
        'grid-area', 'grid-gap', 'grid-row-gap', 'grid-column-gap'
    ],
    'outline': [
        'outline',
        'outline-width', 'outline-style', 'outline-color', 'outline-offset'
    ],
    'animation': [
        'animation',
        'animation-name', 'animation-duration', 'animation-timing-function',
        'animation-delay', 'animation-iteration-count', 'animation-direction',
        'animation-fill-mode', 'animation-play-state'
    ],
    'transition': [
        'transition',
        'transition-property', 'transition-duration', 'transition-timing-function',
        'transition-delay'
    ],
    'transform': [
        'transform',
        'transform-origin', 'transform-style', 'transform-box'
    ],
    'text-decoration': [
        'text-decoration',
        'text-decoration-line', 'text-decoration-color', 'text-decoration-style',
        'text-decoration-thickness'
    ],
    'overflow': [
        'overflow',
        'overflow-x', 'overflow-y', 'overflow-wrap'
    ],
    'position': [
        'position',
        'top', 'right', 'bottom', 'left',
        'inset', 'inset-block', 'inset-inline',
        'inset-block-start', 'inset-block-end',
        'inset-inline-start', 'inset-inline-end'
    ],
    'display': [
        'display',
        'visibility', 'opacity'
    ],
    'width': [
        'width', 'min-width', 'max-width'
    ],
    'height': [
        'height', 'min-height', 'max-height'
    ]
}


def get_related_properties(prop: str) -> Set[str]:
    """
    Get all properties that conflict with the given property.
    
    Args:
        prop: CSS property name
        
    Returns:
        Set of all properties that conflict with the given property
    """
    prop = prop.lower().strip()
    
    # Check each property group
    for group_name, group_props in PROPERTY_GROUPS.items():
        if prop in group_props:
            return set(group_props)
    
    # No group found, return just the property itself
    return {prop}


def has_property_conflict(class_props: Set[str], override_prop: str) -> bool:
    """
    Check if an override property conflicts with any class properties.
    
    Args:
        class_props: Set of CSS properties defined by a class
        override_prop: The property being overridden
        
    Returns:
        True if there's a conflict, False otherwise
    """
    related_props = get_related_properties(override_prop)
    return bool(class_props.intersection(related_props))


def get_conflicting_properties(class_props: Set[str], override_props: Set[str]) -> Set[str]:
    """
    Get all properties from class_props that conflict with override_props.
    
    Args:
        class_props: Set of CSS properties defined by a class
        override_props: Set of properties being overridden
        
    Returns:
        Set of conflicting properties from class_props
    """
    conflicts = set()
    
    for override_prop in override_props:
        related = get_related_properties(override_prop)
        conflicts.update(class_props.intersection(related))
    
    return conflicts