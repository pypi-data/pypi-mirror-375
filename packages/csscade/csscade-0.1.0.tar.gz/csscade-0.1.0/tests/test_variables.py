"""Tests for CSS variables handler."""

import pytest
from csscade.handlers.variables import VariablesHandler


class TestVariablesHandler:
    """Test cases for VariablesHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = VariablesHandler()
    
    def test_is_variable(self):
        """Test detecting CSS variables."""
        assert self.handler.is_variable('var(--primary-color)') is True
        assert self.handler.is_variable('var(--spacing, 10px)') is True
        assert self.handler.is_variable('red') is False
        assert self.handler.is_variable('10px') is False
    
    def test_is_custom_property(self):
        """Test detecting custom properties."""
        assert self.handler.is_custom_property('--primary-color') is True
        assert self.handler.is_custom_property('--my-var') is True
        assert self.handler.is_custom_property('color') is False
        assert self.handler.is_custom_property('-webkit-transform') is False
    
    def test_extract_variables_simple(self):
        """Test extracting simple variables."""
        result = self.handler.extract_variables('var(--primary-color)')
        
        assert len(result) == 1
        assert result[0] == ('--primary-color', None)
    
    def test_extract_variables_with_fallback(self):
        """Test extracting variables with fallback."""
        result = self.handler.extract_variables('var(--primary-color, red)')
        
        assert len(result) == 1
        assert result[0] == ('--primary-color', 'red')
    
    def test_extract_variables_multiple(self):
        """Test extracting multiple variables."""
        result = self.handler.extract_variables('var(--color-1) var(--color-2, blue)')
        
        assert len(result) == 2
        assert result[0] == ('--color-1', None)
        assert result[1] == ('--color-2', 'blue')
    
    def test_register_variable_root(self):
        """Test registering root variables."""
        self.handler.register_variable('--primary-color', '#007bff')
        
        assert '--primary-color' in self.handler.root_variables
        assert self.handler.root_variables['--primary-color'] == '#007bff'
    
    def test_register_variable_scoped(self):
        """Test registering scoped variables."""
        self.handler.register_variable('--text-color', 'white', '.dark-theme')
        
        assert '.dark-theme' in self.handler.scope_variables
        assert '--text-color' in self.handler.scope_variables['.dark-theme']
        assert self.handler.scope_variables['.dark-theme']['--text-color'] == 'white'
    
    def test_resolve_variable_from_root(self):
        """Test resolving variable from root."""
        self.handler.register_variable('--primary-color', '#007bff')
        
        result = self.handler.resolve_variable('--primary-color')
        assert result == '#007bff'
    
    def test_resolve_variable_from_scope(self):
        """Test resolving variable from scope."""
        self.handler.register_variable('--text-color', 'black')  # root
        self.handler.register_variable('--text-color', 'white', '.dark-theme')
        
        # Should get scoped value when scope provided
        result = self.handler.resolve_variable('--text-color', '.dark-theme')
        assert result == 'white'
        
        # Should get root value without scope
        result = self.handler.resolve_variable('--text-color')
        assert result == 'black'
    
    def test_resolve_variable_with_fallback(self):
        """Test resolving non-existent variable with fallback."""
        result = self.handler.resolve_variable('--unknown-var', None, 'red')
        assert result == 'red'
    
    def test_expand_variables_simple(self):
        """Test expanding simple variables."""
        self.handler.register_variable('--primary-color', '#007bff')
        
        result = self.handler.expand_variables('var(--primary-color)')
        assert result == '#007bff'
    
    def test_expand_variables_with_fallback(self):
        """Test expanding variables with fallback."""
        result = self.handler.expand_variables('var(--unknown-color, red)')
        assert result == 'red'
    
    def test_expand_variables_nested(self):
        """Test expanding nested variables."""
        self.handler.register_variable('--base-color', '#007bff')
        self.handler.register_variable('--primary-color', 'var(--base-color)')
        
        result = self.handler.expand_variables('var(--primary-color)')
        assert result == '#007bff'
    
    def test_expand_variables_max_depth(self):
        """Test max depth protection for recursive variables."""
        # Create circular reference
        self.handler.register_variable('--var-a', 'var(--var-b)')
        self.handler.register_variable('--var-b', 'var(--var-a)')
        
        # Should not infinite loop, returns original after max depth
        result = self.handler.expand_variables('var(--var-a)', max_depth=2)
        assert 'var(' in result  # Still contains var() due to depth limit
    
    def test_handle_variable_override_expand(self):
        """Test handling variable override with expand strategy."""
        self.handler.register_variable('--spacing', '10px')
        
        prop, value = self.handler.handle_variable_override(
            'margin', 'var(--spacing)', 'expand'
        )
        
        assert prop == 'margin'
        assert value == '10px'
    
    def test_handle_variable_override_preserve(self):
        """Test handling variable override with preserve strategy."""
        prop, value = self.handler.handle_variable_override(
            'margin', 'var(--spacing)', 'preserve'
        )
        
        assert prop == 'margin'
        assert value == 'var(--spacing)'
    
    def test_handle_variable_override_inline(self):
        """Test handling variable override with inline strategy."""
        self.handler.register_variable('--spacing', '10px')
        
        prop, value = self.handler.handle_variable_override(
            'margin', 'var(--spacing)', 'inline'
        )
        
        assert prop == 'margin'
        assert value == '10px'
    
    def test_extract_root_variables(self):
        """Test extracting root variables from CSS."""
        css_text = """
        :root {
            --primary-color: #007bff;
            --secondary-color: #6c757d;
            --spacing: 1rem;
        }
        """
        
        result = self.handler.extract_root_variables(css_text)
        
        assert len(result) == 3
        assert result['--primary-color'] == '#007bff'
        assert result['--secondary-color'] == '#6c757d'
        assert result['--spacing'] == '1rem'
        
        # Should also register them
        assert self.handler.root_variables['--primary-color'] == '#007bff'
    
    def test_extract_root_variables_multiline(self):
        """Test extracting root variables with multiline values."""
        css_text = """
        :root {
            --gradient: linear-gradient(
                45deg,
                red,
                blue
            );
        }
        """
        
        result = self.handler.extract_root_variables(css_text)
        assert '--gradient' in result
    
    def test_merge_variables(self):
        """Test merging variable sets."""
        base = {'--color': 'red', '--spacing': '10px'}
        override = {'--color': 'blue', '--margin': '20px'}
        
        result = self.handler.merge_variables(base, override)
        
        assert result['--color'] == 'blue'  # overridden
        assert result['--spacing'] == '10px'  # preserved
        assert result['--margin'] == '20px'  # added
    
    def test_generate_root_block(self):
        """Test generating :root CSS block."""
        variables = {
            '--primary-color': '#007bff',
            '--spacing': '1rem'
        }
        
        result = self.handler.generate_root_block(variables)
        
        assert ':root {' in result
        assert '--primary-color: #007bff;' in result
        assert '--spacing: 1rem;' in result
        assert '}' in result
    
    def test_generate_root_block_empty(self):
        """Test generating empty root block."""
        result = self.handler.generate_root_block({})
        assert result == ""
    
    def test_get_fallback_chain_simple(self):
        """Test getting fallback chain from var expression."""
        self.handler.register_variable('--color', 'blue')
        
        result = self.handler.get_fallback_chain('var(--color, red)')
        
        assert 'blue' in result  # resolved value
        assert 'red' in result   # fallback
    
    def test_get_fallback_chain_nested(self):
        """Test getting fallback chain with nested variables."""
        self.handler.register_variable('--base', 'green')
        
        result = self.handler.get_fallback_chain('var(--unknown, var(--base, red))')
        
        assert 'green' in result  # resolved nested var
        assert 'red' in result    # final fallback
    
    def test_validate_variable_name(self):
        """Test validating CSS variable names."""
        assert self.handler.validate_variable_name('--my-var') is True
        assert self.handler.validate_variable_name('--primary-color') is True
        assert self.handler.validate_variable_name('--123') is True
        assert self.handler.validate_variable_name('my-var') is False
        assert self.handler.validate_variable_name('--') is False
        assert self.handler.validate_variable_name('color') is False
    
    def test_clear_variables(self):
        """Test clearing all variables."""
        self.handler.register_variable('--color', 'red')
        self.handler.register_variable('--spacing', '10px', '.container')
        
        self.handler.clear_variables()
        
        assert len(self.handler.root_variables) == 0
        assert len(self.handler.scope_variables) == 0
    
    def test_complex_variable_expansion(self):
        """Test complex variable expansion scenarios."""
        # Register a chain of variables
        self.handler.register_variable('--base-size', '16px')
        self.handler.register_variable('--spacing-unit', 'calc(var(--base-size) * 1.5)')
        self.handler.register_variable('--margin', 'var(--spacing-unit)')
        
        # Expand through the chain
        result = self.handler.expand_variables('var(--margin)')
        assert 'calc(16px * 1.5)' in result
    
    def test_partial_variable_expansion(self):
        """Test partial expansion in compound values."""
        self.handler.register_variable('--spacing', '10px')
        
        result = self.handler.expand_variables('var(--spacing) var(--unknown, 20px) 30px')
        
        assert '10px' in result  # expanded known var
        assert '20px' in result  # used fallback for unknown
        assert '30px' in result  # preserved literal value