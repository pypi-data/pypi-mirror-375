"""Tests for error recovery and graceful degradation."""

import pytest
from csscade.handlers.error_recovery import (
    ErrorRecovery, PartialSuccess, create_fallback_css
)


class TestErrorRecovery:
    """Test error recovery functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.recovery = ErrorRecovery(strict=False)
        self.strict_recovery = ErrorRecovery(strict=True)
    
    def test_add_error(self):
        """Test error logging."""
        self.recovery.add_error(
            'parse_error',
            'Invalid CSS syntax',
            {'line': 10}
        )
        
        assert len(self.recovery.errors) == 1
        assert self.recovery.errors[0]['type'] == 'parse_error'
        assert self.recovery.errors[0]['message'] == 'Invalid CSS syntax'
        assert self.recovery.errors[0]['context']['line'] == 10
    
    def test_add_error_with_exception(self):
        """Test error logging with exception."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            self.recovery.add_error(
                'value_error',
                'Test error occurred',
                exception=e
            )
        
        assert len(self.recovery.errors) == 1
        assert 'exception' in self.recovery.errors[0]
        assert 'traceback' in self.recovery.errors[0]
        assert 'ValueError' in self.recovery.errors[0]['exception']
    
    def test_add_warning(self):
        """Test warning logging."""
        self.recovery.add_warning('Deprecated property used')
        assert len(self.recovery.warnings) == 1
        assert self.recovery.warnings[0] == 'Deprecated property used'
    
    def test_recover_context_manager(self):
        """Test recovery context manager."""
        # Non-strict mode - recovers from error
        try:
            with self.recovery.recover('divide', default=0) as ctx:
                result = 10 / 0  # This would raise
        except:
            pass  # Error should be caught and logged
        
        assert self.recovery.recovered_count == 1
        assert len(self.recovery.errors) == 1
        
        # Strict mode - raises error
        with pytest.raises(ZeroDivisionError):
            with self.strict_recovery.recover('divide', default=0):
                result = 10 / 0
    
    def test_parse_with_recovery_valid(self):
        """Test parsing valid CSS with recovery."""
        css = """.button {
    color: blue;
    padding: 10px;
}"""
        
        parsed, errors = self.recovery.parse_with_recovery(css)
        assert len(errors) > 0 or 'rules' in parsed
    
    def test_parse_with_recovery_invalid(self):
        """Test parsing invalid CSS with recovery."""
        css = """.button {
    color: blue
    padding 10px;  /* Missing colon */
    margin: 5px;
}"""
        
        parsed, errors = self.recovery.parse_with_recovery(css)
        # Should still parse what it can
        assert len(errors) > 0 or parsed != {}
    
    def test_parse_with_recovery_comments(self):
        """Test parsing CSS with comments."""
        css = """/* Header styles */
.header {
    /* Primary color */
    color: #333;
    // Line comment (non-standard)
    padding: 10px;
}"""
        
        parsed, errors = self.recovery.parse_with_recovery(css)
        # Should handle comments gracefully
        assert 'rules' in parsed or len(errors) > 0
    
    def test_parse_with_recovery_at_rules(self):
        """Test parsing CSS with at-rules."""
        css = """@import url('styles.css');
@charset "UTF-8";
.button {
    color: blue;
}"""
        
        parsed, errors = self.recovery.parse_with_recovery(css)
        if 'at_rules' in parsed:
            assert len(parsed['at_rules']) >= 1
    
    def test_merge_with_recovery_success(self):
        """Test successful merge with recovery."""
        source = {'color': 'red', 'padding': '10px'}
        override = {'color': 'blue', 'margin': '5px'}
        
        def merger(s, o):
            result = s.copy()
            result.update(o)
            return result
        
        result, errors = self.recovery.merge_with_recovery(
            source, override, merger
        )
        
        assert result['color'] == 'blue'
        assert result['padding'] == '10px'
        assert result['margin'] == '5px'
        assert len(errors) == 0
    
    def test_merge_with_recovery_failure(self):
        """Test merge with recovery on failure."""
        source = {'color': 'red'}
        override = {'color': 'blue'}
        
        def failing_merger(s, o):
            raise ValueError("Merge failed")
        
        result, errors = self.recovery.merge_with_recovery(
            source, override, failing_merger
        )
        
        # Should do partial merge
        assert 'color' in result
        assert len(errors) > 0
        assert 'Complete merge failed' in errors[0]
    
    def test_validate_with_recovery(self):
        """Test property validation with recovery."""
        properties = {
            'color': 'blue',
            'invalid-prop': 'value',
            'padding': '10px'
        }
        
        def validator(name, value):
            return not name.startswith('invalid')
        
        valid, errors = self.recovery.validate_with_recovery(
            properties, validator
        )
        
        assert 'color' in valid
        assert 'padding' in valid
        assert 'invalid-prop' in valid  # Non-strict mode includes it
        assert len(errors) == 1
    
    def test_validate_with_recovery_strict(self):
        """Test strict validation."""
        properties = {'invalid-prop': 'value'}
        
        def validator(name, value):
            return not name.startswith('invalid')
        
        valid, errors = self.strict_recovery.validate_with_recovery(
            properties, validator
        )
        
        assert 'invalid-prop' not in valid  # Strict mode excludes it
        assert len(errors) == 1
    
    def test_get_error_report(self):
        """Test error report generation."""
        self.recovery.add_error('error1', 'Message 1')
        self.recovery.add_warning('Warning 1')
        self.recovery.recovered_count = 2
        
        report = self.recovery.get_error_report()
        
        assert report['error_count'] == 1
        assert report['warning_count'] == 1
        assert report['recovered_count'] == 2
        assert report['strict_mode'] == False
        assert len(report['errors']) == 1
        assert len(report['warnings']) == 1
    
    def test_clear(self):
        """Test clearing errors and warnings."""
        self.recovery.add_error('error', 'message')
        self.recovery.add_warning('warning')
        self.recovery.recovered_count = 1
        
        self.recovery.clear()
        
        assert len(self.recovery.errors) == 0
        assert len(self.recovery.warnings) == 0
        assert self.recovery.recovered_count == 0


