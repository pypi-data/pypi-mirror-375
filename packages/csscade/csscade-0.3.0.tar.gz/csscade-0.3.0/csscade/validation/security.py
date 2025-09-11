"""Security checks for CSS content."""

import re
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse


class SecurityChecker:
    """Check CSS for security issues."""
    
    def __init__(self, allow_external_urls: bool = False):
        """
        Initialize security checker.
        
        Args:
            allow_external_urls: Whether to allow external URLs
        """
        self.allow_external_urls = allow_external_urls
        self.issues: List[str] = []
        
        # Dangerous patterns
        self.dangerous_patterns = [
            # JavaScript execution attempts
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
            
            # Expression/behavior (IE specific)
            r'expression\s*\(',
            r'behavior\s*:',
            r'-moz-binding\s*:',
            
            # Import from untrusted sources
            r'@import\s+["\']https?://',
        ]
        
        # Suspicious patterns that warrant warnings
        self.suspicious_patterns = [
            r'position\s*:\s*fixed',  # Can be used for clickjacking
            r'z-index\s*:\s*9999',    # Extremely high z-index
            r'!important.*!important', # Multiple !important
        ]
    
    def check_property_value(self, property_name: str, value: str) -> Tuple[bool, Optional[str]]:
        """
        Check property value for security issues.
        
        Args:
            property_name: CSS property name
            value: Property value
            
        Returns:
            Tuple of (is_safe, issue_description)
        """
        value_lower = value.lower()
        
        # Check for JavaScript URLs
        if 'javascript:' in value_lower or 'vbscript:' in value_lower:
            return False, f"JavaScript execution attempt in {property_name}"
        
        # Check for data URLs with HTML
        if 'data:text/html' in value_lower:
            return False, f"HTML data URL in {property_name}"
        
        # Check for expressions (IE)
        if 'expression(' in value_lower:
            return False, f"IE expression in {property_name}"
        
        # Check for behavior/binding
        if property_name in {'behavior', '-moz-binding'}:
            return False, f"Dangerous property: {property_name}"
        
        # Check URLs in specific properties
        if property_name in {'background-image', 'background', 'list-style-image', 'cursor'}:
            urls = self.extract_urls(value)
            for url in urls:
                is_safe, issue = self.check_url_safety(url)
                if not is_safe:
                    return False, issue
        
        return True, None
    
    def check_url_safety(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Check if URL is safe.
        
        Args:
            url: URL to check
            
        Returns:
            Tuple of (is_safe, issue_description)
        """
        url_lower = url.lower().strip()
        
        # Check for dangerous protocols
        if url_lower.startswith(('javascript:', 'vbscript:', 'data:text/html')):
            return False, f"Dangerous protocol in URL: {url}"
        
        # Check for external URLs if not allowed
        if not self.allow_external_urls:
            parsed = urlparse(url)
            if parsed.scheme in {'http', 'https'}:
                return False, f"External URL not allowed: {url}"
        
        return True, None
    
    def extract_urls(self, value: str) -> List[str]:
        """
        Extract URLs from CSS value.
        
        Args:
            value: CSS value
            
        Returns:
            List of URLs
        """
        urls = []
        
        # Match url() function
        url_pattern = r'url\s*\(\s*["\']?([^"\')]+)["\']?\s*\)'
        matches = re.findall(url_pattern, value, re.IGNORECASE)
        urls.extend(matches)
        
        # Match @import statements
        import_pattern = r'@import\s+["\']([^"\']+)["\']'
        matches = re.findall(import_pattern, value, re.IGNORECASE)
        urls.extend(matches)
        
        return urls
    
    def check_css_injection(self, value: str) -> Tuple[bool, Optional[str]]:
        """
        Check for CSS injection attempts.
        
        Args:
            value: CSS value to check
            
        Returns:
            Tuple of (is_safe, issue_description)
        """
        # Check for unclosed strings that might break out
        if value.count('"') % 2 != 0 or value.count("'") % 2 != 0:
            return False, "Unbalanced quotes detected"
        
        # Check for comment injection
        if '/*' in value and '*/' not in value:
            return False, "Unclosed comment detected"
        
        # Check for escape sequences that might be malicious
        if re.search(r'\\[0-9a-fA-F]{1,6}', value):
            # Unicode escapes are okay, but check for suspicious patterns
            if re.search(r'\\0{0,4}[0-9a-fA-F]{2}', value):
                # Potential null byte or control character
                return False, "Suspicious escape sequence detected"
        
        return True, None
    
    def check_properties(self, properties: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Check dictionary of properties for security issues.
        
        Args:
            properties: CSS properties dictionary
            
        Returns:
            Tuple of (is_safe, list_of_issues)
        """
        self.issues = []
        is_safe = True
        
        for prop_name, prop_value in properties.items():
            # Check property value
            safe, issue = self.check_property_value(prop_name, prop_value)
            if not safe:
                is_safe = False
                self.issues.append(issue)
            
            # Check for injection
            safe, issue = self.check_css_injection(prop_value)
            if not safe:
                is_safe = False
                self.issues.append(issue)
        
        return is_safe, self.issues
    
    def sanitize_value(self, value: str) -> str:
        """
        Sanitize CSS value by removing dangerous content.
        
        Args:
            value: CSS value to sanitize
            
        Returns:
            Sanitized value
        """
        # Remove JavaScript URLs
        value = re.sub(r'javascript:[^;}\s]*', '', value, flags=re.IGNORECASE)
        value = re.sub(r'vbscript:[^;}\s]*', '', value, flags=re.IGNORECASE)
        
        # Remove data URLs with HTML
        value = re.sub(r'data:text/html[^;}\s]*', '', value, flags=re.IGNORECASE)
        
        # Remove expressions
        value = re.sub(r'expression\s*\([^)]*\)', '', value, flags=re.IGNORECASE)
        
        # Remove behavior/binding
        value = re.sub(r'behavior\s*:[^;}\s]*', '', value, flags=re.IGNORECASE)
        value = re.sub(r'-moz-binding\s*:[^;}\s]*', '', value, flags=re.IGNORECASE)
        
        return value.strip()
    
    def sanitize_properties(self, properties: Dict[str, str]) -> Dict[str, str]:
        """
        Sanitize dictionary of CSS properties.
        
        Args:
            properties: CSS properties dictionary
            
        Returns:
            Sanitized properties dictionary
        """
        sanitized = {}
        
        for prop_name, prop_value in properties.items():
            # Skip dangerous properties entirely
            if prop_name.lower() in {'behavior', '-moz-binding'}:
                continue
            
            # Sanitize value
            sanitized_value = self.sanitize_value(prop_value)
            
            # Only include if still has content after sanitization
            if sanitized_value:
                sanitized[prop_name] = sanitized_value
        
        return sanitized


class SafeMode:
    """Safe mode for CSS operations."""
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        """
        Initialize safe mode.
        
        Args:
            dry_run: If True, don't apply changes
            verbose: If True, provide detailed output
        """
        self.dry_run = dry_run
        self.verbose = verbose
        self.operations_log: List[Dict] = []
    
    def log_operation(
        self,
        operation: str,
        source: any,
        override: any,
        result: any,
        warnings: List[str] = None
    ) -> None:
        """
        Log an operation.
        
        Args:
            operation: Operation type
            source: Source data
            override: Override data
            result: Operation result
            warnings: Any warnings
        """
        log_entry = {
            'operation': operation,
            'source': source,
            'override': override,
            'result': result if not self.dry_run else 'DRY RUN - NOT APPLIED',
            'warnings': warnings or []
        }
        
        self.operations_log.append(log_entry)
        
        if self.verbose:
            self._print_operation(log_entry)
    
    def _print_operation(self, log_entry: Dict) -> None:
        """
        Print operation details.
        
        Args:
            log_entry: Log entry to print
        """
        print(f"\n{'='*50}")
        print(f"Operation: {log_entry['operation']}")
        print(f"Dry Run: {self.dry_run}")
        
        if log_entry['warnings']:
            print(f"Warnings:")
            for warning in log_entry['warnings']:
                print(f"  - {warning}")
        
        if self.verbose:
            print(f"Source: {log_entry['source']}")
            print(f"Override: {log_entry['override']}")
            print(f"Result: {log_entry['result']}")
    
    def get_operation_summary(self) -> Dict:
        """
        Get summary of all operations.
        
        Returns:
            Summary dictionary
        """
        total_operations = len(self.operations_log)
        total_warnings = sum(len(op['warnings']) for op in self.operations_log)
        
        return {
            'total_operations': total_operations,
            'total_warnings': total_warnings,
            'dry_run': self.dry_run,
            'operations': self.operations_log
        }
    
    def clear_log(self) -> None:
        """Clear operation log."""
        self.operations_log = []
    
    def would_remove_properties(
        self,
        source: Dict[str, str],
        override: Dict[str, str]
    ) -> List[str]:
        """
        Check which properties would be removed in a merge.
        
        Args:
            source: Source properties
            override: Override properties
            
        Returns:
            List of properties that would be removed
        """
        would_remove = []
        
        for prop in source:
            if prop not in override:
                # Property exists in source but not in override
                # In some merge strategies, this might be removed
                would_remove.append(prop)
        
        return would_remove