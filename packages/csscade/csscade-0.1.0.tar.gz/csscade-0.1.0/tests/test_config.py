"""Tests for configuration management."""

import pytest
import json
import tempfile
from pathlib import Path
from csscade.config import Config, ConfigBuilder, ConfigError, load_config


class TestConfig:
    """Test cases for Config class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.get('mode') == 'component'
        assert config.get('debug') is False
        assert config.get('cache.enabled') is True
        assert config.get('cache.max_size') == 128
    
    def test_get_with_dot_notation(self):
        """Test getting values with dot notation."""
        config = Config()
        
        assert config.get('cache.enabled') is True
        assert config.get('validation.strict') is False
        assert config.get('nonexistent.key') is None
        assert config.get('nonexistent.key', 'default') == 'default'
    
    def test_set_with_dot_notation(self):
        """Test setting values with dot notation."""
        config = Config()
        
        config.set('cache.enabled', False)
        assert config.get('cache.enabled') is False
        
        config.set('new.nested.value', 'test')
        assert config.get('new.nested.value') == 'test'
    
    def test_update_config(self):
        """Test updating configuration."""
        config = Config()
        
        updates = {
            'mode': 'permanent',
            'cache': {
                'enabled': False,
                'max_size': 256
            }
        }
        
        config.update(updates)
        
        assert config.get('mode') == 'permanent'
        assert config.get('cache.enabled') is False
        assert config.get('cache.max_size') == 256
        # Other cache settings should remain
        assert config.get('cache.ttl') is None
    
    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        config = Config({'mode': 'component'})
        
        # Should not raise
        config.validate()
    
    def test_validate_invalid_mode(self):
        """Test validation with invalid mode."""
        config = Config({'mode': 'invalid'})
        
        with pytest.raises(ConfigError) as exc:
            config.validate()
        
        assert 'Invalid mode' in str(exc.value)
    
    def test_validate_invalid_cache_size(self):
        """Test validation with invalid cache size."""
        config = Config({'cache': {'max_size': -1}})
        
        with pytest.raises(ConfigError) as exc:
            config.validate()
        
        assert 'non-negative' in str(exc.value)
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config({'mode': 'replace'})
        
        result = config.to_dict()
        
        assert isinstance(result, dict)
        assert result['mode'] == 'replace'
        # Should be a copy
        result['mode'] = 'changed'
        assert config.get('mode') == 'replace'
    
    def test_to_json(self):
        """Test converting config to JSON."""
        config = Config({'mode': 'permanent'})
        
        json_str = config.to_json()
        
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed['mode'] == 'permanent'
    
    def test_from_json(self):
        """Test loading config from JSON."""
        config = Config()
        
        json_str = '{"mode": "replace", "debug": true}'
        config.from_json(json_str)
        
        assert config.get('mode') == 'replace'
        assert config.get('debug') is True
    
    def test_save_and_load_file(self):
        """Test saving and loading config from file."""
        config = Config({'mode': 'permanent', 'debug': True})
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            config.save(f.name)
            
            # Load into new config
            new_config = Config()
            new_config.load(f.name)
            
            assert new_config.get('mode') == 'permanent'
            assert new_config.get('debug') is True
        
        # Clean up
        Path(f.name).unlink()
    
    def test_reset_config(self):
        """Test resetting config to defaults."""
        config = Config({'mode': 'permanent'})
        
        assert config.get('mode') == 'permanent'
        
        config.reset()
        
        assert config.get('mode') == 'component'  # Back to default
    
    def test_bracket_notation(self):
        """Test bracket notation access."""
        config = Config()
        
        # Get
        assert config['mode'] == 'component'
        
        # Set
        config['mode'] = 'replace'
        assert config['mode'] == 'replace'
        
        # Contains
        assert 'mode' in config
        assert 'nonexistent' not in config


class TestConfigBuilder:
    """Test cases for ConfigBuilder."""
    
    def test_build_basic_config(self):
        """Test building basic configuration."""
        builder = ConfigBuilder()
        
        config = (builder
                 .mode('permanent')
                 .debug(True)
                 .build())
        
        assert config.get('mode') == 'permanent'
        assert config.get('debug') is True
    
    def test_build_cache_config(self):
        """Test building cache configuration."""
        builder = ConfigBuilder()
        
        config = (builder
                 .cache(enabled=True, max_size=256)
                 .build())
        
        assert config.get('cache.enabled') is True
        assert config.get('cache.max_size') == 256
    
    def test_build_validation_config(self):
        """Test building validation configuration."""
        builder = ConfigBuilder()
        
        config = (builder
                 .validation(enabled=True, strict=True)
                 .build())
        
        assert config.get('validation.enabled') is True
        assert config.get('validation.strict') is True
    
    def test_build_security_config(self):
        """Test building security configuration."""
        builder = ConfigBuilder()
        
        config = (builder
                 .security(enabled=True, allow_external=True)
                 .build())
        
        assert config.get('security.enabled') is True
        assert config.get('security.allow_external_urls') is True
    
    def test_build_browser_compat_config(self):
        """Test building browser compatibility configuration."""
        builder = ConfigBuilder()
        
        config = (builder
                 .browser_compat(enabled=True, browsers=['chrome', 'firefox'])
                 .build())
        
        assert config.get('browser_compat.enabled') is True
        assert config.get('browser_compat.target_browsers') == ['chrome', 'firefox']
    
    def test_build_optimization_config(self):
        """Test building optimization configuration."""
        builder = ConfigBuilder()
        
        config = (builder
                 .optimization(deduplicate=True, minify=True)
                 .build())
        
        assert config.get('optimization.deduplicate_styles') is True
        assert config.get('optimization.minify') is True
    
    def test_build_output_config(self):
        """Test building output configuration."""
        builder = ConfigBuilder()
        
        config = (builder
                 .output(format='compact', minify=False)
                 .build())
        
        assert config.get('output.format') == 'compact'
        
        # Test minify override
        config = (builder
                 .output(format='compact', minify=True)
                 .build())
        
        assert config.get('output.format') == 'minified'
    
    def test_build_safe_mode_config(self):
        """Test building safe mode configuration."""
        builder = ConfigBuilder()
        
        config = (builder
                 .safe_mode(dry_run=True, verbose=True)
                 .build())
        
        assert config.get('safe_mode.enabled') is True
        assert config.get('safe_mode.dry_run') is True
        assert config.get('safe_mode.verbose') is True
    
    def test_chained_building(self):
        """Test chained configuration building."""
        builder = ConfigBuilder()
        
        config = (builder
                 .mode('permanent')
                 .debug(True)
                 .cache(enabled=False)
                 .validation(strict=True)
                 .security(enabled=True)
                 .output(format='minified')
                 .build())
        
        assert config.get('mode') == 'permanent'
        assert config.get('debug') is True
        assert config.get('cache.enabled') is False
        assert config.get('validation.strict') is True
        assert config.get('security.enabled') is True
        assert config.get('output.format') == 'minified'