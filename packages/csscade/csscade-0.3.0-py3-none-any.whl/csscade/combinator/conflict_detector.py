"""Conflict detection for CSS classes and overrides."""

from typing import Dict, List, Set, Union, Tuple
from .property_groups import has_property_conflict, get_conflicting_properties


class ConflictDetector:
    """Detects conflicts between CSS classes and override properties."""
    
    def find_conflicts(
        self,
        element_classes: List[str],
        overrides: Dict,
        class_properties: Dict[str, Dict[str, str]]
    ) -> Dict[str, List[str]]:
        """
        Find which classes conflict with the given overrides.
        
        Args:
            element_classes: List of CSS class names on the element
            overrides: Dictionary of CSS properties to override (may include pseudo-selectors)
            class_properties: Mapping of class names to their CSS properties
            
        Returns:
            Dictionary mapping conflicting class names to the properties that conflict
        """
        conflicts = {}
        
        # Flatten overrides to get all properties being overridden
        flat_overrides = self._flatten_overrides(overrides)
        override_props = set(flat_overrides.keys())
        
        # Check each class for conflicts
        for class_name in element_classes:
            if class_name not in class_properties:
                # Class not found in loaded CSS, skip it
                continue
            
            # Get properties defined by this class
            class_props = set(class_properties[class_name].keys())
            
            # Find conflicting properties
            conflicting_props = []
            for override_prop in override_props:
                # Remove pseudo-selector prefix if present for property comparison
                base_prop = self._extract_base_property(override_prop)
                
                if has_property_conflict(class_props, base_prop):
                    conflicting_props.append(base_prop)
            
            # If there are conflicts, record them
            if conflicting_props:
                conflicts[class_name] = list(set(conflicting_props))  # Remove duplicates
        
        return conflicts
    
    def _flatten_overrides(self, overrides: Dict) -> Dict[str, str]:
        """
        Flatten nested override structure (with pseudo-selectors) into a flat dictionary.
        
        Args:
            overrides: Potentially nested dictionary of overrides
            
        Returns:
            Flat dictionary with all properties
        """
        flat = {}
        
        for key, value in overrides.items():
            if key.startswith(':'):
                # It's a pseudo-selector with nested properties
                if isinstance(value, dict):
                    for prop, val in value.items():
                        # Store with pseudo-selector prefix for tracking
                        flat[f"{key}:{prop}"] = val
                else:
                    # Shouldn't happen with proper structure, but handle gracefully
                    flat[key] = value
            else:
                # Regular property
                flat[key] = value
        
        return flat
    
    def _extract_base_property(self, prop: str) -> str:
        """
        Extract the base property name from a potentially prefixed property.
        
        Args:
            prop: Property name that may have pseudo-selector prefix
            
        Returns:
            Base property name
        """
        # If it has a pseudo-selector prefix like ":hover:background-color"
        if prop.startswith(':') and ':' in prop[1:]:
            # Split by colon and take the last part
            parts = prop.split(':')
            return parts[-1]
        return prop
    
    def get_conflicting_values(
        self,
        class_name: str,
        override_props: Set[str],
        class_properties: Dict[str, Dict[str, str]]
    ) -> Dict[str, Tuple[str, str]]:
        """
        Get the actual values that are conflicting.
        
        Args:
            class_name: The CSS class name
            override_props: Set of properties being overridden
            class_properties: Mapping of class names to their CSS properties
            
        Returns:
            Dictionary mapping property names to (original_value, override_value) tuples
        """
        conflicts = {}
        
        if class_name not in class_properties:
            return conflicts
        
        class_props = class_properties[class_name]
        
        for override_prop in override_props:
            base_prop = self._extract_base_property(override_prop)
            
            # Get all properties that might conflict
            class_prop_set = set(class_props.keys())
            conflicting = get_conflicting_properties(class_prop_set, {base_prop})
            
            for conflict_prop in conflicting:
                if conflict_prop in class_props:
                    conflicts[conflict_prop] = (class_props[conflict_prop], None)
        
        return conflicts
    
    def analyze_specificity_requirements(
        self,
        conflicts: Dict[str, List[str]]
    ) -> Dict[str, bool]:
        """
        Analyze which properties need !important based on conflicts.
        
        Args:
            conflicts: Dictionary of class conflicts
            
        Returns:
            Dictionary mapping property names to whether they need !important
        """
        important_needed = {}
        
        # Collect all conflicting properties
        all_conflicting_props = set()
        for props in conflicts.values():
            all_conflicting_props.update(props)
        
        # All conflicting properties need !important
        for prop in all_conflicting_props:
            important_needed[prop] = True
        
        return important_needed