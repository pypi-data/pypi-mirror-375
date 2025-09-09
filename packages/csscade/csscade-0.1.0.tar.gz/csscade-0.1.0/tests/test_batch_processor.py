"""Tests for batch processing optimization."""

import pytest
import time
from csscade.optimization.batch_processor import (
    BatchProcessor, StreamProcessor, LazyLoader
)


class TestBatchProcessor:
    """Test cases for batch processor."""
    
    def test_sequential_processing(self):
        """Test sequential batch processing."""
        processor = BatchProcessor()
        
        # Simple processing function
        def process_op(op_type, source, override):
            return {'type': op_type, 'result': f'{source}+{override}'}
        
        operations = [
            ('merge', 'a', 'b'),
            ('merge', 'c', 'd'),
            ('merge', 'e', 'f')
        ]
        
        results = processor.process_batch(operations, process_op, parallel=False)
        
        assert len(results) == 3
        assert results[0] == {'type': 'merge', 'result': 'a+b'}
        assert results[1] == {'type': 'merge', 'result': 'c+d'}
        assert results[2] == {'type': 'merge', 'result': 'e+f'}
    
    def test_parallel_processing(self):
        """Test parallel batch processing."""
        processor = BatchProcessor(max_workers=2)
        
        # Processing function with delay
        def process_op(op_type, source, override):
            time.sleep(0.01)  # Small delay
            return {'type': op_type, 'result': f'{source}+{override}'}
        
        operations = [
            ('merge', f'a{i}', f'b{i}')
            for i in range(5)
        ]
        
        # Parallel should be faster than sequential for multiple operations
        start = time.time()
        results = processor.process_batch(operations, process_op, parallel=True)
        parallel_time = time.time() - start
        
        assert len(results) == 5
        # Results should be in order despite parallel processing
        for i in range(5):
            assert results[i] == {'type': 'merge', 'result': f'a{i}+b{i}'}
    
    def test_error_handling(self):
        """Test error handling in batch processing."""
        processor = BatchProcessor()
        
        def process_op(op_type, source, override):
            if source == 'error':
                raise ValueError('Test error')
            return {'result': 'ok'}
        
        operations = [
            ('merge', 'good', 'data'),
            ('merge', 'error', 'data'),
            ('merge', 'good', 'data')
        ]
        
        results = processor.process_batch(operations, process_op, parallel=False)
        
        assert results[0] == {'result': 'ok'}
        assert 'error' in results[1]
        assert results[2] == {'result': 'ok'}
    
    def test_optimize_operations(self):
        """Test operation optimization."""
        processor = BatchProcessor()
        
        operations = [
            ('type_b', 'data1', 'data2'),
            ('type_a', 'data3', 'data4'),
            ('type_b', 'data5', 'data6'),
            ('type_a', 'data7', 'data8')
        ]
        
        optimized = processor.optimize_operations(operations)
        
        # Should group by type
        assert optimized[0][0] == 'type_a'
        assert optimized[1][0] == 'type_a'
        assert optimized[2][0] == 'type_b'
        assert optimized[3][0] == 'type_b'
    
    def test_chunk_operations(self):
        """Test operation chunking."""
        processor = BatchProcessor()
        
        # Test auto chunk size
        operations = list(range(25))
        chunks = processor.chunk_operations(operations)
        
        assert len(chunks) > 1  # Should be split into chunks
        assert sum(len(chunk) for chunk in chunks) == 25
        
        # Test specified chunk size
        chunks = processor.chunk_operations(operations, chunk_size=5)
        assert len(chunks) == 5
        assert all(len(chunk) == 5 for chunk in chunks)
    
    def test_statistics(self):
        """Test batch processing statistics."""
        processor = BatchProcessor()
        
        def simple_op(op_type, a, b):
            return f'{a}{b}'
        
        operations = [('op', 'a', 'b')] * 3
        processor.process_batch(operations, simple_op)
        
        stats = processor.get_stats()
        assert stats['total_batches'] == 1
        assert stats['total_operations'] == 3
        assert stats['total_time'] > 0
        
        # Process another batch
        processor.process_batch(operations, simple_op)
        
        stats = processor.get_stats()
        assert stats['total_batches'] == 2
        assert stats['total_operations'] == 6


