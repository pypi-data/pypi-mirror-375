"""Integration module for CSSCade."""

from .helpers import (
    StateManager, FrameworkAdapter, APIWrapper,
    quick_merge, merge_files
)

__all__ = [
    'StateManager', 'FrameworkAdapter', 'APIWrapper',
    'quick_merge', 'merge_files'
]