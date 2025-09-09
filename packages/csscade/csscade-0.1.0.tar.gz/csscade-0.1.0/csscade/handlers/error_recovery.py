"""Error recovery and graceful degradation for CSS processing."""

import traceback
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import contextmanager


class ErrorRecovery:
    """Handle errors and provide graceful degradation."""
    
    def __init__(self, strict: bool = False):
        """
        Initialize error recovery handler.
        
        Args:
            strict: If True, raise errors; if False, recover gracefully
        """
        self.strict = strict
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[str] = []
        self.recovered_count = 0
    
    def add_error(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ) -> None:
        """
        Add an error to the log.
        
        Args:
            error_type: Type of error
            message: Error message
            context: Additional context
            exception: Original exception if any
        """
        error_entry = {
            'type': error_type,
            'message': message,
            'context': context or {},
            'traceback': None
        }
        
        if exception:
            error_entry['exception'] = str(type(exception).__name__)
            error_entry['exception_message'] = str(exception)
            error_entry['traceback'] = traceback.format_exc()
        
        self.errors.append(error_entry)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    @contextmanager
    def recover(self, operation: str, default: Any = None):
        """
        Context manager for error recovery.
        
        Args:
            operation: Operation being performed
            default: Default value to return on error
            
        Yields:
            Result or default value
        """
        try:
            yield default
        except Exception as e:
            if self.strict:
                raise
            
            self.add_error(
                'operation_failed',
                f'Failed to {operation}',
                {'operation': operation},
                e
            )
            self.recovered_count += 1
    
    def parse_with_recovery(self, css_text: str) -> Tuple[Dict[str, Any], List[str]]:
        """
        Parse CSS with error recovery.
        
        Args:
            css_text: CSS text to parse
            
        Returns:
            Tuple of (parsed_content, errors)
        """
        parsed = {}
        errors = []
        
        # Try to parse as complete CSS first
        try:
            from csscade.parser import CSSParser
            parser = CSSParser()
            parsed = parser.parse(css_text)
            return parsed, errors
        except Exception as e:
            errors.append(f"Complete parse failed: {str(e)}")
        
        # Fall back to line-by-line parsing
        lines = css_text.split('\n')
        current_rule = []
        in_rule = False
        
        for i, line in enumerate(lines):
            try:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('//'):
                    continue
                
                # Handle comments
                if '/*' in line:
                    comment_start = line.index('/*')
                    comment_end = line.find('*/', comment_start)
                    if comment_end != -1:
                        line = line[:comment_start] + line[comment_end + 2:]
                    else:
                        # Multi-line comment
                        line = line[:comment_start]
                
                # Check for rule start
                if '{' in line and not in_rule:
                    in_rule = True
                    current_rule.append(line)
                elif in_rule:
                    current_rule.append(line)
                    if '}' in line:
                        # End of rule, try to parse it
                        rule_text = '\n'.join(current_rule)
                        try:
                            # Parse individual rule
                            self._parse_single_rule(rule_text, parsed)
                        except Exception as rule_error:
                            errors.append(f"Line {i}: {str(rule_error)}")
                        
                        current_rule = []
                        in_rule = False
                else:
                    # Standalone line (might be @import, etc.)
                    if line.startswith('@'):
                        parsed.setdefault('at_rules', []).append(line)
            except Exception as line_error:
                errors.append(f"Line {i}: {str(line_error)}")
                continue
        
        return parsed, errors
    
    def _parse_single_rule(self, rule_text: str, parsed: Dict) -> None:
        """
        Parse a single CSS rule.
        
        Args:
            rule_text: CSS rule text
            parsed: Dictionary to add parsed content to
        """
        # Extract selector and properties
        if '{' in rule_text and '}' in rule_text:
            selector = rule_text[:rule_text.index('{')].strip()
            properties_text = rule_text[rule_text.index('{') + 1:rule_text.rindex('}')]
            
            properties = {}
            for prop in properties_text.split(';'):
                prop = prop.strip()
                if ':' in prop:
                    name, value = prop.split(':', 1)
                    properties[name.strip()] = value.strip()
            
            if selector and properties:
                parsed.setdefault('rules', {})[selector] = properties
    
    def merge_with_recovery(
        self,
        source: Any,
        override: Any,
        merger_func: callable
    ) -> Tuple[Any, List[str]]:
        """
        Perform merge with error recovery.
        
        Args:
            source: Source CSS
            override: Override CSS
            merger_func: Function to perform merge
            
        Returns:
            Tuple of (result, errors)
        """
        errors = []
        
        # Try complete merge first
        try:
            result = merger_func(source, override)
            return result, errors
        except Exception as e:
            errors.append(f"Complete merge failed: {str(e)}")
        
        # Try partial merge - process what we can
        partial_result = {}
        
        # Process source
        if isinstance(source, dict):
            for key, value in source.items():
                try:
                    partial_result[key] = value
                except Exception as e:
                    errors.append(f"Failed to process source {key}: {str(e)}")
        
        # Process override
        if isinstance(override, dict):
            for key, value in override.items():
                try:
                    partial_result[key] = value
                except Exception as e:
                    errors.append(f"Failed to process override {key}: {str(e)}")
        
        return partial_result, errors
    
    def validate_with_recovery(
        self,
        properties: Dict[str, str],
        validator_func: callable
    ) -> Tuple[Dict[str, str], List[str]]:
        """
        Validate properties with recovery.
        
        Args:
            properties: CSS properties to validate
            validator_func: Validation function
            
        Returns:
            Tuple of (valid_properties, errors)
        """
        valid = {}
        errors = []
        
        for prop_name, prop_value in properties.items():
            try:
                if validator_func(prop_name, prop_value):
                    valid[prop_name] = prop_value
                else:
                    if not self.strict:
                        # Include invalid property in non-strict mode
                        valid[prop_name] = prop_value
                    errors.append(f"Invalid property: {prop_name}: {prop_value}")
            except Exception as e:
                errors.append(f"Validation error for {prop_name}: {str(e)}")
                # Include property anyway in non-strict mode
                if not self.strict:
                    valid[prop_name] = prop_value
        
        return valid, errors
    
    def get_error_report(self) -> Dict[str, Any]:
        """
        Get comprehensive error report.
        
        Returns:
            Error report dictionary
        """
        return {
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'recovered_count': self.recovered_count,
            'errors': self.errors,
            'warnings': self.warnings,
            'strict_mode': self.strict
        }
    
    def clear(self) -> None:
        """Clear all errors and warnings."""
        self.errors.clear()
        self.warnings.clear()
        self.recovered_count = 0