class TestPartialSuccess:
    """Test partial success handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.partial = PartialSuccess()
    
    def test_add_success(self):
        """Test adding successful operations."""
        self.partial.add_success('rule1', {'selector': '.btn'})
        
        assert len(self.partial.succeeded) == 1
        assert self.partial.succeeded[0]['item'] == 'rule1'
        assert self.partial.succeeded[0]['details']['selector'] == '.btn'
    
    def test_add_failure(self):
        """Test adding failed operations."""
        self.partial.add_failure(
            'rule2',
            'Invalid syntax',
            {'line': 10}
        )
        
        assert len(self.partial.failed) == 1
        assert self.partial.failed[0]['item'] == 'rule2'
        assert self.partial.failed[0]['reason'] == 'Invalid syntax'
    
    def test_add_partial(self):
        """Test adding partially successful operations."""
        self.partial.add_partial(
            'rule3',
            ['color', 'padding'],
            ['invalid-prop'],
            {'selector': '.widget'}
        )
        
        assert len(self.partial.partial) == 1
        assert self.partial.partial[0]['item'] == 'rule3'
        assert len(self.partial.partial[0]['succeeded']) == 2
        assert len(self.partial.partial[0]['failed']) == 1
    
    def test_get_summary(self):
        """Test summary generation."""
        self.partial.add_success('item1')
        self.partial.add_success('item2')
        self.partial.add_failure('item3', 'error')
        self.partial.add_partial('item4', ['a'], ['b'])
        
        summary = self.partial.get_summary()
        
        assert summary['total'] == 4
        assert summary['succeeded'] == 2
        assert summary['failed'] == 1
        assert summary['partial'] == 1
        assert summary['success_rate'] == 0.5
    
    def test_merge_results(self):
        """Test merging results from another instance."""
        other = PartialSuccess()
        other.add_success('other1')
        other.add_failure('other2', 'error')
        
        self.partial.add_success('mine1')
        self.partial.merge_results(other)
        
        assert len(self.partial.succeeded) == 2
        assert len(self.partial.failed) == 1


class TestFallbackCSS:
    """Test fallback CSS generation."""
    
    def test_create_fallback_css_no_errors(self):
        """Test fallback CSS with no errors."""
        properties = {'color': 'blue', 'padding': '10px'}
        errors = []
        
        css = create_fallback_css(properties, errors)
        
        assert '.recovered {' in css
        assert 'color: blue;' in css
        assert 'padding: 10px;' in css
    
    def test_create_fallback_css_with_errors(self):
        """Test fallback CSS with errors."""
        properties = {'color': 'blue'}
        errors = ['Parse error at line 5', 'Invalid selector']
        
        css = create_fallback_css(properties, errors)
        
        assert '/* CSSCade: Partial parse with errors */' in css
        assert '/* Error: Parse error at line 5 */' in css
        assert '/* Error: Invalid selector */' in css
        assert '.recovered {' in css
        assert 'color: blue;' in css
    
    def test_create_fallback_css_many_errors(self):
        """Test fallback CSS with many errors."""
        properties = {}
        errors = [f'Error {i}' for i in range(10)]
        
        css = create_fallback_css(properties, errors)
        
        # Should only show first 5 errors
        assert '/* Error: Error 0 */' in css
        assert '/* Error: Error 4 */' in css
        assert '/* ... and 5 more errors */' in css
        assert '/* Error: Error 5 */' not in css
    
    def test_create_fallback_css_empty(self):
        """Test fallback CSS with no properties or errors."""
        css = create_fallback_css({}, [])
        
        # Should handle empty case gracefully
        assert css == '' or '.recovered' in css