"""Optimization module for CSS operations."""

from .deduplicator import StyleRegistry, PropertyOptimizer
from .batch_processor import BatchProcessor

__all__ = ['StyleRegistry', 'PropertyOptimizer', 'BatchProcessor']