class PartialSuccess:
    """Handle partial success scenarios."""
    
    def __init__(self):
        """Initialize partial success handler."""
        self.succeeded: List[Dict[str, Any]] = []
        self.failed: List[Dict[str, Any]] = []
        self.partial: List[Dict[str, Any]] = []
    
    def add_success(self, item: str, details: Optional[Dict] = None) -> None:
        """Add successful operation."""
        self.succeeded.append({
            'item': item,
            'details': details or {}
        })
    
    def add_failure(self, item: str, reason: str, details: Optional[Dict] = None) -> None:
        """Add failed operation."""
        self.failed.append({
            'item': item,
            'reason': reason,
            'details': details or {}
        })
    
    def add_partial(
        self,
        item: str,
        succeeded_parts: List[str],
        failed_parts: List[str],
        details: Optional[Dict] = None
    ) -> None:
        """Add partially successful operation."""
        self.partial.append({
            'item': item,
            'succeeded': succeeded_parts,
            'failed': failed_parts,
            'details': details or {}
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of partial success."""
        total = len(self.succeeded) + len(self.failed) + len(self.partial)
        
        return {
            'total': total,
            'succeeded': len(self.succeeded),
            'failed': len(self.failed),
            'partial': len(self.partial),
            'success_rate': len(self.succeeded) / total if total > 0 else 0,
            'details': {
                'succeeded': self.succeeded,
                'failed': self.failed,
                'partial': self.partial
            }
        }
    
    def merge_results(self, other: 'PartialSuccess') -> None:
        """Merge results from another PartialSuccess instance."""
        self.succeeded.extend(other.succeeded)
        self.failed.extend(other.failed)
        self.partial.extend(other.partial)


def create_fallback_css(properties: Dict[str, str], errors: List[str]) -> str:
    """
    Create fallback CSS from partially parsed properties.
    
    Args:
        properties: Successfully parsed properties
        errors: List of errors encountered
        
    Returns:
        Fallback CSS string
    """
    css_lines = []
    
    # Add error comment
    if errors:
        css_lines.append('/* CSSCade: Partial parse with errors */')
        for error in errors[:5]:  # Limit to first 5 errors
            css_lines.append(f'/* Error: {error} */')
        if len(errors) > 5:
            css_lines.append(f'/* ... and {len(errors) - 5} more errors */')
        css_lines.append('')
    
    # Add successfully parsed properties
    if properties:
        css_lines.append('.recovered {')
        for prop_name, prop_value in properties.items():
            css_lines.append(f'  {prop_name}: {prop_value};')
        css_lines.append('}')
    
    return '\n'.join(css_lines)