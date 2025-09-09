"""Browser compatibility checking for CSS properties."""

from typing import Dict, List, Set, Tuple, Optional
from enum import Enum


class BrowserSupport(Enum):
    """Browser support levels."""
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"
    PREFIXED = "prefixed"
    UNKNOWN = "unknown"


class BrowserCompatChecker:
    """Check CSS properties for browser compatibility."""
    
    def __init__(self, target_browsers: Optional[List[str]] = None):
        """
        Initialize browser compatibility checker.
        
        Args:
            target_browsers: List of target browsers (e.g., ['chrome', 'firefox', 'safari'])
        """
        self.target_browsers = target_browsers or ['chrome', 'firefox', 'safari', 'edge']
        
        # Simplified compatibility data (real implementation would use caniuse-db)
        self.compatibility_data = {
            # Flexbox
            'display: flex': {
                'chrome': (21, BrowserSupport.FULL),
                'firefox': (20, BrowserSupport.FULL),
                'safari': (9, BrowserSupport.PREFIXED),
                'edge': (12, BrowserSupport.FULL),
                'ie': (11, BrowserSupport.PARTIAL)
            },
            'flex': {
                'chrome': (29, BrowserSupport.FULL),
                'firefox': (20, BrowserSupport.FULL),
                'safari': (9, BrowserSupport.PREFIXED),
                'edge': (12, BrowserSupport.FULL),
                'ie': (11, BrowserSupport.PARTIAL)
            },
            
            # Grid
            'display: grid': {
                'chrome': (57, BrowserSupport.FULL),
                'firefox': (52, BrowserSupport.FULL),
                'safari': (10.1, BrowserSupport.FULL),
                'edge': (16, BrowserSupport.FULL),
                'ie': (10, BrowserSupport.PARTIAL)
            },
            'grid-template-columns': {
                'chrome': (57, BrowserSupport.FULL),
                'firefox': (52, BrowserSupport.FULL),
                'safari': (10.1, BrowserSupport.FULL),
                'edge': (16, BrowserSupport.FULL),
                'ie': (10, BrowserSupport.PARTIAL)
            },
            
            # CSS Variables
            '--*': {  # Custom properties
                'chrome': (49, BrowserSupport.FULL),
                'firefox': (31, BrowserSupport.FULL),
                'safari': (9.1, BrowserSupport.FULL),
                'edge': (15, BrowserSupport.FULL),
                'ie': (None, BrowserSupport.NONE)
            },
            
            # Transform
            'transform': {
                'chrome': (36, BrowserSupport.FULL),
                'firefox': (16, BrowserSupport.FULL),
                'safari': (9, BrowserSupport.PREFIXED),
                'edge': (12, BrowserSupport.FULL),
                'ie': (10, BrowserSupport.PREFIXED)
            },
            
            # Newer properties
            'gap': {
                'chrome': (84, BrowserSupport.FULL),
                'firefox': (63, BrowserSupport.FULL),
                'safari': (14.1, BrowserSupport.FULL),
                'edge': (84, BrowserSupport.FULL),
                'ie': (None, BrowserSupport.NONE)
            },
            'aspect-ratio': {
                'chrome': (88, BrowserSupport.FULL),
                'firefox': (89, BrowserSupport.FULL),
                'safari': (15, BrowserSupport.FULL),
                'edge': (88, BrowserSupport.FULL),
                'ie': (None, BrowserSupport.NONE)
            }
        }
        
        # Properties that need vendor prefixes
        self.prefixed_properties = {
            'transform': ['-webkit-', '-moz-', '-ms-', '-o-'],
            'transition': ['-webkit-', '-moz-', '-o-'],
            'animation': ['-webkit-', '-moz-', '-o-'],
            'box-shadow': ['-webkit-', '-moz-'],
            'border-radius': ['-webkit-', '-moz-'],
            'background-size': ['-webkit-', '-moz-', '-o-'],
            'user-select': ['-webkit-', '-moz-', '-ms-'],
            'appearance': ['-webkit-', '-moz-']
        }
    
    def check_property_support(
        self,
        property_name: str,
        value: Optional[str] = None
    ) -> Dict[str, BrowserSupport]:
        """
        Check browser support for a property.
        
        Args:
            property_name: CSS property name
            value: Optional property value
            
        Returns:
            Dictionary of browser support levels
        """
        support = {}
        
        # Check for custom properties
        if property_name.startswith('--'):
            compat_key = '--*'
        # Check for specific value combinations
        elif value and f"{property_name}: {value}" in self.compatibility_data:
            compat_key = f"{property_name}: {value}"
        # Check property alone
        elif property_name in self.compatibility_data:
            compat_key = property_name
        else:
            # Unknown property, assume full support
            for browser in self.target_browsers:
                support[browser] = BrowserSupport.UNKNOWN
            return support
        
        compat_info = self.compatibility_data.get(compat_key, {})
        
        for browser in self.target_browsers:
            if browser in compat_info:
                version, level = compat_info[browser]
                support[browser] = level
            else:
                support[browser] = BrowserSupport.UNKNOWN
        
        return support
    
    def needs_prefix(self, property_name: str) -> List[str]:
        """
        Check if property needs vendor prefixes.
        
        Args:
            property_name: CSS property name
            
        Returns:
            List of vendor prefixes needed
        """
        return self.prefixed_properties.get(property_name, [])
    
    def add_vendor_prefixes(
        self,
        properties: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Add vendor prefixes to properties that need them.
        
        Args:
            properties: CSS properties dictionary
            
        Returns:
            Properties with vendor prefixes added
        """
        result = {}
        
        for prop_name, prop_value in properties.items():
            # Add the original property
            result[prop_name] = prop_value
            
            # Check if needs prefixes
            prefixes = self.needs_prefix(prop_name)
            for prefix in prefixes:
                prefixed_name = f"{prefix}{prop_name}"
                if prefixed_name not in result:
                    result[prefixed_name] = prop_value
        
        return result
    
    def check_properties_compatibility(
        self,
        properties: Dict[str, str]
    ) -> Tuple[Dict[str, Dict[str, BrowserSupport]], List[str]]:
        """
        Check browser compatibility for multiple properties.
        
        Args:
            properties: CSS properties dictionary
            
        Returns:
            Tuple of (compatibility_map, warnings)
        """
        compatibility = {}
        warnings = []
        
        for prop_name, prop_value in properties.items():
            support = self.check_property_support(prop_name, prop_value)
            compatibility[prop_name] = support
            
            # Generate warnings for poor support
            for browser, level in support.items():
                if level == BrowserSupport.NONE:
                    warnings.append(f"'{prop_name}' is not supported in {browser}")
                elif level == BrowserSupport.PARTIAL:
                    warnings.append(f"'{prop_name}' has partial support in {browser}")
                elif level == BrowserSupport.PREFIXED:
                    warnings.append(f"'{prop_name}' needs vendor prefix for {browser}")
        
        return compatibility, warnings
    
    def get_fallback_properties(
        self,
        property_name: str,
        value: str
    ) -> List[Tuple[str, str]]:
        """
        Get fallback properties for better compatibility.
        
        Args:
            property_name: CSS property name
            value: Property value
            
        Returns:
            List of (property, value) tuples for fallbacks
        """
        fallbacks = []
        
        # Flexbox fallbacks
        if property_name == 'display' and value == 'flex':
            fallbacks.append(('display', '-webkit-box'))
            fallbacks.append(('display', '-moz-box'))
            fallbacks.append(('display', '-ms-flexbox'))
            fallbacks.append(('display', '-webkit-flex'))
        
        # Grid fallbacks
        elif property_name == 'display' and value == 'grid':
            fallbacks.append(('display', '-ms-grid'))
        
        # Gap fallbacks (for flexbox)
        elif property_name == 'gap':
            # No direct fallback, but could use margins
            pass
        
        # Sticky positioning fallback
        elif property_name == 'position' and value == 'sticky':
            fallbacks.append(('position', '-webkit-sticky'))
        
        # Add the original property last
        fallbacks.append((property_name, value))
        
        return fallbacks
    
    def generate_compatible_css(
        self,
        properties: Dict[str, str],
        add_prefixes: bool = True,
        add_fallbacks: bool = True
    ) -> Dict[str, str]:
        """
        Generate CSS with maximum browser compatibility.
        
        Args:
            properties: CSS properties dictionary
            add_prefixes: Whether to add vendor prefixes
            add_fallbacks: Whether to add fallback properties
            
        Returns:
            Compatible CSS properties (with fallbacks as list for duplicate keys)
        """
        result = {}
        
        for prop_name, prop_value in properties.items():
            # Add fallbacks first (they should come before the standard property)
            if add_fallbacks:
                fallbacks = self.get_fallback_properties(prop_name, prop_value)
                # Handle multiple values for same property (like display)
                for fallback_prop, fallback_value in fallbacks:
                    if fallback_prop in result:
                        # If property exists, keep as a list for multiple fallbacks
                        if not isinstance(result[fallback_prop], list):
                            result[fallback_prop] = [result[fallback_prop]]
                        result[fallback_prop].append(fallback_value)
                    else:
                        result[fallback_prop] = fallback_value
            else:
                # Add the property itself
                result[prop_name] = prop_value
            
            # Add prefixed versions
            if add_prefixes:
                prefixes = self.needs_prefix(prop_name)
                for prefix in prefixes:
                    prefixed_name = f"{prefix}{prop_name}"
                    if prefixed_name not in result:
                        result[prefixed_name] = prop_value
        
        return result
    
    def get_minimum_browser_versions(
        self,
        properties: Dict[str, str]
    ) -> Dict[str, Optional[float]]:
        """
        Get minimum browser versions needed for properties.
        
        Args:
            properties: CSS properties dictionary
            
        Returns:
            Dictionary of minimum browser versions
        """
        min_versions = {}
        
        for browser in self.target_browsers:
            min_version = None
            
            for prop_name in properties:
                # Get compatibility data
                if prop_name.startswith('--'):
                    compat_key = '--*'
                else:
                    compat_key = prop_name
                
                if compat_key in self.compatibility_data:
                    browser_data = self.compatibility_data[compat_key].get(browser)
                    if browser_data:
                        version, support = browser_data
                        if version and support != BrowserSupport.NONE:
                            if min_version is None or (version and version > min_version):
                                min_version = version
            
            min_versions[browser] = min_version
        
        return min_versions