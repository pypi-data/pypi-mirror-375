"""CSS handlers for advanced features."""

from .shorthand import ShorthandResolver
from .variables import VariablesHandler
from .selector_parser import SelectorParser
from .media import MediaQueryHandler
from .fallback import FallbackHandler
from .unicode_handler import UnicodeHandler
from .error_recovery import ErrorRecovery, PartialSuccess, create_fallback_css
from .large_file_handler import LargeFileHandler, StreamingMerger
from ..parser.value_parser import ValueParser

__all__ = [
    'ShorthandResolver',
    'ValueParser',
    'VariablesHandler',
    'SelectorParser',
    'MediaQueryHandler',
    'FallbackHandler',
    'UnicodeHandler',
    'ErrorRecovery',
    'PartialSuccess',
    'create_fallback_css',
    'LargeFileHandler',
    'StreamingMerger'
]