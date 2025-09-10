"""Media query handling for CSS merging."""

import re
from typing import Dict, List, Any, Optional, Union, Tuple
from csscade.models import CSSProperty, CSSRule
from csscade.parser.css_parser import CSSParser
from csscade.generator.output import OutputFormatter


class MediaQueryHandler:
    """Handles media queries in CSS merging operations."""
    
    def __init__(self):
        """Initialize the media query handler."""
        self.parser = CSSParser()
        self.formatter = OutputFormatter()
        
        # Common media query patterns
        self.media_patterns = {
            'min_width': re.compile(r'min-width:\s*(\d+)(px|em|rem)'),
            'max_width': re.compile(r'max-width:\s*(\d+)(px|em|rem)'),
            'min_height': re.compile(r'min-height:\s*(\d+)(px|em|rem)'),
            'max_height': re.compile(r'max-height:\s*(\d+)(px|em|rem)'),
            'orientation': re.compile(r'orientation:\s*(portrait|landscape)'),
            'media_type': re.compile(r'(screen|print|all|speech)'),
        }
    
    def parse_media_query(self, media_query: str) -> Dict[str, Any]:
        """
        Parse a media query string.
        
        Args:
            media_query: Media query string (e.g., "@media (min-width: 768px)")
            
        Returns:
            Dictionary with parsed media query information
        """
        # Remove @media prefix if present
        query = media_query.strip()
        if query.startswith('@media'):
            query = query[6:].strip()
        
        result = {
            'original': media_query,
            'query': query,
            'conditions': [],
            'media_type': None,
            'features': {}
        }
        
        # Extract media type
        media_type_match = self.media_patterns['media_type'].search(query)
        if media_type_match:
            result['media_type'] = media_type_match.group(1)
        
        # Extract min-width
        min_width_match = self.media_patterns['min_width'].search(query)
        if min_width_match:
            result['features']['min-width'] = {
                'value': int(min_width_match.group(1)),
                'unit': min_width_match.group(2)
            }
            result['conditions'].append(f"min-width: {min_width_match.group(1)}{min_width_match.group(2)}")
        
        # Extract max-width
        max_width_match = self.media_patterns['max_width'].search(query)
        if max_width_match:
            result['features']['max-width'] = {
                'value': int(max_width_match.group(1)),
                'unit': max_width_match.group(2)
            }
            result['conditions'].append(f"max-width: {max_width_match.group(1)}{max_width_match.group(2)}")
        
        # Extract orientation
        orientation_match = self.media_patterns['orientation'].search(query)
        if orientation_match:
            result['features']['orientation'] = orientation_match.group(1)
            result['conditions'].append(f"orientation: {orientation_match.group(1)}")
        
        return result
    
    def handle_media_query_merge(
        self,
        media_query: str,
        selector: str,
        properties: Union[List[CSSProperty], Dict[str, str]],
        strategy: str = "preserve"
    ) -> Dict[str, Any]:
        """
        Handle merging properties within a media query.
        
        Args:
            media_query: Media query string
            selector: CSS selector within the media query
            properties: Properties to merge
            strategy: Merge strategy ('preserve', 'duplicate', 'inline')
            
        Returns:
            Merge result with appropriate handling
        """
        # Convert properties to list if needed
        if isinstance(properties, dict):
            prop_list = []
            for name, value in properties.items():
                if '!important' in value:
                    clean_value = value.replace('!important', '').strip()
                    prop_list.append(CSSProperty(name, clean_value, important=True))
                else:
                    prop_list.append(CSSProperty(name, value))
        else:
            prop_list = properties
        
        if strategy == "preserve":
            return self._handle_preserve_strategy(media_query, selector, prop_list)
        elif strategy == "duplicate":
            return self._handle_duplicate_strategy(media_query, selector, prop_list)
        elif strategy == "inline":
            return self._handle_inline_strategy(media_query, selector, prop_list)
        else:
            # Default to preserve
            return self._handle_preserve_strategy(media_query, selector, prop_list)
    
    def _handle_preserve_strategy(
        self,
        media_query: str,
        selector: str,
        properties: List[CSSProperty]
    ) -> Dict[str, Any]:
        """
        Preserve media query with merged properties.
        
        Args:
            media_query: Media query string
            selector: CSS selector
            properties: Properties to apply
            
        Returns:
            Result with preserved media query
        """
        # Create rule within media query
        rule = CSSRule(selector, properties)
        rule_css = self.formatter.format_rule(rule, format="css")
        
        # Wrap in media query
        if not media_query.startswith('@media'):
            media_query = f"@media {media_query}"
        
        css_output = f"{media_query} {{\n  {rule_css}\n}}"
        
        return {
            'css': css_output,
            'warnings': ['Media query preserved: Override applies to matching breakpoints']
        }
    
    def _handle_duplicate_strategy(
        self,
        media_query: str,
        selector: str,
        properties: List[CSSProperty]
    ) -> Dict[str, Any]:
        """
        Duplicate rules for different media queries.
        
        Args:
            media_query: Media query string
            selector: CSS selector
            properties: Properties to apply
            
        Returns:
            Result with duplicated rules
        """
        # Create rule for media query
        rule = CSSRule(selector, properties)
        media_css = self.formatter.format_rule(rule, format="css")
        
        # Also create rule without media query
        base_css = self.formatter.format_rule(rule, format="css")
        
        # Wrap media rule in query
        if not media_query.startswith('@media'):
            media_query = f"@media {media_query}"
        
        media_output = f"{media_query} {{\n  {media_css}\n}}"
        
        # Combine both
        css_output = f"{base_css}\n\n{media_output}"
        
        return {
            'css': css_output,
            'warnings': ['Rules duplicated for base and media query contexts']
        }
    
    def _handle_inline_strategy(
        self,
        media_query: str,
        selector: str,
        properties: List[CSSProperty]
    ) -> Dict[str, Any]:
        """
        Fall back to inline styles for media query overrides.
        
        Args:
            media_query: Media query string
            selector: CSS selector
            properties: Properties to apply
            
        Returns:
            Result with inline styles and warning
        """
        # Convert properties to dict for inline
        inline_props = {prop.name: prop.value for prop in properties}
        
        return {
            'inline': inline_props,
            'warnings': [
                f'Cannot apply media query "{media_query}" with class merge, '
                f'using inline styles (applies to all breakpoints)'
            ]
        }
    
    def extract_rules_from_media(self, css_text: str) -> List[Tuple[str, List[CSSRule]]]:
        """
        Extract rules from media queries in CSS text.
        
        Args:
            css_text: CSS text potentially containing media queries
            
        Returns:
            List of (media_query, rules) tuples
        """
        results = []
        
        # Pattern to match media queries
        media_pattern = re.compile(
            r'@media\s+([^{]+)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}',
            re.MULTILINE | re.DOTALL
        )
        
        for match in media_pattern.finditer(css_text):
            media_query = f"@media {match.group(1).strip()}"
            content = match.group(2)
            
            # Parse rules within media query
            try:
                rules = self.parser.parse_rule_string(content)
                if rules:
                    results.append((media_query, rules))
            except Exception:
                # Skip unparseable content
                continue
        
        return results
    
    def merge_media_queries(
        self,
        media_queries: List[Tuple[str, List[CSSRule]]]
    ) -> str:
        """
        Merge multiple media queries with the same conditions.
        
        Args:
            media_queries: List of (media_query, rules) tuples
            
        Returns:
            Merged CSS string
        """
        # Group by media query
        grouped = {}
        for query, rules in media_queries:
            if query not in grouped:
                grouped[query] = []
            grouped[query].extend(rules)
        
        # Format output
        output_parts = []
        for query, rules in grouped.items():
            rules_css = "\n  ".join(
                self.formatter.format_rule(rule, format="css")
                for rule in rules
            )
            output_parts.append(f"{query} {{\n  {rules_css}\n}}")
        
        return "\n\n".join(output_parts)
    
    def is_media_query(self, selector: str) -> bool:
        """
        Check if a selector is a media query.
        
        Args:
            selector: CSS selector or at-rule
            
        Returns:
            True if media query, False otherwise
        """
        return selector.strip().startswith('@media')
    
    def get_breakpoint_info(self, media_query: str) -> Dict[str, Any]:
        """
        Extract breakpoint information from media query.
        
        Args:
            media_query: Media query string
            
        Returns:
            Dictionary with breakpoint information
        """
        parsed = self.parse_media_query(media_query)
        
        info = {
            'type': 'custom',
            'min': None,
            'max': None,
            'orientation': None
        }
        
        # Determine breakpoint type
        features = parsed.get('features', {})
        
        if 'min-width' in features:
            min_val = features['min-width']['value']
            info['min'] = min_val
            
            # Common breakpoint sizes
            if min_val == 576:
                info['type'] = 'sm'
            elif min_val == 768:
                info['type'] = 'md'
            elif min_val == 992:
                info['type'] = 'lg'
            elif min_val == 1200:
                info['type'] = 'xl'
            elif min_val == 1400:
                info['type'] = 'xxl'
        
        if 'max-width' in features:
            info['max'] = features['max-width']['value']
        
        if 'orientation' in features:
            info['orientation'] = features['orientation']
        
        return info