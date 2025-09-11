"""Integration helpers for CSSCade."""

import json
import pickle
import time
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path


class StateManager:
    """Manage CSSCade state for serialization and restoration."""
    
    def __init__(self):
        """Initialize state manager."""
        self.version = "1.0.0"
        self.state: Dict[str, Any] = {}
    
    def capture_state(self, merger: Any) -> Dict[str, Any]:
        """
        Capture current state of a merger.
        
        Args:
            merger: CSSMerger instance
            
        Returns:
            State dictionary
        """
        state = {
            'version': self.version,
            'config': merger.config.to_dict() if hasattr(merger, 'config') else {},
            'mode': merger.mode,
            'cache': self._capture_cache_state(merger),
            'stats': self._capture_stats(merger),
            'timestamp': time.time()
        }
        
        return state
    
    def restore_state(self, merger: Any, state: Dict[str, Any]) -> None:
        """
        Restore merger state from dictionary.
        
        Args:
            merger: CSSMerger instance
            state: State dictionary
        """
        # Check version compatibility
        if state.get('version') != self.version:
            print(f"Warning: State version mismatch ({state.get('version')} vs {self.version})")
        
        # Restore configuration
        if 'config' in state and hasattr(merger, 'config'):
            merger.config.update(state['config'])
        
        # Restore mode
        if 'mode' in state:
            merger.mode = state['mode']
        
        # Restore cache if possible
        if 'cache' in state:
            self._restore_cache_state(merger, state['cache'])
    
    def _capture_cache_state(self, merger: Any) -> Dict[str, Any]:
        """Capture cache state."""
        cache_state = {}
        
        if hasattr(merger, '_cache'):
            # Capture cache statistics
            cache_state['stats'] = merger._cache.stats() if hasattr(merger._cache, 'stats') else {}
        
        return cache_state
    
    def _restore_cache_state(self, merger: Any, cache_state: Dict[str, Any]) -> None:
        """Restore cache state."""
        # Cache content is not restored for security/freshness
        # Only statistics are preserved for reference
        pass
    
    def _capture_stats(self, merger: Any) -> Dict[str, Any]:
        """Capture merger statistics."""
        stats = {}
        
        if hasattr(merger, '_performance'):
            stats['performance'] = merger._performance.get_summary() if hasattr(merger._performance, 'get_summary') else {}
        
        if hasattr(merger, '_debugger'):
            stats['debug'] = len(merger._debugger.info.operations) if merger._debugger else 0
        
        return stats
    
    def save_state(self, state: Dict[str, Any], path: Union[str, Path]) -> None:
        """
        Save state to file.
        
        Args:
            state: State dictionary
            path: File path
        """
        path = Path(path)
        
        if path.suffix == '.json':
            with open(path, 'w') as f:
                json.dump(state, f, indent=2, default=str)
        else:
            with open(path, 'wb') as f:
                pickle.dump(state, f)
    
    def load_state(self, path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load state from file.
        
        Args:
            path: File path
            
        Returns:
            State dictionary
        """
        path = Path(path)
        
        if path.suffix == '.json':
            with open(path, 'r') as f:
                return json.load(f)
        else:
            with open(path, 'rb') as f:
                return pickle.load(f)


class FrameworkAdapter:
    """Adapters for popular web frameworks."""
    
    @staticmethod
    def django_middleware(merger: Any):
        """
        Create Django middleware for CSS merging.
        
        Args:
            merger: CSSMerger instance
            
        Returns:
            Django middleware class
        """
        class CSSMergeMiddleware:
            def __init__(self, get_response):
                self.get_response = get_response
                self.merger = merger
            
            def __call__(self, request):
                response = self.get_response(request)
                
                # Process CSS in response if needed
                if response.get('Content-Type', '').startswith('text/css'):
                    # Extract and merge CSS
                    pass
                
                return response
        
        return CSSMergeMiddleware
    
    @staticmethod
    def flask_extension(merger: Any):
        """
        Create Flask extension for CSS merging.
        
        Args:
            merger: CSSMerger instance
            
        Returns:
            Flask extension
        """
        class CSSMergeExtension:
            def __init__(self, app=None):
                self.merger = merger
                if app:
                    self.init_app(app)
            
            def init_app(self, app):
                app.config.setdefault('CSSCADE_MODE', 'component')
                app.config.setdefault('CSSCADE_CACHE', True)
                
                # Add template functions
                app.jinja_env.globals['merge_css'] = self.merge_css
            
            def merge_css(self, source, override):
                return self.merger.merge(source, override)
        
        return CSSMergeExtension
    
    @staticmethod
    def webpack_plugin(merger: Any) -> str:
        """
        Generate webpack plugin configuration.
        
        Args:
            merger: CSSMerger instance
            
        Returns:
            Webpack plugin configuration as string
        """
        config = """
class CSSCadePlugin {
    constructor(options = {}) {
        this.options = options;
    }
    
    apply(compiler) {
        compiler.hooks.emit.tapAsync('CSSCadePlugin', (compilation, callback) => {
            // Process CSS assets
            Object.keys(compilation.assets).forEach(filename => {
                if (filename.endsWith('.css')) {
                    // Apply CSS merging
                    const source = compilation.assets[filename].source();
                    // Process with CSSCade
                }
            });
            callback();
        });
    }
}

module.exports = CSSCadePlugin;
"""
        return config


class APIWrapper:
    """Simplified API wrapper for common use cases."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize API wrapper.
        
        Args:
            config: Configuration dictionary
        """
        from csscade import CSSMerger
        from csscade.config.config_manager import Config
        
        self.config = Config(config) if config else Config()
        self.merger = CSSMerger(
            mode=self.config.get('mode')
        )
        # Store config for later use
        self.merger.config = self.config
    
    def merge_files(
        self,
        source_path: Union[str, Path],
        override_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """
        Merge CSS files.
        
        Args:
            source_path: Source CSS file
            override_path: Override CSS file
            output_path: Optional output file path
            
        Returns:
            Merged CSS string
        """
        source_path = Path(source_path)
        override_path = Path(override_path)
        
        with open(source_path, 'r') as f:
            source_css = f.read()
        
        with open(override_path, 'r') as f:
            override_css = f.read()
        
        result = self.merger.merge(source_css, override_css)
        merged_css = result.get('css', '')
        
        if output_path:
            output_path = Path(output_path)
            with open(output_path, 'w') as f:
                f.write(merged_css)
        
        return merged_css
    
    def merge_inline(
        self,
        html: str,
        override_css: str,
        selector: str = 'style'
    ) -> str:
        """
        Merge CSS with inline styles in HTML.
        
        Args:
            html: HTML content
            override_css: Override CSS
            selector: Style tag selector
            
        Returns:
            Updated HTML
        """
        # Simple implementation - would use BeautifulSoup in production
        import re
        
        # Extract style tags
        style_pattern = f'<{selector}[^>]*>(.*?)</{selector}>'
        matches = re.findall(style_pattern, html, re.DOTALL)
        
        if matches:
            source_css = '\n'.join(matches)
            result = self.merger.merge(source_css, override_css)
            merged_css = result.get('css', '')
            
            # Replace first style tag and remove others
            html = re.sub(style_pattern, '', html, flags=re.DOTALL)
            html = html.replace('</head>', f'<style>{merged_css}</style></head>')
        
        return html
    
    def batch_merge(
        self,
        operations: List[Tuple[str, str]],
        parallel: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Perform batch merge operations.
        
        Args:
            operations: List of (source, override) tuples
            parallel: Whether to process in parallel
            
        Returns:
            List of merge results
        """
        batch = self.merger.batch()
        
        for source, override in operations:
            batch.add(source, override)
        
        return batch.execute()
    
    def validate_css(self, css: Union[str, Dict[str, str]]) -> Tuple[bool, List[str]]:
        """
        Validate CSS content.
        
        Args:
            css: CSS string or properties dictionary
            
        Returns:
            Tuple of (is_valid, issues)
        """
        from csscade.validation import CSSValidator
        
        validator = CSSValidator(strict=False)
        
        if isinstance(css, str):
            # Parse CSS string to properties
            from csscade.parser import CSSParser
            parser = CSSParser()
            try:
                parsed = parser.parse(css)
                if isinstance(parsed, dict):
                    properties = parsed
                else:
                    return False, ["Could not parse CSS"]
            except Exception as e:
                return False, [str(e)]
        else:
            properties = css
        
        return validator.validate_properties(properties)
    
    def check_security(self, css: Union[str, Dict[str, str]]) -> Tuple[bool, List[str]]:
        """
        Check CSS for security issues.
        
        Args:
            css: CSS string or properties dictionary
            
        Returns:
            Tuple of (is_safe, issues)
        """
        from csscade.validation import SecurityChecker
        
        checker = SecurityChecker(
            allow_external_urls=self.config.get('security.allow_external_urls', False)
        )
        
        if isinstance(css, str):
            # Parse CSS string to properties
            from csscade.parser import CSSParser
            parser = CSSParser()
            try:
                parsed = parser.parse(css)
                if isinstance(parsed, dict):
                    properties = parsed
                else:
                    return False, ["Could not parse CSS"]
            except Exception as e:
                return False, [str(e)]
        else:
            properties = css
        
        return checker.check_properties(properties)


# Convenience functions
def quick_merge(source: str, override: str, mode: str = 'component') -> str:
    """
    Quick CSS merge without configuration.
    
    Args:
        source: Source CSS
        override: Override CSS
        mode: Merge mode
        
    Returns:
        Merged CSS string
    """
    from csscade import CSSMerger
    
    merger = CSSMerger(mode=mode)
    result = merger.merge(source, override)
    return result.get('css', '')


def merge_files(source_path: str, override_path: str, output_path: str) -> None:
    """
    Merge CSS files and save result.
    
    Args:
        source_path: Source CSS file
        override_path: Override CSS file
        output_path: Output CSS file
    """
    wrapper = APIWrapper()
    wrapper.merge_files(source_path, override_path, output_path)