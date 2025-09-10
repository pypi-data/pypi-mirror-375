"""CSS data models for CSSCade."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class CSSProperty:
    """Represents a single CSS property with its value and importance."""
    
    name: str
    value: str
    important: bool = False
    
    def __str__(self) -> str:
        """Return the CSS string representation of the property."""
        importance = " !important" if self.important else ""
        return f"{self.name}: {self.value}{importance}"
    
    def __eq__(self, other: object) -> bool:
        """Check equality based on name, value, and importance."""
        if not isinstance(other, CSSProperty):
            return False
        return (
            self.name == other.name 
            and self.value == other.value 
            and self.important == other.important
        )
    
    def __hash__(self) -> int:
        """Make the property hashable for use in sets and dicts."""
        return hash((self.name, self.value, self.important))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert property to dictionary representation."""
        return {
            "name": self.name,
            "value": self.value,
            "important": self.important
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CSSProperty":
        """Create a CSSProperty from dictionary representation."""
        return cls(
            name=data["name"],
            value=data["value"],
            important=data.get("important", False)
        )


@dataclass
class CSSRule:
    """Represents a CSS rule with a selector and list of properties."""
    
    selector: str
    properties: List[CSSProperty] = field(default_factory=list)
    
    def __str__(self) -> str:
        """Return the CSS string representation of the rule."""
        if not self.properties:
            return f"{self.selector} {{}}"
        
        props_str = "; ".join(str(prop) for prop in self.properties)
        return f"{self.selector} {{ {props_str}; }}"
    
    def add_property(self, property: CSSProperty) -> None:
        """Add a property to the rule."""
        self.properties.append(property)
    
    def remove_property(self, property_name: str) -> bool:
        """Remove a property by name. Returns True if removed, False if not found."""
        initial_length = len(self.properties)
        self.properties = [
            prop for prop in self.properties 
            if prop.name != property_name
        ]
        return len(self.properties) < initial_length
    
    def get_property(self, property_name: str) -> Optional[CSSProperty]:
        """Get a property by name. Returns None if not found."""
        for prop in self.properties:
            if prop.name == property_name:
                return prop
        return None
    
    def has_property(self, property_name: str) -> bool:
        """Check if the rule has a property with the given name."""
        return any(prop.name == property_name for prop in self.properties)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary representation."""
        return {
            "selector": self.selector,
            "properties": [prop.to_dict() for prop in self.properties]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CSSRule":
        """Create a CSSRule from dictionary representation."""
        properties = [
            CSSProperty.from_dict(prop_data) 
            for prop_data in data.get("properties", [])
        ]
        return cls(selector=data["selector"], properties=properties)
    
    def get_properties_dict(self) -> Dict[str, str]:
        """Get properties as a simple dictionary (name -> value)."""
        return {prop.name: prop.value for prop in self.properties}
    
    def merge_properties(self, other_properties: List[CSSProperty]) -> None:
        """Merge other properties into this rule, overriding existing ones."""
        property_map = {prop.name: prop for prop in self.properties}
        
        for prop in other_properties:
            property_map[prop.name] = prop
        
        self.properties = list(property_map.values())