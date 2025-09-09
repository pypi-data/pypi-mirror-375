"""Conflict resolution system for CSS merging strategies."""

from typing import Dict, List, Union, Optional, Any, Tuple
from enum import Enum
from csscade.models import CSSProperty, CSSRule


class ResolutionStrategy(Enum):
    """Available resolution strategies for different conflict types."""
    
    # Pseudo selector strategies
    PRESERVE = "preserve"      # Keep pseudo selectors as separate rules
    INLINE = "inline"          # Convert to inline styles for runtime
    IGNORE = "ignore"          # Skip pseudo selectors entirely
    FORCE_MERGE = "force_merge"  # Merge anyway (loses pseudo state)
    EXTRACT = "extract"        # Extract to separate object
    
    # Media query strategies
    DUPLICATE = "duplicate"     # Create duplicate rules for each media query
    
    # !important strategies
    RESPECT = "respect"        # !important always wins
    OVERRIDE = "override"      # Override always wins (ignore !important)
    WARN = "warn"             # Warn and skip
    STRIP = "strip"           # Remove !important flag
    
    # Shorthand strategies
    EXPAND = "expand"         # Expand shorthands to longhands
    SMART = "smart"           # Intelligently merge shorthands
    CASCADE = "cascade"       # Use CSS cascade (append after)
    
    # Multiple rules strategies
    FIRST = "first"           # Apply to first matching rule only
    ALL = "all"               # Apply to all matching rules
    MOST_SPECIFIC = "most_specific"  # Apply to most specific selector


