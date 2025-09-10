"""Conflict detection for CSS properties."""

from typing import Set, Dict, List, Tuple


class ConflictDetector:
    """Detects conflicts between CSS properties including shorthand/longhand relationships."""
    
    def __init__(self) -> None:
        """Initialize the conflict detector with property relationships."""
        # Map of shorthand properties to their longhand equivalents
        self.shorthand_map: Dict[str, Set[str]] = {
            # Margin
            "margin": {"margin-top", "margin-right", "margin-bottom", "margin-left"},
            
            # Padding
            "padding": {"padding-top", "padding-right", "padding-bottom", "padding-left"},
            
            # Border
            "border": {
                "border-width", "border-style", "border-color",
                "border-top", "border-right", "border-bottom", "border-left",
                "border-top-width", "border-right-width", "border-bottom-width", "border-left-width",
                "border-top-style", "border-right-style", "border-bottom-style", "border-left-style",
                "border-top-color", "border-right-color", "border-bottom-color", "border-left-color"
            },
            "border-width": {"border-top-width", "border-right-width", "border-bottom-width", "border-left-width"},
            "border-style": {"border-top-style", "border-right-style", "border-bottom-style", "border-left-style"},
            "border-color": {"border-top-color", "border-right-color", "border-bottom-color", "border-left-color"},
            "border-top": {"border-top-width", "border-top-style", "border-top-color"},
            "border-right": {"border-right-width", "border-right-style", "border-right-color"},
            "border-bottom": {"border-bottom-width", "border-bottom-style", "border-bottom-color"},
            "border-left": {"border-left-width", "border-left-style", "border-left-color"},
            
            # Background
            "background": {
                "background-color", "background-image", "background-repeat",
                "background-attachment", "background-position", "background-size",
                "background-origin", "background-clip"
            },
            
            # Font
            "font": {
                "font-style", "font-variant", "font-weight", "font-size",
                "line-height", "font-family"
            },
            
            # List style
            "list-style": {"list-style-type", "list-style-position", "list-style-image"},
            
            # Outline
            "outline": {"outline-width", "outline-style", "outline-color"},
            
            # Flex
            "flex": {"flex-grow", "flex-shrink", "flex-basis"},
            
            # Grid
            "grid": {
                "grid-template-rows", "grid-template-columns", "grid-template-areas",
                "grid-auto-rows", "grid-auto-columns", "grid-auto-flow"
            },
            "grid-template": {"grid-template-rows", "grid-template-columns", "grid-template-areas"},
            "grid-gap": {"grid-row-gap", "grid-column-gap"},
            "gap": {"row-gap", "column-gap"},
            
            # Animation
            "animation": {
                "animation-name", "animation-duration", "animation-timing-function",
                "animation-delay", "animation-iteration-count", "animation-direction",
                "animation-fill-mode", "animation-play-state"
            },
            
            # Transition
            "transition": {
                "transition-property", "transition-duration",
                "transition-timing-function", "transition-delay"
            },
            
            # Text decoration
            "text-decoration": {
                "text-decoration-line", "text-decoration-color",
                "text-decoration-style", "text-decoration-thickness"
            },
            
            # Columns
            "columns": {"column-width", "column-count"},
            "column-rule": {"column-rule-width", "column-rule-style", "column-rule-color"},
            
            # Border radius
            "border-radius": {
                "border-top-left-radius", "border-top-right-radius",
                "border-bottom-right-radius", "border-bottom-left-radius"
            },
            
            # Overflow
            "overflow": {"overflow-x", "overflow-y"},
            
            # Place (grid/flexbox)
            "place-content": {"align-content", "justify-content"},
            "place-items": {"align-items", "justify-items"},
            "place-self": {"align-self", "justify-self"}
        }
        
        # Build reverse mapping (longhand to shorthands that contain it)
        self.longhand_to_shorthands: Dict[str, Set[str]] = {}
        for shorthand, longhands in self.shorthand_map.items():
            for longhand in longhands:
                if longhand not in self.longhand_to_shorthands:
                    self.longhand_to_shorthands[longhand] = set()
                self.longhand_to_shorthands[longhand].add(shorthand)
    
    def detect_conflict(self, property1: str, property2: str) -> bool:
        """
        Detect if two CSS properties conflict with each other.
        
        Args:
            property1: First property name
            property2: Second property name
        
        Returns:
            True if properties conflict, False otherwise
        """
        # Same property always conflicts
        if property1 == property2:
            return True
        
        # Check if one is a shorthand that contains the other
        if property1 in self.shorthand_map and property2 in self.shorthand_map[property1]:
            return True
        if property2 in self.shorthand_map and property1 in self.shorthand_map[property2]:
            return True
        
        # Check if both are longhands of the same shorthand
        shorthands1 = self.longhand_to_shorthands.get(property1, set())
        shorthands2 = self.longhand_to_shorthands.get(property2, set())
        
        # If they share any shorthand parent, they might conflict
        # but only if they're actually the same longhand property
        # (different longhands of same shorthand don't conflict)
        
        return False
    
    def find_conflicts(self, properties: List[str]) -> List[Tuple[str, str]]:
        """
        Find all conflicting property pairs in a list.
        
        Args:
            properties: List of property names
        
        Returns:
            List of conflicting property pairs
        """
        conflicts = []
        for i, prop1 in enumerate(properties):
            for prop2 in properties[i+1:]:
                if self.detect_conflict(prop1, prop2):
                    conflicts.append((prop1, prop2))
        return conflicts
    
    def get_affected_properties(self, property_name: str) -> Set[str]:
        """
        Get all properties that would be affected by setting this property.
        
        Args:
            property_name: CSS property name
        
        Returns:
            Set of affected property names (including the property itself)
        """
        affected = {property_name}
        
        # If it's a shorthand, add all its longhands
        if property_name in self.shorthand_map:
            affected.update(self.shorthand_map[property_name])
        
        # If it's a longhand, add any shorthands that contain it
        if property_name in self.longhand_to_shorthands:
            affected.update(self.longhand_to_shorthands[property_name])
        
        return affected
    
    def is_shorthand(self, property_name: str) -> bool:
        """
        Check if a property is a shorthand property.
        
        Args:
            property_name: CSS property name
        
        Returns:
            True if property is a shorthand, False otherwise
        """
        return property_name in self.shorthand_map
    
    def is_longhand(self, property_name: str) -> bool:
        """
        Check if a property is a longhand property.
        
        Args:
            property_name: CSS property name
        
        Returns:
            True if property is a longhand, False otherwise
        """
        return property_name in self.longhand_to_shorthands
    
    def get_longhand_properties(self, shorthand: str) -> Set[str]:
        """
        Get the longhand properties for a shorthand.
        
        Args:
            shorthand: Shorthand property name
        
        Returns:
            Set of longhand property names, or empty set if not a shorthand
        """
        return self.shorthand_map.get(shorthand, set())
    
    def get_shorthand_properties(self, longhand: str) -> Set[str]:
        """
        Get the shorthand properties that contain a longhand.
        
        Args:
            longhand: Longhand property name
        
        Returns:
            Set of shorthand property names, or empty set if not a longhand
        """
        return self.longhand_to_shorthands.get(longhand, set())