class TestStreamProcessor:
    """Test cases for stream processor."""
    
    def test_stream_processing(self):
        """Test stream-based processing."""
        stream = StreamProcessor(buffer_size=3)
        
        def process_op(op_type, value):
            return f'processed_{value}'
        
        stream.set_processor(process_op)
        
        # Add operations
        stream.add('op', 'val1')
        stream.add('op', 'val2')
        
        # Buffer not full yet
        assert len(stream.results) == 0
        
        # This should trigger flush
        stream.add('op', 'val3')
        
        # Buffer should have been processed
        assert len(stream.buffer) == 0
        
        # Add more and get all results
        stream.add('op', 'val4')
        all_results = stream.get_results()
        
        assert len(all_results) == 4
        assert all_results[0] == 'processed_val1'
    
    def test_manual_flush(self):
        """Test manual buffer flush."""
        stream = StreamProcessor(buffer_size=10)
        
        def process_op(op_type, value):
            return value * 2
        
        stream.set_processor(process_op)
        
        stream.add('op', 5)
        stream.add('op', 10)
        
        # Manually flush
        results = stream.flush()
        
        assert results == [10, 20]
        assert len(stream.buffer) == 0
    
    def test_clear_stream(self):
        """Test clearing stream."""
        stream = StreamProcessor()
        
        stream.add('op', 'data')
        stream.results = ['result1', 'result2']
        
        stream.clear()
        
        assert len(stream.buffer) == 0
        assert len(stream.results) == 0


class TestLazyLoader:
    """Test cases for lazy loader."""
    
    def test_load_css_chunks(self):
        """Test loading CSS in chunks."""
        loader = LazyLoader(chunk_size=2)
        
        css_content = """
        .class1 { color: red; }
        .class2 { color: blue; }
        .class3 { color: green; }
        .class4 { color: yellow; }
        .class5 { color: purple; }
        """
        
        loader.load_css(css_content)
        
        # Should be split into chunks
        assert len(loader.chunks) > 1
    
    def test_get_chunk(self):
        """Test getting specific chunks."""
        loader = LazyLoader(chunk_size=2)
        
        css_content = ".a{color:red}.b{color:blue}.c{color:green}"
        loader.load_css(css_content)
        
        chunk0 = loader.get_chunk(0)
        assert chunk0 is not None
        
        # Out of range
        assert loader.get_chunk(100) is None
    
    def test_iterate_chunks(self):
        """Test iterating over chunks."""
        loader = LazyLoader(chunk_size=1)
        
        css_content = ".a{}.b{}.c{}"
        loader.load_css(css_content)
        
        chunks = list(loader.iterate_chunks())
        assert len(chunks) == len(loader.chunks)
    
    def test_process_chunk_with_cache(self):
        """Test processing chunks with caching."""
        loader = LazyLoader()
        
        css_content = ".test { color: red; }"
        loader.load_css(css_content)
        
        process_count = 0
        
        def processor(chunk):
            nonlocal process_count
            process_count += 1
            return f'processed_{chunk}'
        
        # First call should process
        result1 = loader.process_chunk(0, processor)
        assert process_count == 1
        
        # Second call should use cache
        result2 = loader.process_chunk(0, processor)
        assert process_count == 1  # Not incremented
        assert result1 == result2
    
    def test_clear_cache(self):
        """Test clearing chunk cache."""
        loader = LazyLoader()
        
        loader.loaded_chunks = {0: 'cached_data'}
        loader.clear_cache()
        
        assert len(loader.loaded_chunks) == 0