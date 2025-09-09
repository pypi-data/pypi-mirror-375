"""Base strategy class for CSS merging strategies."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Union, List, Optional
from csscade.models import CSSProperty, CSSRule


class MergeStrategy(ABC):
    """Abstract base class for CSS merge strategies."""
    
    def __init__(
        self, 
        conflict_resolution: Optional[Dict[str, Any]] = None,
        naming: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the merge strategy.
        
        Args:
            conflict_resolution: Conflict resolution configuration
            naming: Naming configuration for class generation
        """
        self.conflict_resolution = conflict_resolution or {}
        self.naming = naming or {}
        self.conflict_resolver = None
        
        # Initialize conflict resolver if config provided
        if self.conflict_resolution:
            from csscade.resolvers.conflict_resolver import ConflictResolver
            self.conflict_resolver = ConflictResolver(self.conflict_resolution)
    
    @abstractmethod
    def merge(
        self,
        source: Union[str, CSSRule, Dict[str, str], List[CSSProperty]],
        override: Union[Dict[str, str], List[CSSProperty], str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Merge CSS properties according to the strategy.
        
        Args:
            source: Source CSS (can be rule, properties, or string)
            override: Override properties
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            Dictionary with merge results including:
                - css: Generated CSS string (optional)
                - add: Classes to add (optional)
                - remove: Classes to remove (optional)
                - preserve: Classes to preserve (optional)
                - inline: Inline styles to apply (optional)
                - important: Important styles to apply (optional)
                - warnings: Warning messages (optional)
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        Get the name of this strategy.
        
        Returns:
            Strategy name
        """
        pass
    
    def validate_input(
        self,
        source: Any,
        override: Any
    ) -> bool:
        """
        Validate input parameters.
        
        Args:
            source: Source input
            override: Override input
            
        Returns:
            True if valid, raises exception otherwise
        """
        if source is None:
            raise ValueError("Source cannot be None")
        if override is None:
            raise ValueError("Override cannot be None")
        return True
    
    def prepare_result(
        self,
        css: Optional[str] = None,
        add_classes: Optional[List[str]] = None,
        remove_classes: Optional[List[str]] = None,
        preserve_classes: Optional[List[str]] = None,
        inline_styles: Optional[Dict[str, str]] = None,
        important_styles: Optional[Dict[str, str]] = None,
        warnings: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Prepare the result dictionary.
        
        Args:
            css: Generated CSS
            add_classes: Classes to add
            remove_classes: Classes to remove
            preserve_classes: Classes to preserve
            inline_styles: Inline styles
            important_styles: Important styles
            warnings: Warning messages
            
        Returns:
            Formatted result dictionary
        """
        result = {}
        
        if css is not None:
            result["css"] = css
        if add_classes:
            result["add"] = add_classes
        if remove_classes:
            result["remove"] = remove_classes
        if preserve_classes:
            result["preserve"] = preserve_classes
        if inline_styles:
            result["inline"] = inline_styles
        if important_styles:
            result["important"] = important_styles
        if warnings:
            result["warnings"] = warnings
            
        return result