class ConflictResolver:
    """
    Resolves CSS conflicts based on configured strategies.
    Supports fallback chains for graceful degradation.
    """
    
    # Default strategies with fallback chains
    DEFAULT_STRATEGIES = {
        'pseudo': ['preserve', 'inline'],      # Try preserve, fallback to inline
        'media': ['preserve', 'extract'],      # Try preserve, fallback to extract
        'important': ['respect', 'warn'],      # Try respect, fallback to warn
        'shorthand': ['smart', 'cascade'],     # Try smart merge, fallback to cascade
        'multiple_rules': ['first']            # Default to first rule
    }
    
    def __init__(self, strategies: Optional[Dict[str, Union[str, List[str]]]] = None):
        """
        Initialize conflict resolver with strategies.
        
        Args:
            strategies: Dict of conflict types to resolution strategies.
                       Can be single strategy or list for fallback chain.
        """
        self.strategies = self._normalize_strategies(strategies or {})
        self.resolution_log = []
        
    def _normalize_strategies(self, strategies: Dict) -> Dict[str, List[str]]:
        """
        Normalize strategies to always be lists (for fallback support).
        
        Args:
            strategies: Raw strategy configuration
            
        Returns:
            Normalized strategies with defaults
        """
        normalized = {}
        
        for conflict_type, strategy in strategies.items():
            if isinstance(strategy, str):
                normalized[conflict_type] = [strategy]
            elif isinstance(strategy, list):
                normalized[conflict_type] = strategy
            else:
                raise ValueError(f"Invalid strategy type for {conflict_type}: {type(strategy)}")
        
        # Apply defaults for missing strategies
        for conflict_type, default in self.DEFAULT_STRATEGIES.items():
            if conflict_type not in normalized:
                normalized[conflict_type] = default
                
        return normalized
    
    def resolve_pseudo_conflict(
        self,
        source_rule: CSSRule,
        override_props: List[CSSProperty],
        pseudo_part: str
    ) -> Dict[str, Any]:
        """
        Resolve conflicts with pseudo selectors.
        
        Args:
            source_rule: Source CSS rule with pseudo selector
            override_props: Override properties
            pseudo_part: The pseudo selector part (e.g., ':hover')
            
        Returns:
            Resolution result with strategy used
        """
        strategies = self.strategies.get('pseudo', ['preserve'])
        
        for strategy in strategies:
            try:
                if strategy == 'preserve':
                    # Keep pseudo selector, create new rule
                    return {
                        'strategy': 'preserve',
                        'action': 'create_pseudo_rule',
                        'preserve_pseudo': True,
                        'message': f"Preserving {pseudo_part} as separate rule"
                    }
                    
                elif strategy == 'inline':
                    # Convert to inline styles for runtime application
                    return {
                        'strategy': 'inline',
                        'action': 'convert_to_inline',
                        'inline_styles': self._properties_to_dict(override_props),
                        'pseudo_state': pseudo_part,
                        'message': f"Converting {pseudo_part} to inline styles for runtime"
                    }
                    
                elif strategy == 'ignore':
                    # Skip pseudo selector entirely
                    return {
                        'strategy': 'ignore',
                        'action': 'skip',
                        'message': f"Ignoring {pseudo_part} selector"
                    }
                    
                elif strategy == 'force_merge':
                    # Merge anyway, losing pseudo state
                    return {
                        'strategy': 'force_merge',
                        'action': 'merge_without_pseudo',
                        'warning': f"Forcing merge, {pseudo_part} state will be lost",
                        'message': f"Force merging, dropping {pseudo_part}"
                    }
                    
                elif strategy == 'extract':
                    # Extract to separate object
                    return {
                        'strategy': 'extract',
                        'action': 'extract_styles',
                        'extracted': {
                            'base': self._properties_to_dict(source_rule.properties),
                            pseudo_part: self._properties_to_dict(override_props)
                        },
                        'message': f"Extracting {pseudo_part} styles separately"
                    }
                    
            except Exception as e:
                # Log failure and try next strategy
                self.resolution_log.append(f"Strategy {strategy} failed: {e}")
                continue
        
        # All strategies failed, return error
        return {
            'strategy': 'failed',
            'action': 'error',
            'message': f"All resolution strategies failed for {pseudo_part}",
            'attempted': strategies
        }
    
    def resolve_media_conflict(
        self,
        source_rule: CSSRule,
        override_props: List[CSSProperty],
        media_query: str
    ) -> Dict[str, Any]:
        """
        Resolve conflicts with media queries.
        
        Args:
            source_rule: Source CSS rule with media query
            override_props: Override properties
            media_query: The media query string
            
        Returns:
            Resolution result with strategy used
        """
        strategies = self.strategies.get('media', ['preserve'])
        
        for strategy in strategies:
            try:
                if strategy == 'preserve':
                    # Keep media query intact
                    return {
                        'strategy': 'preserve',
                        'action': 'keep_media_query',
                        'media_query': media_query,
                        'message': f"Preserving media query: {media_query}"
                    }
                    
                elif strategy == 'inline':
                    # Convert to inline (for JS handling)
                    return {
                        'strategy': 'inline',
                        'action': 'convert_to_inline',
                        'breakpoint': self._parse_media_query(media_query),
                        'styles': self._properties_to_dict(override_props),
                        'message': "Converting media query for runtime handling"
                    }
                    
                elif strategy == 'duplicate':
                    # Create duplicate rules for each breakpoint
                    return {
                        'strategy': 'duplicate',
                        'action': 'duplicate_rules',
                        'message': "Creating duplicate rules for media queries"
                    }
                    
                elif strategy == 'extract':
                    # Extract to separate stylesheet
                    return {
                        'strategy': 'extract',
                        'action': 'extract_media',
                        'media_styles': {
                            media_query: self._properties_to_dict(override_props)
                        },
                        'message': f"Extracting media query styles"
                    }
                    
            except Exception as e:
                self.resolution_log.append(f"Strategy {strategy} failed: {e}")
                continue
        
        return {
            'strategy': 'failed',
            'action': 'error',
            'message': f"All resolution strategies failed for media query",
            'attempted': strategies
        }
    
    def resolve_important_conflict(
        self,
        source_prop: CSSProperty,
        override_prop: CSSProperty
    ) -> Dict[str, Any]:
        """
        Resolve conflicts with !important declarations.
        
        Args:
            source_prop: Source property (may have !important)
            override_prop: Override property (may have !important)
            
        Returns:
            Resolution result with winning property
        """
        strategies = self.strategies.get('important', ['respect'])
        
        source_important = source_prop.important if hasattr(source_prop, 'important') else False
        override_important = override_prop.important if hasattr(override_prop, 'important') else False
        
        for strategy in strategies:
            try:
                if strategy == 'respect':
                    # !important always wins
                    if source_important and not override_important:
                        return {
                            'strategy': 'respect',
                            'winner': 'source',
                            'property': source_prop,
                            'message': "Source wins due to !important"
                        }
                    else:
                        return {
                            'strategy': 'respect',
                            'winner': 'override',
                            'property': override_prop,
                            'message': "Override wins (both or neither !important)"
                        }
                        
                elif strategy == 'override':
                    # Override always wins, ignore !important
                    return {
                        'strategy': 'override',
                        'winner': 'override',
                        'property': override_prop,
                        'message': "Override wins (ignoring !important)"
                    }
                    
                elif strategy == 'warn':
                    # Warn about conflict
                    if source_important:
                        return {
                            'strategy': 'warn',
                            'winner': 'source',
                            'property': source_prop,
                            'warning': "Source has !important, override skipped",
                            'message': "Warning: !important conflict"
                        }
                    else:
                        return {
                            'strategy': 'warn',
                            'winner': 'override',
                            'property': override_prop,
                            'message': "Override applied"
                        }
                        
                elif strategy == 'strip':
                    # Remove !important flag
                    clean_prop = CSSProperty(
                        name=override_prop.name,
                        value=override_prop.value,
                        important=False
                    )
                    return {
                        'strategy': 'strip',
                        'winner': 'override',
                        'property': clean_prop,
                        'message': "Stripped !important flag"
                    }
                    
            except Exception as e:
                self.resolution_log.append(f"Strategy {strategy} failed: {e}")
                continue
        
        return {
            'strategy': 'failed',
            'action': 'error',
            'message': "All resolution strategies failed for !important",
            'attempted': strategies
        }
    
    def resolve_shorthand_conflict(
        self,
        shorthand: str,
        longhand: str,
        source_value: str,
        override_value: str
    ) -> Dict[str, Any]:
        """
        Resolve conflicts between shorthand and longhand properties.
        
        Args:
            shorthand: Shorthand property name
            longhand: Longhand property name
            source_value: Source value
            override_value: Override value
            
        Returns:
            Resolution result
        """
        strategies = self.strategies.get('shorthand', ['smart'])
        
        for strategy in strategies:
            try:
                if strategy == 'expand':
                    # Expand shorthand to longhands
                    return {
                        'strategy': 'expand',
                        'action': 'expand_shorthand',
                        'message': f"Expanding {shorthand} to longhands"
                    }
                    
                elif strategy == 'smart':
                    # Intelligently merge
                    return {
                        'strategy': 'smart',
                        'action': 'smart_merge',
                        'message': f"Smart merging {shorthand} with {longhand}"
                    }
                    
                elif strategy == 'cascade':
                    # Use CSS cascade order
                    return {
                        'strategy': 'cascade',
                        'action': 'use_cascade',
                        'message': f"Using CSS cascade for {shorthand}/{longhand}"
                    }
                    
                elif strategy == 'preserve':
                    # Keep shorthand as-is
                    return {
                        'strategy': 'preserve',
                        'action': 'keep_shorthand',
                        'message': f"Preserving {shorthand}"
                    }
                    
            except Exception as e:
                self.resolution_log.append(f"Strategy {strategy} failed: {e}")
                continue
        
        return {
            'strategy': 'failed',
            'action': 'error',
            'message': "All resolution strategies failed for shorthand",
            'attempted': strategies
        }
    
    def resolve_multiple_rules(
        self,
        rules: List[CSSRule],
        override_props: List[CSSProperty]
    ) -> Dict[str, Any]:
        """
        Resolve how to handle multiple matching rules.
        
        Args:
            rules: List of matching CSS rules
            override_props: Override properties
            
        Returns:
            Resolution result
        """
        strategies = self.strategies.get('multiple_rules', ['first'])
        
        for strategy in strategies:
            try:
                if strategy == 'first':
                    return {
                        'strategy': 'first',
                        'target_rule': rules[0] if rules else None,
                        'message': "Applying to first matching rule"
                    }
                    
                elif strategy == 'all':
                    return {
                        'strategy': 'all',
                        'target_rules': rules,
                        'message': f"Applying to all {len(rules)} matching rules"
                    }
                    
                elif strategy == 'most_specific':
                    # Calculate specificity and pick highest
                    most_specific = self._find_most_specific(rules)
                    return {
                        'strategy': 'most_specific',
                        'target_rule': most_specific,
                        'message': f"Applying to most specific rule: {most_specific.selector}"
                    }
                    
            except Exception as e:
                self.resolution_log.append(f"Strategy {strategy} failed: {e}")
                continue
        
        return {
            'strategy': 'failed',
            'action': 'error',
            'message': "All resolution strategies failed for multiple rules",
            'attempted': strategies
        }
    
    def _properties_to_dict(self, properties: List[CSSProperty]) -> Dict[str, str]:
        """Convert list of CSSProperty to dict."""
        return {prop.name: prop.value for prop in properties}
    
    def _parse_media_query(self, query: str) -> Dict[str, Any]:
        """Parse media query into structured format."""
        # Simple parsing for now
        return {
            'raw': query,
            'type': 'screen' if 'screen' in query else 'all',
            'conditions': query
        }
    
    def _find_most_specific(self, rules: List[CSSRule]) -> Optional[CSSRule]:
        """Find the most specific CSS rule based on selector."""
        if not rules:
            return None
        
        # Simple specificity: count selector parts
        # In production, use proper specificity calculation
        def specificity(rule):
            selector = rule.selector
            return (
                selector.count('#'),  # IDs
                selector.count('.'),  # Classes
                len(selector.split())  # Elements
            )
        
        return max(rules, key=specificity)
    
    def get_resolution_log(self) -> List[str]:
        """Get the resolution log for debugging."""
        return self.resolution_log
    
    def clear_log(self):
        """Clear the resolution log."""
        self.resolution_log = []