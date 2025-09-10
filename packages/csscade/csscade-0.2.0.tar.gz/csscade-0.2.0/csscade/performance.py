"""Performance optimization utilities."""

from .cache.lru_cache import CSSCache
from .optimization.batch_processor import BatchProcessor
from .optimization.deduplicator import StyleRegistry

__all__ = ['CSSCache', 'StyleRegistry', 'BatchProcessor']