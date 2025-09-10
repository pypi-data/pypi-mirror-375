"""Unicode and special character handling for CSS."""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple


class UnicodeHandler:
    """Handle Unicode and special characters in CSS."""
    
    def __init__(self):
        """Initialize Unicode handler."""
        # Characters that need escaping in CSS
        self.special_chars = {
            '!', '"', '#', '$', '%', '&', "'", '(', ')', '*',
            '+', ',', '.', '/', ':', ';', '<', '=', '>', '?',
            '@', '[', '\\', ']', '^', '`', '{', '|', '}', '~'
        }
        
        # CSS identifier pattern
        self.identifier_pattern = re.compile(r'^[a-zA-Z_\u0080-\uFFFF][\w\u0080-\uFFFF-]*$')
        
        # Unicode escape pattern
        self.unicode_escape_pattern = re.compile(r'\\([0-9a-fA-F]{1,6})\s?')
    
    def is_valid_identifier(self, identifier: str) -> bool:
        """
        Check if string is a valid CSS identifier.
        
        Args:
            identifier: String to check
            
        Returns:
            True if valid CSS identifier
        """
        if not identifier:
            return False
        
        # Check if it matches CSS identifier pattern
        return bool(self.identifier_pattern.match(identifier))
    
    def escape_identifier(self, identifier: str) -> str:
        """
        Escape special characters in CSS identifier.
        
        Args:
            identifier: CSS identifier to escape
            
        Returns:
            Escaped identifier
        """
        if not identifier:
            return identifier
        
        result = []
        
        for i, char in enumerate(identifier):
            # First character has special rules
            if i == 0:
                if char.isdigit():
                    # Digits at start need escaping
                    result.append(f'\\{ord(char):x} ')
                elif char == '-':
                    # Hyphen at start needs special handling
                    if len(identifier) > 1 and identifier[1].isdigit():
                        result.append(f'\\{ord(char):x} ')
                    else:
                        result.append(char)
                elif char in self.special_chars:
                    result.append(f'\\{char}')
                else:
                    result.append(char)
            else:
                if char in self.special_chars:
                    result.append(f'\\{char}')
                elif ord(char) > 127:
                    # Non-ASCII characters can be escaped
                    result.append(char)  # Keep as-is, CSS supports Unicode
                else:
                    result.append(char)
        
        return ''.join(result)
    
    def escape_string(self, string: str, quote_char: str = '"') -> str:
        """
        Escape string for use in CSS.
        
        Args:
            string: String to escape
            quote_char: Quote character to use
            
        Returns:
            Escaped string with quotes
        """
        # Escape backslashes first
        escaped = string.replace('\\', '\\\\')
        
        # Escape the quote character
        escaped = escaped.replace(quote_char, f'\\{quote_char}')
        
        # Escape newlines and other control characters
        escaped = escaped.replace('\n', '\\n')
        escaped = escaped.replace('\r', '\\r')
        escaped = escaped.replace('\t', '\\t')
        
        return f'{quote_char}{escaped}{quote_char}'
    
    def unescape_unicode(self, text: str) -> str:
        """
        Unescape Unicode escape sequences in CSS.
        
        Args:
            text: CSS text with escape sequences
            
        Returns:
            Text with Unicode characters
        """
        def replace_escape(match):
            code_point = int(match.group(1), 16)
            if code_point <= 0x10FFFF:  # Valid Unicode range
                return chr(code_point)
            return match.group(0)  # Keep invalid escapes as-is
        
        return self.unicode_escape_pattern.sub(replace_escape, text)
    
    def normalize_unicode(self, text: str, form: str = 'NFC') -> str:
        """
        Normalize Unicode text.
        
        Args:
            text: Text to normalize
            form: Normalization form (NFC, NFD, NFKC, NFKD)
            
        Returns:
            Normalized text
        """
        return unicodedata.normalize(form, text)
    
    def handle_bidi_text(self, text: str) -> str:
        """
        Handle bidirectional text in CSS.
        
        Args:
            text: Text that may contain RTL characters
            
        Returns:
            Text with proper directional marks
        """
        # Check if text contains RTL characters
        has_rtl = any(
            unicodedata.bidirectional(char) in ('R', 'AL')
            for char in text
        )
        
        if has_rtl:
            # Add directional marks for proper display
            # Left-to-right mark (LRM) and Right-to-left mark (RLM)
            return f'\u202D{text}\u202C'  # LTR override and pop directional
        
        return text
    
    def sanitize_selector(self, selector: str) -> str:
        """
        Sanitize CSS selector for special characters.
        
        Args:
            selector: CSS selector
            
        Returns:
            Sanitized selector
        """
        # Handle class selectors
        if selector.startswith('.'):
            class_name = selector[1:]
            escaped = self.escape_identifier(class_name)
            return f'.{escaped}'
        
        # Handle ID selectors
        if selector.startswith('#'):
            id_name = selector[1:]
            escaped = self.escape_identifier(id_name)
            return f'#{escaped}'
        
        # Handle attribute selectors
        if '[' in selector and ']' in selector:
            # Extract and escape attribute value
            pattern = r'\[([^=\]]+)(=["\']?)([^"\'\]]*)?(["\']?)\]'
            
            def escape_attr(match):
                attr = match.group(1)
                op = match.group(2) or ''
                value = match.group(3) or ''
                quote = match.group(4) or ''
                
                if value and not quote:
                    # Unquoted value needs escaping
                    value = self.escape_identifier(value)
                
                return f'[{attr}{op}{value}{quote}]'
            
            selector = re.sub(pattern, escape_attr, selector)
        
        return selector
    
    def process_css_with_unicode(self, css_text: str) -> str:
        """
        Process CSS text with Unicode support.
        
        Args:
            css_text: CSS text that may contain Unicode
            
        Returns:
            Processed CSS text
        """
        # Normalize Unicode
        css_text = self.normalize_unicode(css_text)
        
        # Process each rule
        lines = []
        for line in css_text.split('\n'):
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('/*'):
                lines.append(line)
                continue
            
            # Check for selectors (lines ending with {)
            if '{' in line:
                selector_part = line[:line.index('{')]
                rest = line[line.index('{'):]
                
                # Sanitize selector
                selector_part = self.sanitize_selector(selector_part.strip())
                lines.append(f'{selector_part} {rest}')
            else:
                lines.append(line)
        
        return '\n'.join(lines)
    
    def encode_for_css(self, text: str) -> str:
        """
        Encode text for safe use in CSS.
        
        Args:
            text: Text to encode
            
        Returns:
            CSS-safe encoded text
        """
        encoded = []
        
        for char in text:
            code_point = ord(char)
            
            # ASCII printable characters (except special CSS chars)
            if 32 <= code_point <= 126:
                if char in self.special_chars:
                    encoded.append(f'\\{char}')
                else:
                    encoded.append(char)
            # Non-ASCII or control characters
            else:
                encoded.append(f'\\{code_point:x} ')
        
        return ''.join(encoded)
    
    def decode_from_css(self, text: str) -> str:
        """
        Decode CSS-encoded text.
        
        Args:
            text: CSS-encoded text
            
        Returns:
            Decoded text
        """
        # Handle Unicode escapes
        text = self.unescape_unicode(text)
        
        # Handle simple escapes
        text = re.sub(r'\\(.)', r'\1', text)
        
        return text