"""CSS selector parsing and analysis."""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum


class SelectorType(Enum):
    """Types of CSS selectors."""
    SIMPLE = "simple"           # .class, #id, tag
    PSEUDO = "pseudo"           # :hover, :focus, ::before
    ATTRIBUTE = "attribute"     # [attr=value]
    COMPLEX = "complex"         # combinators: >, +, ~, space
    COMPOUND = "compound"       # multiple simple selectors combined
    MEDIA = "media"            # @media queries
    KEYFRAMES = "keyframes"    # @keyframes
    UNKNOWN = "unknown"


class SelectorParser:
    """Parse and analyze CSS selectors to determine mergeability."""
    
    def __init__(self):
        """Initialize the selector parser."""
        # Patterns for different selector types
        self.patterns = {
            'class': re.compile(r'^\.[a-zA-Z][\w-]*$'),
            'id': re.compile(r'^#[a-zA-Z][\w-]*$'),
            'tag': re.compile(r'^[a-zA-Z][\w-]*$'),
            'pseudo_class': re.compile(r':[\w-]+(\([^)]*\))?'),
            'pseudo_element': re.compile(r'::[\w-]+'),
            'attribute': re.compile(r'\[[^\]]+\]'),
            'combinator': re.compile(r'[>+~\s]+'),
            'media': re.compile(r'^@media\s+'),
            'keyframes': re.compile(r'^@keyframes\s+'),
        }
        
        # Pseudo-classes that can't be merged with class overrides
        self.unmergeable_pseudos = {
            ':hover', ':focus', ':active', ':visited', ':link',
            ':checked', ':disabled', ':enabled', ':target',
            ':first-child', ':last-child', ':nth-child',
            ':first-of-type', ':last-of-type', ':nth-of-type',
            '::before', '::after', '::first-letter', '::first-line'
        }
    
    def parse(self, selector: str) -> Dict[str, any]:
        """
        Parse a CSS selector and determine its characteristics.
        
        Args:
            selector: CSS selector string
            
        Returns:
            Dictionary with parsing results:
                - type: SelectorType
                - mergeable: Whether it can be merged with class override
                - fallback: Suggested fallback strategy
                - components: Parsed components of the selector
                - specificity: Specificity score
        """
        selector = selector.strip()
        
        # Check for at-rules
        if selector.startswith('@'):
            if self.patterns['media'].match(selector):
                return self._parse_media_query(selector)
            elif self.patterns['keyframes'].match(selector):
                return self._parse_keyframes(selector)
            else:
                return {
                    'type': SelectorType.UNKNOWN,
                    'mergeable': False,
                    'fallback': 'inline',
                    'components': [],
                    'specificity': 0
                }
        
        # Check for simple selectors
        if self.patterns['class'].match(selector):
            return {
                'type': SelectorType.SIMPLE,
                'subtype': 'class',
                'mergeable': True,
                'fallback': None,
                'components': [selector],
                'specificity': self._calculate_specificity(selector)
            }
        
        if self.patterns['id'].match(selector):
            return {
                'type': SelectorType.SIMPLE,
                'subtype': 'id',
                'mergeable': True,
                'fallback': None,
                'components': [selector],
                'specificity': self._calculate_specificity(selector)
            }
        
        if self.patterns['tag'].match(selector) and ' ' not in selector:
            return {
                'type': SelectorType.SIMPLE,
                'subtype': 'tag',
                'mergeable': True,
                'fallback': None,
                'components': [selector],
                'specificity': self._calculate_specificity(selector)
            }
        
        # Check for pseudo-classes/elements
        if self._contains_pseudo(selector):
            return self._parse_pseudo_selector(selector)
        
        # Check for attribute selectors
        if self.patterns['attribute'].search(selector):
            return self._parse_attribute_selector(selector)
        
        # Check for complex selectors (combinators)
        if self._contains_combinator(selector):
            return self._parse_complex_selector(selector)
        
        # Compound selector (multiple simple selectors)
        if self._is_compound(selector):
            return self._parse_compound_selector(selector)
        
        # Unknown selector type
        return {
            'type': SelectorType.UNKNOWN,
            'mergeable': False,
            'fallback': 'inline',
            'components': [selector],
            'specificity': 0
        }
    
    def _contains_pseudo(self, selector: str) -> bool:
        """Check if selector contains pseudo-class or pseudo-element."""
        return bool(self.patterns['pseudo_class'].search(selector) or 
                   self.patterns['pseudo_element'].search(selector))
    
    def _contains_combinator(self, selector: str) -> bool:
        """Check if selector contains combinators."""
        # Look for >, +, ~ or multiple spaces indicating descendant combinator
        return bool(re.search(r'[>+~]|\s+[a-zA-Z#.\[]', selector))
    
    def _is_compound(self, selector: str) -> bool:
        """Check if selector is a compound selector."""
        # Multiple classes, or class with tag, etc.
        return bool(re.match(r'^[a-zA-Z]*(\.[a-zA-Z][\w-]*)+$', selector) or
                   re.match(r'^[a-zA-Z]+#[a-zA-Z][\w-]*$', selector))
    
    def _parse_pseudo_selector(self, selector: str) -> Dict[str, any]:
        """Parse selector with pseudo-class or pseudo-element."""
        # Extract base selector and pseudo parts
        base_match = re.match(r'^([^:]+)(:.*)$', selector)
        
        if base_match:
            base = base_match.group(1)
            pseudo = base_match.group(2)
            
            # Check if pseudo is unmergeable
            for unmergeable in self.unmergeable_pseudos:
                if pseudo.startswith(unmergeable):
                    return {
                        'type': SelectorType.PSEUDO,
                        'base': base,
                        'pseudo': pseudo,
                        'mergeable': False,
                        'fallback': 'inline',
                        'components': [base, pseudo],
                        'specificity': self._calculate_specificity(selector)
                    }
            
            # Some pseudo-classes might be mergeable
            return {
                'type': SelectorType.PSEUDO,
                'base': base,
                'pseudo': pseudo,
                'mergeable': True,
                'fallback': None,
                'components': [base, pseudo],
                'specificity': self._calculate_specificity(selector)
            }
        
        return {
            'type': SelectorType.PSEUDO,
            'mergeable': False,
            'fallback': 'inline',
            'components': [selector],
            'specificity': self._calculate_specificity(selector)
        }
    
    def _parse_attribute_selector(self, selector: str) -> Dict[str, any]:
        """Parse attribute selector."""
        return {
            'type': SelectorType.ATTRIBUTE,
            'mergeable': False,
            'fallback': 'inline',
            'components': self._extract_components(selector),
            'specificity': self._calculate_specificity(selector)
        }
    
    def _parse_complex_selector(self, selector: str) -> Dict[str, any]:
        """Parse complex selector with combinators."""
        components = self._extract_components(selector)
        
        return {
            'type': SelectorType.COMPLEX,
            'mergeable': False,
            'fallback': 'inline',
            'components': components,
            'specificity': self._calculate_specificity(selector)
        }
    
    def _parse_compound_selector(self, selector: str) -> Dict[str, any]:
        """Parse compound selector."""
        components = self._extract_components(selector)
        
        # Compound selectors might be mergeable in some cases
        mergeable = not self._contains_pseudo(selector)
        
        return {
            'type': SelectorType.COMPOUND,
            'mergeable': mergeable,
            'fallback': 'inline' if not mergeable else None,
            'components': components,
            'specificity': self._calculate_specificity(selector)
        }
    
    def _parse_media_query(self, selector: str) -> Dict[str, any]:
        """Parse media query."""
        return {
            'type': SelectorType.MEDIA,
            'mergeable': False,
            'fallback': 'preserve',
            'components': [selector],
            'specificity': 0  # Media queries don't have specificity
        }
    
    def _parse_keyframes(self, selector: str) -> Dict[str, any]:
        """Parse keyframes."""
        return {
            'type': SelectorType.KEYFRAMES,
            'mergeable': False,
            'fallback': 'preserve',
            'components': [selector],
            'specificity': 0  # Keyframes don't have specificity
        }
    
    def _extract_components(self, selector: str) -> List[str]:
        """Extract individual components from a selector."""
        # Split by combinators but keep them
        components = re.split(r'(\s*[>+~]\s*|\s+)', selector)
        return [c for c in components if c.strip()]
    
    def _calculate_specificity(self, selector: str) -> Tuple[int, int, int]:
        """
        Calculate CSS specificity (a, b, c).
        
        Args:
            selector: CSS selector string
            
        Returns:
            Tuple of (id_count, class_count, element_count)
        """
        # Count IDs
        id_count = len(re.findall(r'#[\w-]+', selector))
        
        # Count classes, attributes, and pseudo-classes
        class_count = len(re.findall(r'\.[\w-]+', selector))
        class_count += len(re.findall(r'\[[^\]]+\]', selector))
        class_count += len(re.findall(r':(?!:)[\w-]+(\([^)]*\))?', selector))
        
        # Count elements and pseudo-elements
        # Remove classes, IDs, attributes, and pseudo stuff first
        clean = re.sub(r'[#.][\w-]+', '', selector)
        clean = re.sub(r'\[[^\]]+\]', '', clean)
        clean = re.sub(r'::?[\w-]+(\([^)]*\))?', '', clean)
        clean = re.sub(r'[>+~\s]+', ' ', clean)
        
        elements = [e for e in clean.split() if e and not e.startswith(':')]
        element_count = len(elements)
        
        return (id_count, class_count, element_count)
    
    def can_merge(self, selector: str) -> bool:
        """
        Determine if a selector can be merged with class override.
        
        Args:
            selector: CSS selector string
            
        Returns:
            True if mergeable, False otherwise
        """
        result = self.parse(selector)
        return result['mergeable']
    
    def get_fallback_strategy(self, selector: str) -> str:
        """
        Get the fallback strategy for a non-mergeable selector.
        
        Args:
            selector: CSS selector string
            
        Returns:
            Fallback strategy name ('inline', 'important', 'preserve')
        """
        result = self.parse(selector)
        return result.get('fallback', 'inline')