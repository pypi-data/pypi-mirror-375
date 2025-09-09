"""Tests for Unicode and special character handling."""

import pytest
from csscade.handlers.unicode_handler import UnicodeHandler


class TestUnicodeHandler:
    """Test Unicode handler functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = UnicodeHandler()
    
    def test_valid_identifier_check(self):
        """Test CSS identifier validation."""
        # Valid identifiers
        assert self.handler.is_valid_identifier('myClass')
        assert self.handler.is_valid_identifier('_private')
        assert self.handler.is_valid_identifier('btn-primary')
        assert self.handler.is_valid_identifier('élément')  # Unicode
        
        # Invalid identifiers
        assert not self.handler.is_valid_identifier('')
        assert not self.handler.is_valid_identifier('123class')  # Starts with digit
        assert not self.handler.is_valid_identifier('-123')  # Hyphen then digit
    
    def test_escape_identifier(self):
        """Test identifier escaping."""
        # Normal identifier
        assert self.handler.escape_identifier('myClass') == 'myClass'
        
        # Identifier with special characters
        assert self.handler.escape_identifier('my.class') == 'my\\.class'
        assert self.handler.escape_identifier('my#id') == 'my\\#id'
        
        # Identifier starting with digit
        assert '\\3' in self.handler.escape_identifier('3col')
        
        # Hyphen at start followed by digit
        assert '\\2d' in self.handler.escape_identifier('-3col')
    
    def test_escape_string(self):
        """Test string escaping for CSS."""
        # Simple string
        assert self.handler.escape_string('hello') == '"hello"'
        
        # String with quotes
        assert self.handler.escape_string('say "hello"') == '"say \\"hello\\""'
        assert self.handler.escape_string("it's", "'") == "'it\\'s'"
        
        # String with newlines
        assert self.handler.escape_string('line1\nline2') == '"line1\\nline2"'
        
        # String with backslashes
        assert self.handler.escape_string('path\\to\\file') == '"path\\\\to\\\\file"'
    
    def test_unescape_unicode(self):
        """Test Unicode unescaping."""
        # Simple Unicode escape
        assert self.handler.unescape_unicode('\\41') == 'A'
        assert self.handler.unescape_unicode('\\0041') == 'A'
        
        # Multiple escapes
        text = '\\48\\65\\6c\\6c\\6f'
        assert 'Hello' in self.handler.unescape_unicode(text)
        
        # Invalid escape (out of range)
        invalid = '\\110000'  # Beyond Unicode range
        assert '\\110000' in self.handler.unescape_unicode(invalid)
    
    def test_normalize_unicode(self):
        """Test Unicode normalization."""
        # Combining characters
        composed = 'é'  # Single character
        decomposed = 'e\u0301'  # e + combining accent
        
        # NFC normalization (composed)
        assert self.handler.normalize_unicode(decomposed, 'NFC') == composed
        
        # NFD normalization (decomposed)
        assert len(self.handler.normalize_unicode(composed, 'NFD')) == 2
    
    def test_handle_bidi_text(self):
        """Test bidirectional text handling."""
        # LTR text
        ltr_text = 'Hello World'
        assert self.handler.handle_bidi_text(ltr_text) == ltr_text
        
        # RTL text (Arabic)
        rtl_text = 'مرحبا'
        result = self.handler.handle_bidi_text(rtl_text)
        assert '\u202D' in result  # LTR override
        assert '\u202C' in result  # Pop directional
    
    def test_sanitize_selector(self):
        """Test CSS selector sanitization."""
        # Class selector
        assert self.handler.sanitize_selector('.my-class') == '.my-class'
        assert self.handler.sanitize_selector('.my.class') == '.my\\.class'
        
        # ID selector
        assert self.handler.sanitize_selector('#my-id') == '#my-id'
        assert self.handler.sanitize_selector('#my#id') == '#my\\#id'
        
        # Attribute selector
        selector = '[data-value="test"]'
        result = self.handler.sanitize_selector(selector)
        assert '[data-value="test"]' in result
        
        # Unquoted attribute value
        selector = '[data-value=test-123]'
        result = self.handler.sanitize_selector(selector)
        assert 'test-123' in result
    
    def test_process_css_with_unicode(self):
        """Test processing CSS with Unicode support."""
        css = """.café {
    color: red;
}
#naïve {
    background: blue;
}"""
        
        result = self.handler.process_css_with_unicode(css)
        assert '.café' in result or '.caf\\e9' in result
        assert '#naïve' in result or '#na\\efve' in result
    
    def test_encode_for_css(self):
        """Test encoding text for CSS."""
        # ASCII text
        assert self.handler.encode_for_css('hello') == 'hello'
        
        # Special CSS characters
        assert self.handler.encode_for_css('a.b') == 'a\\.b'
        assert self.handler.encode_for_css('a#b') == 'a\\#b'
        
        # Non-ASCII characters
        encoded = self.handler.encode_for_css('café')
        assert 'caf' in encoded
        assert '\\e9 ' in encoded or 'é' in encoded
        
        # Control characters
        encoded = self.handler.encode_for_css('line\nbreak')
        assert '\\a ' in encoded
    
    def test_decode_from_css(self):
        """Test decoding CSS-encoded text."""
        # Unicode escapes
        assert self.handler.decode_from_css('\\41') == 'A'
        
        # Simple escapes
        assert self.handler.decode_from_css('\\#') == '#'
        assert self.handler.decode_from_css('\\.') == '.'
        
        # Mixed content
        assert self.handler.decode_from_css('hello\\20world') == 'hello world'
    
    def test_edge_cases(self):
        """Test edge cases."""
        # Empty input
        assert self.handler.escape_identifier('') == ''
        assert self.handler.escape_string('') == '""'
        assert self.handler.unescape_unicode('') == ''
        
        # Very long Unicode escape
        assert self.handler.unescape_unicode('\\000041') == 'A'
        
        # Mixed RTL and LTR text
        mixed = 'Hello مرحبا World'
        result = self.handler.handle_bidi_text(mixed)
        assert '\u202D' in result