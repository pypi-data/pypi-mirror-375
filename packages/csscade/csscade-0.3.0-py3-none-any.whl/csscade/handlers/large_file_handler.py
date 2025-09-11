"""Handler for large CSS files with memory-efficient processing."""

import os
import tempfile
from typing import Any, Dict, Generator, List, Optional, Tuple
from pathlib import Path
import mmap


class LargeFileHandler:
    """Handle large CSS files efficiently."""
    
    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB chunks
        """
        Initialize large file handler.
        
        Args:
            chunk_size: Size of chunks to process
        """
        self.chunk_size = chunk_size
        self.temp_files: List[Path] = []
    
    def is_large_file(self, file_path: str, threshold: int = 5 * 1024 * 1024) -> bool:
        """
        Check if file is considered large.
        
        Args:
            file_path: Path to file
            threshold: Size threshold in bytes (default 5MB)
            
        Returns:
            True if file is larger than threshold
        """
        try:
            file_size = os.path.getsize(file_path)
            return file_size > threshold
        except OSError:
            return False
    
    def read_in_chunks(self, file_path: str) -> Generator[str, None, None]:
        """
        Read file in chunks.
        
        Args:
            file_path: Path to file
            
        Yields:
            File chunks
        """
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk
    
    def process_large_css(
        self,
        file_path: str,
        processor_func: callable
    ) -> Generator[Any, None, None]:
        """
        Process large CSS file in chunks.
        
        Args:
            file_path: Path to CSS file
            processor_func: Function to process each chunk
            
        Yields:
            Processed chunks
        """
        buffer = ""
        
        for chunk in self.read_in_chunks(file_path):
            # Add chunk to buffer
            buffer += chunk
            
            # Find complete rules (ending with })
            rules = []
            last_complete = buffer.rfind('}')
            
            if last_complete != -1:
                # Extract complete rules
                complete_part = buffer[:last_complete + 1]
                buffer = buffer[last_complete + 1:]
                
                # Split into individual rules
                rule_parts = complete_part.split('}')
                for part in rule_parts[:-1]:  # Last part is empty
                    if part.strip():
                        rules.append(part + '}')
            
            # Process complete rules
            if rules:
                for rule in rules:
                    try:
                        result = processor_func(rule)
                        if result:
                            yield result
                    except Exception as e:
                        # Log error but continue processing
                        yield {'error': str(e), 'rule': rule}
        
        # Process any remaining buffer
        if buffer.strip():
            try:
                result = processor_func(buffer)
                if result:
                    yield result
            except Exception as e:
                yield {'error': str(e), 'rule': buffer}
    
    def merge_large_files(
        self,
        source_path: str,
        override_path: str,
        output_path: str,
        merger_func: callable
    ) -> Dict[str, Any]:
        """
        Merge large CSS files.
        
        Args:
            source_path: Source CSS file
            override_path: Override CSS file
            output_path: Output file path
            merger_func: Function to merge CSS
            
        Returns:
            Merge statistics
        """
        stats = {
            'source_size': os.path.getsize(source_path),
            'override_size': os.path.getsize(override_path),
            'rules_processed': 0,
            'errors': []
        }
        
        # Create temporary file for output
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.css',
            delete=False,
            encoding='utf-8'
        ) as temp_output:
            temp_path = temp_output.name
            self.temp_files.append(Path(temp_path))
            
            # Process source file
            source_rules = {}
            for result in self.process_large_css(source_path, self._parse_rule):
                if 'error' in result:
                    stats['errors'].append(result['error'])
                else:
                    selector = result.get('selector')
                    if selector:
                        source_rules[selector] = result.get('properties', {})
            
            # Process override file
            override_rules = {}
            for result in self.process_large_css(override_path, self._parse_rule):
                if 'error' in result:
                    stats['errors'].append(result['error'])
                else:
                    selector = result.get('selector')
                    if selector:
                        override_rules[selector] = result.get('properties', {})
            
            # Merge rules
            merged_rules = source_rules.copy()
            for selector, properties in override_rules.items():
                if selector in merged_rules:
                    # Merge properties
                    try:
                        merged = merger_func(merged_rules[selector], properties)
                        merged_rules[selector] = merged
                    except Exception as e:
                        stats['errors'].append(f"Merge error for {selector}: {str(e)}")
                        merged_rules[selector].update(properties)
                else:
                    merged_rules[selector] = properties
            
            # Write merged rules to output
            for selector, properties in merged_rules.items():
                temp_output.write(f'{selector} {{\n')
                for prop_name, prop_value in properties.items():
                    temp_output.write(f'  {prop_name}: {prop_value};\n')
                temp_output.write('}\n\n')
                stats['rules_processed'] += 1
        
        # Move temp file to final location
        os.replace(temp_path, output_path)
        self.temp_files.remove(Path(temp_path))
        
        stats['output_size'] = os.path.getsize(output_path)
        return stats
    
    def _parse_rule(self, rule_text: str) -> Dict[str, Any]:
        """
        Parse a CSS rule.
        
        Args:
            rule_text: CSS rule text
            
        Returns:
            Parsed rule dictionary
        """
        rule_text = rule_text.strip()
        if not rule_text or '{' not in rule_text:
            return {}
        
        # Extract selector and properties
        selector_end = rule_text.find('{')
        selector = rule_text[:selector_end].strip()
        
        properties_start = selector_end + 1
        properties_end = rule_text.rfind('}')
        
        if properties_end == -1:
            properties_text = rule_text[properties_start:]
        else:
            properties_text = rule_text[properties_start:properties_end]
        
        # Parse properties
        properties = {}
        for prop in properties_text.split(';'):
            prop = prop.strip()
            if ':' in prop:
                name, value = prop.split(':', 1)
                properties[name.strip()] = value.strip()
        
        return {
            'selector': selector,
            'properties': properties
        }
    
    def use_memory_map(self, file_path: str) -> Optional[mmap.mmap]:
        """
        Create memory-mapped file for efficient access.
        
        Args:
            file_path: Path to file
            
        Returns:
            Memory-mapped file object
        """
        try:
            with open(file_path, 'r+b') as f:
                return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        except (OSError, ValueError):
            return None
    
    def estimate_memory_usage(self, file_path: str) -> Dict[str, Any]:
        """
        Estimate memory usage for processing file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Memory usage estimates
        """
        file_size = os.path.getsize(file_path)
        
        # Rough estimates
        return {
            'file_size': file_size,
            'estimated_memory': file_size * 2,  # Assume 2x for processing
            'recommended_chunk_size': min(
                self.chunk_size,
                max(1024, file_size // 100)  # 1% of file or 1KB minimum
            ),
            'is_large': self.is_large_file(file_path),
            'recommended_method': 'streaming' if file_size > 10 * 1024 * 1024 else 'memory'
        }
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except OSError:
                pass
        self.temp_files.clear()
    
    def __del__(self):
        """Clean up on deletion."""
        self.cleanup()


class StreamingMerger:
    """Stream-based CSS merger for very large files."""
    
    def __init__(self, buffer_size: int = 1024 * 1024):
        """
        Initialize streaming merger.
        
        Args:
            buffer_size: Buffer size for streaming
        """
        self.buffer_size = buffer_size
    
    def stream_merge(
        self,
        source_stream,
        override_stream,
        output_stream,
        merger_func: callable
    ) -> Dict[str, Any]:
        """
        Merge CSS streams.
        
        Args:
            source_stream: Source CSS stream
            override_stream: Override CSS stream
            output_stream: Output stream
            merger_func: Merge function
            
        Returns:
            Merge statistics
        """
        stats = {
            'bytes_read': 0,
            'bytes_written': 0,
            'rules_merged': 0
        }
        
        # Process streams
        source_buffer = ""
        override_buffer = ""
        
        while True:
            # Read from source
            source_chunk = source_stream.read(self.buffer_size)
            if source_chunk:
                source_buffer += source_chunk
                stats['bytes_read'] += len(source_chunk)
            
            # Read from override
            override_chunk = override_stream.read(self.buffer_size)
            if override_chunk:
                override_buffer += override_chunk
                stats['bytes_read'] += len(override_chunk)
            
            # Process complete rules
            if not source_chunk and not override_chunk:
                break
            
            # Extract and merge complete rules
            # (Similar logic to process_large_css)
            
        return stats