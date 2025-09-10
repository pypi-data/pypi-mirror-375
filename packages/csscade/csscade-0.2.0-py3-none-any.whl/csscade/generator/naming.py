"""Class name generation strategies for CSS."""

import hashlib
from typing import Optional, List, Union
from csscade.models import CSSProperty


class ClassNameGenerator:
    """Generates class names for CSS overrides using various strategies."""
    
    def __init__(
        self,
        strategy: str = "hash",
        prefix: str = "css-",
        suffix: str = "",
        hash_length: int = 8
    ):
        """
        Initialize the class name generator.
        
        Args:
            strategy: Naming strategy ('hash', 'semantic', 'sequential')
            prefix: Prefix to add to generated names
            suffix: Suffix to add to generated names
            hash_length: Length of hash for hash-based strategy
        """
        self.strategy = strategy
        self.prefix = prefix
        self.suffix = suffix
        self.hash_length = hash_length
        self._counter = 0
        self._name_cache = {}
    
    def generate_from_properties(
        self,
        properties: Union[List[CSSProperty], str],
        base_name: Optional[str] = None,
        component_id: Optional[str] = None
    ) -> str:
        """
        Generate a class name from CSS properties.
        
        Args:
            properties: List of CSS properties or CSS string
            base_name: Base name for semantic strategy
            component_id: Component ID for uniqueness
            
        Returns:
            Generated class name
        """
        if self.strategy == "hash":
            return self._generate_hash_name(properties)
        elif self.strategy == "semantic":
            return self._generate_semantic_name(properties, base_name, component_id)
        elif self.strategy == "sequential":
            return self._generate_sequential_name()
        else:
            # Default to hash strategy
            return self._generate_hash_name(properties)
    
    def _generate_hash_name(
        self,
        properties: Union[List[CSSProperty], str]
    ) -> str:
        """
        Generate a hash-based class name.
        
        Args:
            properties: CSS properties or string
            
        Returns:
            Hash-based class name
        """
        # Convert properties to a stable string representation
        if isinstance(properties, str):
            content = properties
        else:
            # Sort properties by name for consistent hashing
            sorted_props = sorted(properties, key=lambda p: p.name)
            content = ";".join(f"{p.name}:{p.value}" for p in sorted_props)
        
        # Check cache first
        if content in self._name_cache:
            return self._name_cache[content]
        
        # Generate hash
        hash_obj = hashlib.sha256(content.encode())
        hash_str = hash_obj.hexdigest()[:self.hash_length]
        
        # Create class name
        class_name = f"{self.prefix}{hash_str}{self.suffix}"
        
        # Cache the result
        self._name_cache[content] = class_name
        
        return class_name
    
    def _generate_semantic_name(
        self,
        properties: Union[List[CSSProperty], str],
        base_name: Optional[str] = None,
        component_id: Optional[str] = None
    ) -> str:
        """
        Generate a semantic class name.
        
        Args:
            properties: CSS properties or string
            base_name: Base name to use
            component_id: Component ID for uniqueness
            
        Returns:
            Semantic class name
        """
        parts = []
        
        # Add prefix
        if self.prefix:
            parts.append(self.prefix.rstrip("-"))
        
        # Add base name
        if base_name:
            parts.append(base_name)
        else:
            parts.append("style")
        
        # Add component ID if provided
        if component_id:
            parts.append(component_id)
        else:
            # Add a short hash for uniqueness
            if isinstance(properties, str):
                content = properties
            else:
                sorted_props = sorted(properties, key=lambda p: p.name)
                content = ";".join(f"{p.name}:{p.value}" for p in sorted_props)
            
            hash_obj = hashlib.sha256(content.encode())
            hash_str = hash_obj.hexdigest()[:4]
            parts.append(hash_str)
        
        # Add suffix
        if self.suffix:
            parts.append(self.suffix.lstrip("-"))
        
        return "-".join(parts)
    
    def _generate_sequential_name(self) -> str:
        """
        Generate a sequential class name.
        
        Returns:
            Sequential class name
        """
        self._counter += 1
        return f"{self.prefix}{self._counter}{self.suffix}"
    
    def generate_for_mode(
        self,
        mode: str,
        base_selector: str,
        properties: Union[List[CSSProperty], str],
        component_id: Optional[str] = None
    ) -> str:
        """
        Generate a class name based on merge mode.
        
        Args:
            mode: Merge mode ('permanent', 'component', 'replace')
            base_selector: Base CSS selector
            properties: CSS properties
            component_id: Component ID for uniqueness
            
        Returns:
            Generated class name
        """
        # Clean the base selector (remove . or # prefix)
        clean_base = base_selector.lstrip(".#")
        
        if mode == "permanent":
            # For permanent mode, return the original selector
            return base_selector
        elif mode == "component":
            # For component mode, create an override class
            if component_id:
                return f".{clean_base}-override-{component_id}"
            else:
                # Use semantic naming with base name
                return "." + self.generate_from_properties(
                    properties,
                    base_name=clean_base,
                    component_id=None
                )
        elif mode == "replace":
            # For replace mode, create a replacement class
            return "." + self.generate_from_properties(
                properties,
                base_name=f"{clean_base}-replace",
                component_id=component_id
            )
        else:
            # Default behavior
            return "." + self.generate_from_properties(properties, base_name=clean_base)
    
    def reset_counter(self) -> None:
        """Reset the sequential counter."""
        self._counter = 0
    
    def clear_cache(self) -> None:
        """Clear the name cache."""
        self._name_cache.clear()