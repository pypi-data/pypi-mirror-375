"""Batch processing optimization for CSS operations."""

from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


class BatchProcessor:
    """Optimize batch CSS operations."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize batch processor.
        
        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = max_workers
        self.stats = {
            'total_batches': 0,
            'total_operations': 0,
            'total_time': 0.0,
            'avg_batch_time': 0.0
        }
    
    def process_batch(
        self,
        operations: List[Tuple[str, Any, Any]],
        processor_func: callable,
        parallel: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of operations.
        
        Args:
            operations: List of (operation_type, source, override) tuples
            processor_func: Function to process each operation
            parallel: Whether to process in parallel
            
        Returns:
            List of results
        """
        start_time = time.time()
        results = []
        
        if parallel and len(operations) > 1:
            # Process in parallel for multiple operations
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                futures = {
                    executor.submit(processor_func, *op): i
                    for i, op in enumerate(operations)
                }
                
                # Collect results in order
                results = [None] * len(operations)
                for future in as_completed(futures):
                    index = futures[future]
                    try:
                        results[index] = future.result()
                    except Exception as e:
                        results[index] = {'error': str(e)}
        else:
            # Process sequentially
            for op in operations:
                try:
                    result = processor_func(*op)
                    results.append(result)
                except Exception as e:
                    results.append({'error': str(e)})
        
        # Update statistics
        elapsed = time.time() - start_time
        self.stats['total_batches'] += 1
        self.stats['total_operations'] += len(operations)
        self.stats['total_time'] += elapsed
        self.stats['avg_batch_time'] = self.stats['total_time'] / self.stats['total_batches']
        
        return results
    
    def optimize_operations(
        self,
        operations: List[Tuple[str, Any, Any]]
    ) -> List[Tuple[str, Any, Any]]:
        """
        Optimize operations before processing.
        
        Args:
            operations: List of operations
            
        Returns:
            Optimized list of operations
        """
        # Group similar operations for better cache locality
        grouped = {}
        for op in operations:
            op_type = op[0]
            if op_type not in grouped:
                grouped[op_type] = []
            grouped[op_type].append(op)
        
        # Flatten back to list with grouped operations
        optimized = []
        for op_type in sorted(grouped.keys()):
            optimized.extend(grouped[op_type])
        
        return optimized
    
    def chunk_operations(
        self,
        operations: List[Any],
        chunk_size: Optional[int] = None
    ) -> List[List[Any]]:
        """
        Split operations into chunks for processing.
        
        Args:
            operations: List of operations
            chunk_size: Size of each chunk (auto if None)
            
        Returns:
            List of operation chunks
        """
        if chunk_size is None:
            # Auto-determine chunk size based on operation count
            if len(operations) <= 10:
                chunk_size = len(operations)
            elif len(operations) <= 100:
                chunk_size = 10
            else:
                chunk_size = max(20, len(operations) // self.max_workers)
        
        chunks = []
        for i in range(0, len(operations), chunk_size):
            chunks.append(operations[i:i + chunk_size])
        
        return chunks
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get batch processing statistics.
        
        Returns:
            Statistics dictionary
        """
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Reset statistics."""
        self.stats = {
            'total_batches': 0,
            'total_operations': 0,
            'total_time': 0.0,
            'avg_batch_time': 0.0
        }


class StreamProcessor:
    """Process CSS operations in a streaming fashion."""
    
    def __init__(self, buffer_size: int = 100):
        """
        Initialize stream processor.
        
        Args:
            buffer_size: Size of the processing buffer
        """
        self.buffer_size = buffer_size
        self.buffer: List[Tuple[Any, ...]] = []
        self.results: List[Any] = []
        self.processor: Optional[callable] = None
    
    def set_processor(self, processor_func: callable) -> None:
        """
        Set the processing function.
        
        Args:
            processor_func: Function to process operations
        """
        self.processor = processor_func
    
    def add(self, *operation: Any) -> None:
        """
        Add operation to the stream.
        
        Args:
            *operation: Operation arguments
        """
        self.buffer.append(operation)
        
        # Process if buffer is full
        if len(self.buffer) >= self.buffer_size:
            self.flush()
    
    def flush(self) -> List[Any]:
        """
        Process all buffered operations.
        
        Returns:
            List of results
        """
        if not self.buffer or not self.processor:
            return []
        
        # Process buffer
        batch_processor = BatchProcessor()
        results = batch_processor.process_batch(
            self.buffer,
            self.processor,
            parallel=len(self.buffer) > 10
        )
        
        self.results.extend(results)
        self.buffer.clear()
        
        return results
    
    def get_results(self) -> List[Any]:
        """
        Get all processed results.
        
        Returns:
            List of all results
        """
        # Flush any remaining operations
        self.flush()
        return self.results
    
    def clear(self) -> None:
        """Clear buffer and results."""
        self.buffer.clear()
        self.results.clear()


class LazyLoader:
    """Lazy loading for large CSS files."""
    
    def __init__(self, chunk_size: int = 1000):
        """
        Initialize lazy loader.
        
        Args:
            chunk_size: Number of rules per chunk
        """
        self.chunk_size = chunk_size
        self.chunks: List[str] = []
        self.loaded_chunks: Dict[int, Any] = {}
    
    def load_css(self, css_content: str) -> None:
        """
        Load CSS content for lazy processing.
        
        Args:
            css_content: Full CSS content
        """
        # Split CSS into chunks by rules
        rules = css_content.split('}')
        
        self.chunks = []
        for i in range(0, len(rules), self.chunk_size):
            chunk_rules = rules[i:i + self.chunk_size]
            if chunk_rules[-1].strip():  # Add closing brace if not empty
                chunk_rules[-1] += '}'
            chunk = '}'.join(chunk_rules)
            self.chunks.append(chunk)
    
    def get_chunk(self, index: int) -> Optional[str]:
        """
        Get a specific chunk.
        
        Args:
            index: Chunk index
            
        Returns:
            CSS chunk or None
        """
        if 0 <= index < len(self.chunks):
            return self.chunks[index]
        return None
    
    def iterate_chunks(self):
        """
        Iterate over chunks lazily.
        
        Yields:
            CSS chunks
        """
        for chunk in self.chunks:
            yield chunk
    
    def process_chunk(
        self,
        index: int,
        processor_func: callable
    ) -> Any:
        """
        Process a specific chunk.
        
        Args:
            index: Chunk index
            processor_func: Function to process chunk
            
        Returns:
            Processed result
        """
        # Check cache
        if index in self.loaded_chunks:
            return self.loaded_chunks[index]
        
        # Load and process chunk
        chunk = self.get_chunk(index)
        if chunk:
            result = processor_func(chunk)
            self.loaded_chunks[index] = result
            return result
        
        return None
    
    def clear_cache(self) -> None:
        """Clear loaded chunks cache."""
        self.loaded_chunks.clear()