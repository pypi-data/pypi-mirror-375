"""Main Combinator class for intelligent CSS class conflict resolution."""

from typing import Dict, List, Optional, Union
from pathlib import Path
from html.parser import HTMLParser

from .css_analyzer import CSSAnalyzer
from .conflict_detector import ConflictDetector


class Combinator:
    """
    Intelligent CSS class conflict detector and override generator.
    
    The Combinator analyzes existing CSS classes on an element, detects conflicts
    with desired overrides, and generates appropriate CSS to apply the overrides.
    """
    
    def __init__(self):
        """Initialize the Combinator."""
        self.analyzer = CSSAnalyzer()
        self.detector = ConflictDetector()
        self._css_loaded = False
    
    def load_css(self, css_sources: List[Union[str, Path]]) -> None:
        """
        Load and cache CSS files for analysis.
        
        Args:
            css_sources: List of CSS file paths or CSS strings
        """
        self.analyzer.load_css(css_sources)
        self._css_loaded = True
    
    def process(
        self,
        element_classes: List[str],
        overrides: Dict,
        element_id: str
    ) -> Dict:
        """
        Process CSS overrides for an element with existing classes.
        
        Args:
            element_classes: List of CSS class names on the element
            overrides: Dictionary of CSS properties to override (may include pseudo-selectors)
            element_id: Unique identifier for generating the override class name
            
        Returns:
            Dictionary containing:
                - remove_classes: Classes to remove due to conflicts
                - keep_classes: Classes to keep (no conflicts)
                - add_classes: New override class to add
                - generated_css: CSS rules for the override class
                - fallback_inline: Inline styles for non-pseudo properties
                - conflicts_found: List of conflict descriptions
        """
        if not self._css_loaded:
            raise RuntimeError("No CSS loaded. Call load_css() first.")
        
        # Get class properties from analyzer
        class_properties = self.analyzer.get_class_properties()
        
        # Detect conflicts
        conflicts = self.detector.find_conflicts(
            element_classes,
            overrides,
            class_properties
        )
        
        # Determine which classes to remove/keep
        remove_classes = list(conflicts.keys())
        keep_classes = [c for c in element_classes if c not in remove_classes]
        
        # Generate override class name
        override_class = f"csso-{element_id}"
        
        # Generate CSS for the override class
        generated_css = self._generate_css(
            override_class,
            overrides,
            conflicts
        )
        
        # Generate inline style fallback
        fallback_inline = self._generate_inline_fallback(overrides)
        
        # Format conflict descriptions
        conflicts_found = []
        for class_name, props in conflicts.items():
            props_str = ', '.join(props)
            conflicts_found.append(f"{class_name} → {props_str}")
        
        return {
            'remove_classes': remove_classes,
            'keep_classes': keep_classes,
            'add_classes': [override_class],
            'generated_css': generated_css,
            'fallback_inline': fallback_inline,
            'conflicts_found': conflicts_found
        }
    
    def process_element(
        self,
        html: str,
        overrides: Dict,
        element_id: str
    ) -> Dict:
        """
        Process CSS overrides for an HTML element string.
        
        Args:
            html: HTML element string with classes
            overrides: Dictionary of CSS properties to override
            element_id: Unique identifier for generating the override class name
            
        Returns:
            Same as process() method
        """
        # Extract classes from HTML
        element_classes = self._extract_classes_from_html(html)
        
        # Process with extracted classes
        return self.process(element_classes, overrides, element_id)
    
    def process_batch(
        self,
        elements: List[Dict]
    ) -> List[Dict]:
        """
        Process multiple elements efficiently.
        
        Args:
            elements: List of dictionaries with 'element_classes', 'overrides', and 'element_id'
            
        Returns:
            List of results from process() for each element
        """
        results = []
        
        for element in elements:
            result = self.process(
                element_classes=element.get('element_classes', []),
                overrides=element.get('overrides', {}),
                element_id=element.get('element_id', 'unnamed')
            )
            results.append(result)
        
        return results
    
    def _generate_css(
        self,
        class_name: str,
        overrides: Dict,
        conflicts: Dict[str, List[str]]
    ) -> str:
        """
        Generate CSS rules for the override class.
        
        Args:
            class_name: The override class name
            overrides: Dictionary of CSS properties to override
            conflicts: Dictionary of detected conflicts
            
        Returns:
            CSS string with the override rules
        """
        # Collect all conflicting properties for !important determination
        conflicting_props = set()
        for props in conflicts.values():
            conflicting_props.update(props)
        
        css_rules = []
        
        # Process base properties
        base_props = {}
        pseudo_rules = {}
        media_queries = {}
        
        for key, value in overrides.items():
            if key.startswith(':'):
                # It's a pseudo-selector
                pseudo_rules[key] = value
            elif key.startswith('@'):
                # It's a media query
                media_queries[key] = value
            else:
                # Regular property
                base_props[key] = value
        
        # Generate base rule if there are base properties
        if base_props:
            css = f".{class_name} {{\n"
            for prop, value in base_props.items():
                importance = " !important" if prop in conflicting_props else ""
                css += f"    {prop}: {value}{importance};\n"
            css += "}"
            css_rules.append(css)
        
        # Generate pseudo-selector rules
        for pseudo, props in pseudo_rules.items():
            if isinstance(props, dict):
                css = f".{class_name}{pseudo} {{\n"
                for prop, value in props.items():
                    # Check if this pseudo-property had conflicts
                    importance = " !important" if prop in conflicting_props else ""
                    css += f"    {prop}: {value}{importance};\n"
                css += "}"
                css_rules.append(css)
        
        # Generate media query rules
        for media_query, props in media_queries.items():
            if isinstance(props, dict):
                css = f"{media_query} {{\n"
                css += f"    .{class_name} {{\n"
                for prop, value in props.items():
                    # Check if this property had conflicts
                    importance = " !important" if prop in conflicting_props else ""
                    css += f"        {prop}: {value}{importance};\n"
                css += "    }\n"
                css += "}"
                css_rules.append(css)
        
        return '\n'.join(css_rules)
    
    def _generate_inline_fallback(self, overrides: Dict) -> Dict[str, str]:
        """
        Generate inline style fallback for non-pseudo properties.
        
        Args:
            overrides: Dictionary of CSS properties to override
            
        Returns:
            Dictionary of camelCase property names to values
        """
        inline = {}
        
        for key, value in overrides.items():
            # Skip pseudo-selectors, pseudo-elements, and media queries
            if not key.startswith(':') and not key.startswith('@'):
                # Convert to camelCase for React/JS compatibility
                camel_key = self._to_camel_case(key)
                inline[camel_key] = value
        
        return inline
    
    def _to_camel_case(self, css_prop: str) -> str:
        """
        Convert CSS property name to camelCase.
        
        Args:
            css_prop: CSS property name (e.g., 'background-color')
            
        Returns:
            camelCase property name (e.g., 'backgroundColor')
        """
        parts = css_prop.split('-')
        # First part stays lowercase, rest are capitalized
        return parts[0] + ''.join(part.capitalize() for part in parts[1:])
    
    def _extract_classes_from_html(self, html: str) -> List[str]:
        """
        Extract CSS classes from an HTML element string.
        
        Args:
            html: HTML element string
            
        Returns:
            List of CSS class names
        """
        class ClassExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.classes = []
                
            def handle_starttag(self, tag, attrs):
                for attr_name, attr_value in attrs:
                    if attr_name == 'class' and attr_value:
                        self.classes = attr_value.split()
        
        extractor = ClassExtractor()
        extractor.feed(html)
        
        return extractor.classes
    
    def clear_cache(self) -> None:
        """Clear all cached CSS data."""
        self.analyzer.clear_cache()
        self._css_loaded = False
    
    def get_loaded_files(self) -> List[str]:
        """
        Get list of loaded CSS files.
        
        Returns:
            List of loaded file paths or identifiers
        """
        return self.analyzer.get_loaded_files()