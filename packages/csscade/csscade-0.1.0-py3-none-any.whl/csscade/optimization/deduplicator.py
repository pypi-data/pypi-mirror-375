"""Style deduplication for efficient CSS generation."""

from typing import Dict, List, Optional, Set, Tuple
import hashlib
import json


class StyleRegistry:
    """Registry for tracking and deduplicating styles."""
    
    def __init__(self):
        """Initialize the style registry."""
        self.styles: Dict[str, str] = {}  # hash -> class_name
        self.class_to_properties: Dict[str, Dict[str, str]] = {}  # class_name -> properties
        self.reference_count: Dict[str, int] = {}  # class_name -> count
    
    def _hash_properties(self, properties: Dict[str, str]) -> str:
        """
        Generate hash for properties.
        
        Args:
            properties: CSS properties dictionary
            
        Returns:
            Hash string
        """
        # Sort for consistent hashing
        sorted_props = json.dumps(properties, sort_keys=True)
        return hashlib.md5(sorted_props.encode()).hexdigest()
    
    def register(
        self,
        properties: Dict[str, str],
        class_name: Optional[str] = None
    ) -> Tuple[str, bool]:
        """
        Register style and return class name.
        
        Args:
            properties: CSS properties
            class_name: Optional preferred class name
            
        Returns:
            Tuple of (class_name, is_new)
        """
        prop_hash = self._hash_properties(properties)
        
        if prop_hash in self.styles:
            # Style already exists, reuse class name
            existing_class = self.styles[prop_hash]
            self.reference_count[existing_class] += 1
            return (existing_class, False)
        
        # New style
        if class_name is None:
            class_name = f'style-{prop_hash[:8]}'
        
        self.styles[prop_hash] = class_name
        self.class_to_properties[class_name] = properties.copy()
        self.reference_count[class_name] = 1
        
        return (class_name, True)
    
    def get_properties(self, class_name: str) -> Optional[Dict[str, str]]:
        """
        Get properties for a class name.
        
        Args:
            class_name: CSS class name
            
        Returns:
            Properties dictionary or None
        """
        return self.class_to_properties.get(class_name)
    
    def find_similar(
        self,
        properties: Dict[str, str],
        threshold: float = 0.8
    ) -> List[str]:
        """
        Find similar styles in registry.
        
        Args:
            properties: CSS properties to match
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar class names
        """
        similar = []
        prop_set = set(properties.items())
        
        for class_name, existing_props in self.class_to_properties.items():
            existing_set = set(existing_props.items())
            
            # Calculate Jaccard similarity
            intersection = len(prop_set & existing_set)
            union = len(prop_set | existing_set)
            
            if union > 0:
                similarity = intersection / union
                if similarity >= threshold:
                    similar.append(class_name)
        
        return similar
    
    def deduplicate_batch(
        self,
        style_list: List[Dict[str, str]]
    ) -> List[Tuple[str, Dict[str, str]]]:
        """
        Deduplicate a batch of styles.
        
        Args:
            style_list: List of CSS property dictionaries
            
        Returns:
            List of (class_name, properties) tuples
        """
        result = []
        
        for properties in style_list:
            class_name, is_new = self.register(properties)
            if is_new:
                result.append((class_name, properties))
            else:
                # Return class name with empty properties (reused)
                result.append((class_name, {}))
        
        return result
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get registry statistics.
        
        Returns:
            Statistics dictionary
        """
        total_refs = sum(self.reference_count.values())
        unique_styles = len(self.styles)
        
        return {
            'unique_styles': unique_styles,
            'total_references': total_refs,
            'deduplication_ratio': (total_refs - unique_styles) / total_refs if total_refs > 0 else 0,
            'most_reused': max(self.reference_count.items(), key=lambda x: x[1]) if self.reference_count else None
        }
    
    def clear(self) -> None:
        """Clear the registry."""
        self.styles.clear()
        self.class_to_properties.clear()
        self.reference_count.clear()


class PropertyOptimizer:
    """Optimize CSS properties for size and performance."""
    
    def __init__(self):
        """Initialize the property optimizer."""
        self.shorthand_map = {
            'margin-top': 'margin',
            'margin-right': 'margin',
            'margin-bottom': 'margin',
            'margin-left': 'margin',
            'padding-top': 'padding',
            'padding-right': 'padding',
            'padding-bottom': 'padding',
            'padding-left': 'padding',
        }
    
    def optimize_properties(self, properties: Dict[str, str]) -> Dict[str, str]:
        """
        Optimize properties by combining to shorthands where possible.
        
        Args:
            properties: CSS properties
            
        Returns:
            Optimized properties
        """
        optimized = {}
        
        # Check for margin shorthand opportunity
        margin_props = {
            'margin-top': properties.get('margin-top'),
            'margin-right': properties.get('margin-right'),
            'margin-bottom': properties.get('margin-bottom'),
            'margin-left': properties.get('margin-left')
        }
        
        if all(v is not None for v in margin_props.values()):
            # Can combine to shorthand
            values = [
                margin_props['margin-top'],
                margin_props['margin-right'],
                margin_props['margin-bottom'],
                margin_props['margin-left']
            ]
            
            # Optimize shorthand value
            if values[0] == values[2] and values[1] == values[3]:
                if values[0] == values[1]:
                    optimized['margin'] = values[0]
                else:
                    optimized['margin'] = f'{values[0]} {values[1]}'
            else:
                optimized['margin'] = ' '.join(values)
        else:
            # Keep individual properties
            for key, value in margin_props.items():
                if value is not None:
                    optimized[key] = value
        
        # Check for padding shorthand opportunity
        padding_props = {
            'padding-top': properties.get('padding-top'),
            'padding-right': properties.get('padding-right'),
            'padding-bottom': properties.get('padding-bottom'),
            'padding-left': properties.get('padding-left')
        }
        
        if all(v is not None for v in padding_props.values()):
            # Can combine to shorthand
            values = [
                padding_props['padding-top'],
                padding_props['padding-right'],
                padding_props['padding-bottom'],
                padding_props['padding-left']
            ]
            
            # Optimize shorthand value
            if values[0] == values[2] and values[1] == values[3]:
                if values[0] == values[1]:
                    optimized['padding'] = values[0]
                else:
                    optimized['padding'] = f'{values[0]} {values[1]}'
            else:
                optimized['padding'] = ' '.join(values)
        else:
            # Keep individual properties
            for key, value in padding_props.items():
                if value is not None:
                    optimized[key] = value
        
        # Add other properties
        skip_props = set(self.shorthand_map.keys())
        for key, value in properties.items():
            if key not in skip_props:
                optimized[key] = value
        
        return optimized
    
    def remove_defaults(self, properties: Dict[str, str]) -> Dict[str, str]:
        """
        Remove properties with default values.
        
        Args:
            properties: CSS properties
            
        Returns:
            Properties without defaults
        """
        defaults = {
            'margin': '0',
            'padding': '0',
            'border': 'none',
            'background': 'none',
            'outline': 'none'
        }
        
        result = {}
        for key, value in properties.items():
            if key not in defaults or value != defaults[key]:
                result[key] = value
        
        return result