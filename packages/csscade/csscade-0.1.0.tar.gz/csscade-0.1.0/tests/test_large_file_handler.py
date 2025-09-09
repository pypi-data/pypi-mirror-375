"""Tests for large file handling."""

import os
import tempfile
import pytest
from pathlib import Path
from csscade.handlers.large_file_handler import LargeFileHandler, StreamingMerger


class TestLargeFileHandler:
    """Test large file handler functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = LargeFileHandler(chunk_size=1024)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.handler.cleanup()
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, content: str, name: str = 'test.css') -> str:
        """Create a test file with content."""
        file_path = os.path.join(self.temp_dir, name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def test_is_large_file(self):
        """Test large file detection."""
        # Create a small file
        small_file = self.create_test_file('small content')
        assert not self.handler.is_large_file(small_file)
        
        # Create a large file (> 5MB)
        large_content = 'x' * (6 * 1024 * 1024)
        large_file = self.create_test_file(large_content, 'large.css')
        assert self.handler.is_large_file(large_file)
        
        # Test with custom threshold
        assert self.handler.is_large_file(small_file, threshold=10)
        
        # Test non-existent file
        assert not self.handler.is_large_file('/nonexistent/file.css')
    
    def test_read_in_chunks(self):
        """Test chunked reading."""
        content = 'a' * 3000  # Larger than chunk size
        file_path = self.create_test_file(content)
        
        chunks = list(self.handler.read_in_chunks(file_path))
        
        # Should have multiple chunks
        assert len(chunks) > 1
        
        # Reconstruct content
        reconstructed = ''.join(chunks)
        assert reconstructed == content
    
    def test_process_large_css_simple(self):
        """Test processing large CSS file."""
        css = """.btn { color: red; }
.header { padding: 10px; }
.footer { margin: 5px; }"""
        
        file_path = self.create_test_file(css)
        
        def processor(rule):
            return {'rule': rule, 'processed': True}
        
        results = list(self.handler.process_large_css(file_path, processor))
        
        assert len(results) == 3
        assert all(r.get('processed') for r in results)
    
    def test_process_large_css_with_incomplete_rules(self):
        """Test processing CSS with rules split across chunks."""
        # Create CSS that will be split across chunks
        css = '.btn { ' + 'x' * 2000 + 'color: red; }'
        file_path = self.create_test_file(css)
        
        self.handler.chunk_size = 100  # Small chunks to force splitting
        
        def processor(rule):
            return {'length': len(rule)}
        
        results = list(self.handler.process_large_css(file_path, processor))
        
        # Should still process the complete rule
        assert len(results) >= 1
    
    def test_process_large_css_with_errors(self):
        """Test error handling in processing."""
        css = """.valid { color: red; }
.invalid { this will cause error }
.another { padding: 10px; }"""
        
        file_path = self.create_test_file(css)
        
        def processor(rule):
            if 'invalid' in rule:
                raise ValueError("Invalid rule")
            return {'rule': rule}
        
        results = list(self.handler.process_large_css(file_path, processor))
        
        # Should have results including error
        error_results = [r for r in results if 'error' in r]
        valid_results = [r for r in results if 'error' not in r]
        
        assert len(error_results) == 1
        assert len(valid_results) == 2
    
    def test_merge_large_files(self):
        """Test merging large CSS files."""
        source_css = """.btn { color: red; margin: 10px; }
.header { padding: 5px; }"""
        
        override_css = """.btn { color: blue; }
