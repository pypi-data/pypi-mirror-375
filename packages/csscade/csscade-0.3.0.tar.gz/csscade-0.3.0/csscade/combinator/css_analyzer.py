"""CSS analyzer for parsing and caching CSS rules."""

from typing import Dict, List, Set, Optional, Union
import cssutils
import logging
import os
from pathlib import Path

# Suppress cssutils warnings
cssutils.log.setLevel(logging.ERROR)


class CSSAnalyzer:
    """Analyzes CSS files and builds property mappings for conflict detection."""
    
    def __init__(self):
        """Initialize the CSS analyzer."""
        self._css_cache = {}  # filename -> parsed stylesheet
        self._class_to_props = {}  # class_name -> {property: value}
        self._merged_rules = []  # All rules from all loaded CSS files
        
    def load_css(self, css_sources: List[Union[str, Path]]) -> None:
        """
        Load and parse CSS files, building property mappings.
        
        Args:
            css_sources: List of CSS file paths or CSS strings
        """
        for source in css_sources:
            self._load_single_css(source)
        
        # Build the class to properties mapping after loading all CSS
        self._build_class_map()
    
    def _load_single_css(self, source: Union[str, Path]) -> None:
        """
        Load a single CSS file or string.
        
        Args:
            source: CSS file path or CSS string
        """
        if isinstance(source, Path):
            # It's a Path object
            if source.exists() and source.is_file():
                cache_key = str(source)
                if cache_key not in self._css_cache:
                    with open(source, 'r', encoding='utf-8') as f:
                        css_content = f.read()
                    self._parse_css_content(css_content, cache_key)
        elif isinstance(source, str):
            # Check if it looks like CSS content or a file path
            # CSS content typically contains { and } or starts with whitespace/comments
            if '{' in source or '}' in source or source.strip().startswith(('.', '#', '/*', '@')):
                # Treat as CSS string
                self._parse_css_content(source, f"string_{len(self._css_cache)}")
            else:
                # Try as file path
                try:
                    source_path = Path(source)
                    if source_path.exists() and source_path.is_file():
                        cache_key = str(source_path)
                        if cache_key not in self._css_cache:
                            with open(source_path, 'r', encoding='utf-8') as f:
                                css_content = f.read()
                            self._parse_css_content(css_content, cache_key)
                    else:
                        # Not a valid file, treat as CSS string anyway
                        self._parse_css_content(source, f"string_{len(self._css_cache)}")
                except (OSError, ValueError):
                    # Path creation failed, treat as CSS string
                    self._parse_css_content(source, f"string_{len(self._css_cache)}")
    
    def _parse_css_content(self, css_content: str, cache_key: str) -> None:
        """
        Parse CSS content and cache the results.
        
        Args:
            css_content: CSS string to parse
            cache_key: Key for caching the parsed stylesheet
        """
        try:
            sheet = cssutils.parseString(css_content)
            self._css_cache[cache_key] = sheet
            
            # Extract rules from this stylesheet
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    self._merged_rules.append(rule)
                    
        except Exception as e:
            # Log error but continue - partial CSS is better than none
            print(f"Warning: Error parsing CSS ({cache_key}): {e}")
    
    def _build_class_map(self) -> None:
        """Build the mapping of class names to their CSS properties."""
        self._class_to_props = {}
        
        for rule in self._merged_rules:
            # Process each selector in the rule
            selectors = self._parse_selectors(rule.selectorText)
            
            # Extract properties from the rule
            properties = {}
            for prop in rule.style:
                properties[prop.name] = prop.value
            
            # Map each class selector to its properties
            for selector in selectors:
                if selector.startswith('.'):
                    # It's a class selector
                    class_name = self._extract_class_name(selector)
                    
                    if class_name not in self._class_to_props:
                        self._class_to_props[class_name] = {}
                    
                    # Merge properties (later rules override earlier ones)
                    self._class_to_props[class_name].update(properties)
    
    def _parse_selectors(self, selector_text: str) -> List[str]:
        """
        Parse a selector string into individual selectors.
        
        Args:
            selector_text: CSS selector string (may contain commas)
            
        Returns:
            List of individual selectors
        """
        # Split by comma and clean up
        selectors = [s.strip() for s in selector_text.split(',')]
        return selectors
    
    def _extract_class_name(self, selector: str) -> str:
        """
        Extract the class name from a selector.
        
        Args:
            selector: CSS selector starting with '.'
            
        Returns:
            The class name without the dot and without pseudo-selectors
        """
        # Remove the leading dot
        class_part = selector[1:]
        
        # Remove pseudo-selectors and pseudo-elements
        # Split by : or [ to handle pseudo-selectors and attribute selectors
        for delimiter in [':', '[', ' ', '>', '~', '+']:
            if delimiter in class_part:
                class_part = class_part.split(delimiter)[0]
        
        return class_part
    
    def get_class_properties(self) -> Dict[str, Dict[str, str]]:
        """
        Get the mapping of class names to their CSS properties.
        
        Returns:
            Dictionary mapping class names to their properties
        """
        return self._class_to_props.copy()
    
    def get_properties_for_class(self, class_name: str) -> Dict[str, str]:
        """
        Get CSS properties for a specific class.
        
        Args:
            class_name: The class name (without the dot)
            
        Returns:
            Dictionary of CSS properties and values
        """
        return self._class_to_props.get(class_name, {})
    
    def get_property_names_for_class(self, class_name: str) -> Set[str]:
        """
        Get just the property names (not values) for a class.
        
        Args:
            class_name: The class name (without the dot)
            
        Returns:
            Set of CSS property names
        """
        return set(self._class_to_props.get(class_name, {}).keys())
    
    def clear_cache(self) -> None:
        """Clear all cached CSS data."""
        self._css_cache.clear()
        self._class_to_props.clear()
        self._merged_rules.clear()
    
    def get_loaded_files(self) -> List[str]:
        """
        Get list of loaded CSS files.
        
        Returns:
            List of cache keys (file paths or string identifiers)
        """
        return list(self._css_cache.keys())
    
    def has_class(self, class_name: str) -> bool:
        """
        Check if a class exists in the loaded CSS.
        
        Args:
            class_name: The class name (without the dot)
            
        Returns:
            True if the class exists, False otherwise
        """
        return class_name in self._class_to_props