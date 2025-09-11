"""Configuration management for CSSCade."""

import json
from typing import Any, Dict, Optional, Union
from pathlib import Path
from copy import deepcopy


class ConfigError(Exception):
    """Configuration error."""
    pass


class Config:
    """Configuration container for CSSCade."""
    
    # Default configuration
    DEFAULTS = {
        'mode': 'component',
        'debug': False,
        'cache': {
            'enabled': True,
            'max_size': 128,
            'ttl': None  # Time to live in seconds, None = forever
        },
        'validation': {
            'enabled': True,
            'strict': False,
            'check_property_names': True,
            'check_property_values': True,
            'suggest_corrections': True
        },
        'security': {
            'enabled': True,
            'allow_external_urls': False,
            'sanitize_dangerous_content': True,
            'check_injections': True
        },
        'browser_compat': {
            'enabled': False,
            'target_browsers': ['chrome', 'firefox', 'safari', 'edge'],
            'add_vendor_prefixes': True,
            'add_fallbacks': True,
            'min_browser_versions': None
        },
        'optimization': {
            'deduplicate_styles': True,
            'combine_shorthands': True,
            'remove_defaults': False,
            'minify': False
        },
        'output': {
            'format': 'expanded',  # 'expanded', 'compact', 'minified'
            'indent': '  ',
            'newline': '\n',
            'include_source_map': False
        },
        'safe_mode': {
            'enabled': False,
            'dry_run': False,
            'verbose': False,
            'log_operations': True
        }
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration.
        
        Args:
            config: Configuration dictionary
        """
        self._config = deepcopy(self.DEFAULTS)
        if config:
            self.update(config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Configuration value
        """
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def update(self, config: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            config: Configuration dictionary to merge
        """
        self._merge_dict(self._config, config)
    
    def _merge_dict(self, base: Dict, update: Dict) -> None:
        """
        Recursively merge dictionaries.
        
        Args:
            base: Base dictionary to update
            update: Dictionary with new values
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dict(base[key], value)
            else:
                base[key] = value
    
    def validate(self) -> None:
        """
        Validate configuration.
        
        Raises:
            ConfigError: If configuration is invalid
        """
        # Validate mode
        valid_modes = ['permanent', 'component', 'replace']
        if self._config['mode'] not in valid_modes:
            raise ConfigError(f"Invalid mode: {self._config['mode']}. Must be one of {valid_modes}")
        
        # Validate cache settings
        if self._config['cache']['max_size'] < 0:
            raise ConfigError("Cache max_size must be non-negative")
        
        # Validate output format
        valid_formats = ['expanded', 'compact', 'minified']
        if self._config['output']['format'] not in valid_formats:
            raise ConfigError(f"Invalid output format: {self._config['output']['format']}")
        
        # Validate browser targets
        valid_browsers = ['chrome', 'firefox', 'safari', 'edge', 'ie']
        for browser in self._config['browser_compat']['target_browsers']:
            if browser not in valid_browsers:
                raise ConfigError(f"Invalid target browser: {browser}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return deepcopy(self._config)
    
    def to_json(self, indent: Optional[int] = 2) -> str:
        """
        Convert configuration to JSON string.
        
        Args:
            indent: JSON indentation
            
        Returns:
            JSON string
        """
        return json.dumps(self._config, indent=indent)
    
    def from_json(self, json_str: str) -> None:
        """
        Load configuration from JSON string.
        
        Args:
            json_str: JSON configuration string
        """
        config = json.loads(json_str)
        self.update(config)
        self.validate()
    
    def save(self, path: Union[str, Path]) -> None:
        """
        Save configuration to file.
        
        Args:
            path: File path
        """
        path = Path(path)
        with open(path, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def load(self, path: Union[str, Path]) -> None:
        """
        Load configuration from file.
        
        Args:
            path: File path
        """
        path = Path(path)
        with open(path, 'r') as f:
            config = json.load(f)
        self.update(config)
        self.validate()
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = deepcopy(self.DEFAULTS)
    
    def __getitem__(self, key: str) -> Any:
        """Get configuration value using bracket notation."""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set configuration value using bracket notation."""
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """Check if configuration key exists."""
        return self.get(key) is not None


class ConfigBuilder:
    """Builder for creating configurations."""
    
    def __init__(self):
        """Initialize config builder."""
        self._config = {}
    
    def mode(self, mode: str) -> 'ConfigBuilder':
        """Set merge mode."""
        self._config['mode'] = mode
        return self
    
    def debug(self, enabled: bool = True) -> 'ConfigBuilder':
        """Enable debug mode."""
        self._config['debug'] = enabled
        return self
    
    def cache(self, enabled: bool = True, max_size: int = 128) -> 'ConfigBuilder':
        """Configure caching."""
        self._config['cache'] = {
            'enabled': enabled,
            'max_size': max_size
        }
        return self
    
    def validation(self, enabled: bool = True, strict: bool = False) -> 'ConfigBuilder':
        """Configure validation."""
        self._config['validation'] = {
            'enabled': enabled,
            'strict': strict
        }
        return self
    
    def security(self, enabled: bool = True, allow_external: bool = False) -> 'ConfigBuilder':
        """Configure security."""
        self._config['security'] = {
            'enabled': enabled,
            'allow_external_urls': allow_external
        }
        return self
    
    def browser_compat(
        self,
        enabled: bool = True,
        browsers: Optional[list] = None
    ) -> 'ConfigBuilder':
        """Configure browser compatibility."""
        self._config['browser_compat'] = {
            'enabled': enabled,
            'target_browsers': browsers or ['chrome', 'firefox', 'safari', 'edge']
        }
        return self
    
    def optimization(
        self,
        deduplicate: bool = True,
        minify: bool = False
    ) -> 'ConfigBuilder':
        """Configure optimization."""
        self._config['optimization'] = {
            'deduplicate_styles': deduplicate,
            'minify': minify
        }
        return self
    
    def output(self, format: str = 'expanded', minify: bool = False) -> 'ConfigBuilder':
        """Configure output format."""
        self._config['output'] = {
            'format': 'minified' if minify else format
        }
        return self
    
    def safe_mode(self, dry_run: bool = False, verbose: bool = False) -> 'ConfigBuilder':
        """Configure safe mode."""
        self._config['safe_mode'] = {
            'enabled': True,
            'dry_run': dry_run,
            'verbose': verbose
        }
        return self
    
    def build(self) -> Config:
        """Build configuration."""
        return Config(self._config)


def load_config(path: Optional[Union[str, Path]] = None) -> Config:
    """
    Load configuration from file or use defaults.
    
    Args:
        path: Optional configuration file path
        
    Returns:
        Configuration object
    """
    config = Config()
    
    if path:
        config.load(path)
    else:
        # Check for default config files
        default_paths = [
            Path('csscade.config.json'),
            Path('.csscade.json'),
            Path.home() / '.csscade' / 'config.json'
        ]
        
        for default_path in default_paths:
            if default_path.exists():
                config.load(default_path)
                break
    
    return config