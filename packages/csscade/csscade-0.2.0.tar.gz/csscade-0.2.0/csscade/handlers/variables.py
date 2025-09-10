"""CSS variables (custom properties) handler."""

import re
from typing import Dict, List, Optional, Tuple, Any


class VariablesHandler:
    """Handle CSS variables (custom properties)."""
    
    def __init__(self):
        """Initialize the variables handler."""
        self.var_pattern = re.compile(r'var\((--[\w-]+)(?:,\s*([^)]+))?\)')
        self.custom_prop_pattern = re.compile(r'^--[\w-]+$')
        self.root_variables: Dict[str, str] = {}
        self.scope_variables: Dict[str, Dict[str, str]] = {}
    
    def is_variable(self, value: str) -> bool:
        """
        Check if a value contains CSS variables.
        
        Args:
            value: CSS value to check
            
        Returns:
            True if value contains var() function
        """
        return 'var(' in value
    
    def is_custom_property(self, property_name: str) -> bool:
        """
        Check if a property is a custom property (CSS variable).
        
        Args:
            property_name: Property name to check
            
        Returns:
            True if property is a custom property
        """
        return bool(self.custom_prop_pattern.match(property_name))
    
    def extract_variables(self, value: str) -> List[Tuple[str, Optional[str]]]:
        """
        Extract variable references from a value.
        
        Args:
            value: CSS value containing var() functions
            
        Returns:
            List of (variable_name, fallback_value) tuples
        """
        variables = []
        
        # Find all var() expressions, handling nested parentheses
        i = 0
        while i < len(value):
            if value[i:i+4] == 'var(':
                # Found a var() expression
                start = i + 4
                paren_depth = 1
                end = start
                
                # Find the matching closing parenthesis
                while end < len(value) and paren_depth > 0:
                    if value[end] == '(':
                        paren_depth += 1
                    elif value[end] == ')':
                        paren_depth -= 1
                    end += 1
                
                # Extract the content inside var()
                content = value[start:end-1]
                
                # Split on comma, but only at the top level
                comma_pos = -1
                paren_depth = 0
                for j, char in enumerate(content):
                    if char == '(':
                        paren_depth += 1
                    elif char == ')':
                        paren_depth -= 1
                    elif char == ',' and paren_depth == 0:
                        comma_pos = j
                        break
                
                if comma_pos != -1:
                    var_name = content[:comma_pos].strip()
                    fallback = content[comma_pos+1:].strip()
                else:
                    var_name = content.strip()
                    fallback = None
                
                variables.append((var_name, fallback))
                i = end
            else:
                i += 1
        
        return variables
    
    def register_variable(self, var_name: str, value: str, scope: str = ':root') -> None:
        """
        Register a CSS variable definition.
        
        Args:
            var_name: Variable name (e.g., '--primary-color')
            value: Variable value
            scope: Scope selector (default ':root')
        """
        if scope == ':root':
            self.root_variables[var_name] = value
        else:
            if scope not in self.scope_variables:
                self.scope_variables[scope] = {}
            self.scope_variables[scope][var_name] = value
    
    def resolve_variable(
        self,
        var_name: str,
        scope: Optional[str] = None,
        fallback: Optional[str] = None
    ) -> Optional[str]:
        """
        Resolve a CSS variable to its value.
        
        Args:
            var_name: Variable name to resolve
            scope: Current scope for resolution
            fallback: Fallback value if variable not found
            
        Returns:
            Resolved value or fallback
        """
        # Check scope-specific variables first
        if scope and scope in self.scope_variables:
            if var_name in self.scope_variables[scope]:
                return self.scope_variables[scope][var_name]
        
        # Check root variables
        if var_name in self.root_variables:
            return self.root_variables[var_name]
        
        # Return fallback
        return fallback
    
    def expand_variables(
        self,
        value: str,
        scope: Optional[str] = None,
        max_depth: int = 10
    ) -> str:
        """
        Expand all variables in a value.
        
        Args:
            value: CSS value containing var() functions
            scope: Current scope for resolution
            max_depth: Maximum recursion depth for nested variables
            
        Returns:
            Value with variables expanded
        """
        if max_depth <= 0:
            # Prevent infinite recursion
            return value
        
        if not self.is_variable(value):
            return value
        
        result = value
        variables = self.extract_variables(value)
        
        for var_name, fallback in variables:
            resolved = self.resolve_variable(var_name, scope, fallback)
            
            if resolved:
                # Recursively expand nested variables
                resolved = self.expand_variables(resolved, scope, max_depth - 1)
                
                # Replace the var() expression
                var_expr = f'var({var_name}'
                if fallback:
                    var_expr += f', {fallback}'
                var_expr += ')'
                
                result = result.replace(var_expr, resolved)
        
        return result
    
    def handle_variable_override(
        self,
        property_name: str,
        value: str,
        strategy: str = 'expand'
    ) -> Tuple[str, str]:
        """
        Handle override of a property containing variables.
        
        Args:
            property_name: Property name
            value: Property value potentially containing variables
            strategy: 'expand', 'preserve', or 'inline'
            
        Returns:
            Tuple of (property_name, processed_value)
        """
        if strategy == 'expand':
            # Try to expand variables
            expanded = self.expand_variables(value)
            return (property_name, expanded)
        elif strategy == 'preserve':
            # Keep variables as-is
            return (property_name, value)
        else:  # inline
            # For inline styles, we might want to expand
            expanded = self.expand_variables(value)
            if expanded != value:
                # Variables were expanded
                return (property_name, expanded)
            else:
                # No expansion possible, keep as-is with warning
                return (property_name, value)
    
    def extract_root_variables(self, css_text: str) -> Dict[str, str]:
        """
        Extract :root variables from CSS text.
        
        Args:
            css_text: CSS text to parse
            
        Returns:
            Dictionary of variable names to values
        """
        variables = {}
        
        # Find :root block
        root_pattern = re.compile(r':root\s*{([^}]+)}', re.MULTILINE | re.DOTALL)
        root_match = root_pattern.search(css_text)
        
        if root_match:
            content = root_match.group(1)
            
            # Extract custom properties
            prop_pattern = re.compile(r'(--[\w-]+)\s*:\s*([^;]+);?')
            for match in prop_pattern.finditer(content):
                var_name = match.group(1)
                var_value = match.group(2).strip()
                variables[var_name] = var_value
                self.register_variable(var_name, var_value)
        
        return variables
    
    def merge_variables(
        self,
        base_vars: Dict[str, str],
        override_vars: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Merge two sets of CSS variables.
        
        Args:
            base_vars: Base variables
            override_vars: Override variables
            
        Returns:
            Merged variables dictionary
        """
        return {**base_vars, **override_vars}
    
    def generate_root_block(self, variables: Dict[str, str]) -> str:
        """
        Generate a :root CSS block from variables.
        
        Args:
            variables: Dictionary of CSS variables
            
        Returns:
            CSS :root block string
        """
        if not variables:
            return ""
        
        lines = [":root {"]
        for var_name, var_value in sorted(variables.items()):
            lines.append(f"  {var_name}: {var_value};")
        lines.append("}")
        
        return "\n".join(lines)
    
    def get_fallback_chain(self, value: str) -> List[str]:
        """
        Get the fallback chain from a var() expression.
        
        Args:
            value: CSS value with var()
            
        Returns:
            List of values in fallback order
        """
        chain = []
        variables = self.extract_variables(value)
        
        for var_name, fallback in variables:
            resolved = self.resolve_variable(var_name)
            if resolved:
                # Resolved value might contain more variables
                if self.is_variable(resolved):
                    chain.extend(self.get_fallback_chain(resolved))
                else:
                    chain.append(resolved)
            if fallback:
                # Fallback might contain more variables
                if self.is_variable(fallback):
                    chain.extend(self.get_fallback_chain(fallback))
                else:
                    chain.append(fallback)
        
        return chain
    
    def validate_variable_name(self, name: str) -> bool:
        """
        Validate a CSS variable name.
        
        Args:
            name: Variable name to validate
            
        Returns:
            True if valid CSS variable name
        """
        return bool(self.custom_prop_pattern.match(name))
    
    def clear_variables(self) -> None:
        """Clear all registered variables."""
        self.root_variables.clear()
        self.scope_variables.clear()