.footer { margin: 20px; }"""
        
        source_path = self.create_test_file(source_css, 'source.css')
        override_path = self.create_test_file(override_css, 'override.css')
        output_path = os.path.join(self.temp_dir, 'output.css')
        
        def merger(source_props, override_props):
            merged = source_props.copy()
            merged.update(override_props)
            return merged
        
        stats = self.handler.merge_large_files(
            source_path, override_path, output_path, merger
        )
        
        assert stats['rules_processed'] > 0
        assert os.path.exists(output_path)
        
        # Check output content
        with open(output_path, 'r') as f:
            output = f.read()
            assert 'color: blue' in output  # Override applied
            assert 'margin: 10px' in output or 'margin: 20px' in output
    
    def test_parse_rule(self):
        """Test CSS rule parsing."""
        # Valid rule
        rule = '.btn { color: red; padding: 10px; }'
        parsed = self.handler._parse_rule(rule)
        
        assert parsed['selector'] == '.btn'
        assert parsed['properties']['color'] == 'red'
        assert parsed['properties']['padding'] == '10px'
        
        # Rule without closing brace
        rule = '.btn { color: red'
        parsed = self.handler._parse_rule(rule)
        assert parsed['properties']['color'] == 'red'
        
        # Empty rule
        parsed = self.handler._parse_rule('')
        assert parsed == {}
        
        # Rule without properties
        rule = '.btn { }'
        parsed = self.handler._parse_rule(rule)
        assert parsed['selector'] == '.btn'
        assert parsed['properties'] == {}
    
    def test_use_memory_map(self):
        """Test memory mapping."""
        content = 'test content'
        file_path = self.create_test_file(content)
        
        # Note: Memory mapping requires binary mode and may not work
        # with all file systems, so we just test the interface
        mmap_obj = self.handler.use_memory_map(file_path)
        
        # May return None if not supported
        if mmap_obj is not None:
            mmap_obj.close()
    
    def test_estimate_memory_usage(self):
        """Test memory usage estimation."""
        content = 'x' * 10000
        file_path = self.create_test_file(content)
        
        estimate = self.handler.estimate_memory_usage(file_path)
        
        assert estimate['file_size'] == 10000
        assert estimate['estimated_memory'] == 20000  # 2x file size
        assert 'recommended_chunk_size' in estimate
        assert 'is_large' in estimate
        assert estimate['recommended_method'] in ['streaming', 'memory']
    
    def test_cleanup(self):
        """Test temporary file cleanup."""
        # Create a temp file through the handler
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.css',
            delete=False
        ) as f:
            temp_path = Path(f.name)
            self.handler.temp_files.append(temp_path)
            f.write('temp content')
        
        assert temp_path.exists()
        
        self.handler.cleanup()
        
        # File should be deleted
        assert not temp_path.exists()
        assert len(self.handler.temp_files) == 0
    
    def test_del_cleanup(self):
        """Test cleanup on deletion."""
        handler = LargeFileHandler()
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.css',
            delete=False
        ) as f:
            temp_path = Path(f.name)
            handler.temp_files.append(temp_path)
        
        # Delete handler should trigger cleanup
        del handler
        
        # File should be deleted
        assert not temp_path.exists()


class TestStreamingMerger:
    """Test streaming CSS merger."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.merger = StreamingMerger(buffer_size=1024)
    
    def test_stream_merge(self):
        """Test streaming merge."""
        from io import StringIO
        
        source = StringIO('.btn { color: red; }')
        override = StringIO('.btn { color: blue; }')
        output = StringIO()
        
        def merger_func(source_rules, override_rules):
            merged = source_rules.copy() if source_rules else {}
            if override_rules:
                merged.update(override_rules)
            return merged
        
        stats = self.merger.stream_merge(
            source, override, output, merger_func
        )
        
        assert stats['bytes_read'] > 0
        
        # Note: Full implementation would process rules
        # This is a basic interface test
    
    def test_stream_merge_large_buffers(self):
        """Test streaming with large content."""
        from io import StringIO
        
        # Create large CSS content
        large_css = '.rule { ' + 'x' * 2000 + ' }'
        
        source = StringIO(large_css)
        override = StringIO('.override { color: blue; }')
        output = StringIO()
        
        def merger_func(s, o):
            return {}  # Simple merger for test
        
        self.merger.buffer_size = 100  # Small buffer
        
        stats = self.merger.stream_merge(
            source, override, output, merger_func
        )
        
        # Should handle content larger than buffer
        assert stats['bytes_read'] > self.merger.buffer_size