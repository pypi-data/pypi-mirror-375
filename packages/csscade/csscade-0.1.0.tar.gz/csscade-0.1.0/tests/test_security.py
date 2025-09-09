"""Tests for CSS security checks."""

import pytest
from csscade.validation import SecurityChecker, SafeMode


class TestSecurityChecker:
    """Test cases for security checker."""
    
    def test_check_javascript_urls(self):
        """Test detecting JavaScript URLs."""
        checker = SecurityChecker()
        
        # Test dangerous JavaScript URL
        is_safe, issue = checker.check_property_value(
            'background-image',
            'url(javascript:alert(1))'
        )
        assert is_safe is False
        assert 'JavaScript execution' in issue
        
        # Test safe URL
        is_safe, issue = checker.check_property_value(
            'background-image',
            'url(image.png)'
        )
        assert is_safe is True
        assert issue is None
    
    def test_check_data_urls(self):
        """Test detecting dangerous data URLs."""
        checker = SecurityChecker()
        
        # Dangerous HTML data URL
        is_safe, issue = checker.check_property_value(
            'background',
            'url(data:text/html,<script>alert(1)</script>)'
        )
        assert is_safe is False
        assert 'HTML data URL' in issue
        
        # Safe image data URL
        is_safe, issue = checker.check_property_value(
            'background',
            'url(data:image/png;base64,iVBORw0KG...)'
        )
        assert is_safe is True
    
    def test_check_expressions(self):
        """Test detecting IE expressions."""
        checker = SecurityChecker()
        
        is_safe, issue = checker.check_property_value(
            'width',
            'expression(document.body.clientWidth)'
        )
        assert is_safe is False
        assert 'expression' in issue
    
    def test_check_behavior_binding(self):
        """Test detecting behavior and binding properties."""
        checker = SecurityChecker()
        
        # IE behavior
        is_safe, issue = checker.check_property_value(
            'behavior',
            'url(script.htc)'
        )
        assert is_safe is False
        assert 'Dangerous property' in issue
        
        # Mozilla binding
        is_safe, issue = checker.check_property_value(
            '-moz-binding',
            'url(binding.xml)'
        )
        assert is_safe is False
        assert 'Dangerous property' in issue
    
    def test_check_external_urls(self):
        """Test checking external URLs."""
        # Disallow external URLs
        checker = SecurityChecker(allow_external_urls=False)
        
        is_safe, issue = checker.check_url_safety('http://external.com/image.png')
        assert is_safe is False
        assert 'External URL not allowed' in issue
        
        # Allow external URLs
        checker = SecurityChecker(allow_external_urls=True)
        
        is_safe, issue = checker.check_url_safety('http://external.com/image.png')
        assert is_safe is True
    
    def test_extract_urls(self):
        """Test extracting URLs from CSS values."""
        checker = SecurityChecker()
        
        # url() function
        urls = checker.extract_urls('url(image.png) url("other.jpg")')
        assert 'image.png' in urls
        assert 'other.jpg' in urls
        
        # @import statement
        urls = checker.extract_urls('@import "style.css"')
        assert 'style.css' in urls
    
    def test_check_css_injection(self):
        """Test detecting CSS injection attempts."""
        checker = SecurityChecker()
        
        # Unbalanced quotes
        is_safe, issue = checker.check_css_injection('value"breakout')
        assert is_safe is False
        assert 'Unbalanced quotes' in issue
        
        # Unclosed comment
        is_safe, issue = checker.check_css_injection('/* unclosed comment')
        assert is_safe is False
        assert 'Unclosed comment' in issue
        
        # Safe value
        is_safe, issue = checker.check_css_injection('normal value')
        assert is_safe is True
    
    def test_check_properties(self):
        """Test checking multiple properties."""
        checker = SecurityChecker()
        
        properties = {
            'color': 'red',
            'background': 'url(javascript:alert(1))',
            'width': 'expression(evil())'
        }
        
        is_safe, issues = checker.check_properties(properties)
        assert is_safe is False
        assert len(issues) >= 2
    
    def test_sanitize_value(self):
        """Test sanitizing CSS values."""
        checker = SecurityChecker()
        
        # Remove JavaScript URL
        sanitized = checker.sanitize_value('url(javascript:alert(1))')
        assert 'javascript:' not in sanitized
        
        # Remove expression
        sanitized = checker.sanitize_value('expression(document.body.clientWidth)')
        assert 'expression' not in sanitized
        
        # Keep safe content
        sanitized = checker.sanitize_value('10px solid red')
        assert sanitized == '10px solid red'
    
    def test_sanitize_properties(self):
        """Test sanitizing property dictionary."""
        checker = SecurityChecker()
        
        properties = {
            'color': 'red',
            'background': 'url(javascript:alert(1))',
            'behavior': 'url(script.htc)',
            'width': '100px'
        }
        
        sanitized = checker.sanitize_properties(properties)
        
        assert sanitized['color'] == 'red'
        assert sanitized['width'] == '100px'
        assert 'behavior' not in sanitized  # Removed entirely
        assert 'javascript' not in sanitized.get('background', '')


class TestSafeMode:
    """Test cases for safe mode."""
    
    def test_dry_run_mode(self):
        """Test dry run mode."""
        safe_mode = SafeMode(dry_run=True)
        
        safe_mode.log_operation(
            'merge',
            {'color': 'red'},
            {'color': 'blue'},
            {'color': 'blue'}
        )
        
        log = safe_mode.operations_log[0]
        assert 'DRY RUN' in log['result']
    
    def test_verbose_mode(self, capsys):
        """Test verbose mode output."""
        safe_mode = SafeMode(verbose=True)
        
        safe_mode.log_operation(
            'merge',
            {'color': 'red'},
            {'color': 'blue'},
            {'color': 'blue'},
            warnings=['Test warning']
        )
        
        captured = capsys.readouterr()
        assert 'Operation: merge' in captured.out
        assert 'Test warning' in captured.out
    
    def test_operation_logging(self):
        """Test operation logging."""
        safe_mode = SafeMode()
        
        safe_mode.log_operation('op1', 'source1', 'override1', 'result1')
        safe_mode.log_operation('op2', 'source2', 'override2', 'result2')
        
        assert len(safe_mode.operations_log) == 2
        assert safe_mode.operations_log[0]['operation'] == 'op1'
        assert safe_mode.operations_log[1]['operation'] == 'op2'
    
    def test_operation_summary(self):
        """Test getting operation summary."""
        safe_mode = SafeMode()
        
        safe_mode.log_operation('op1', 's1', 'o1', 'r1', ['warning1'])
        safe_mode.log_operation('op2', 's2', 'o2', 'r2', ['warning2', 'warning3'])
        
        summary = safe_mode.get_operation_summary()
        
        assert summary['total_operations'] == 2
        assert summary['total_warnings'] == 3
        assert summary['dry_run'] is False
        assert len(summary['operations']) == 2
    
    def test_would_remove_properties(self):
        """Test checking which properties would be removed."""
        safe_mode = SafeMode()
        
        source = {'color': 'red', 'margin': '10px', 'padding': '5px'}
        override = {'color': 'blue', 'margin': '20px'}
        
        would_remove = safe_mode.would_remove_properties(source, override)
        
        assert 'padding' in would_remove
        assert 'color' not in would_remove
        assert 'margin' not in would_remove
    
    def test_clear_log(self):
        """Test clearing operation log."""
        safe_mode = SafeMode()
        
        safe_mode.log_operation('op1', 's1', 'o1', 'r1')
        assert len(safe_mode.operations_log) == 1
        
        safe_mode.clear_log()
        assert len(safe_mode.operations_log) == 0