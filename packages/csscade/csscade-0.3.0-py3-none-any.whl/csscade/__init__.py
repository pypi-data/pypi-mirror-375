"""
CSSCade: Intelligent CSS Merging and Override System for Python

A sophisticated CSS manipulation library for server-side rendered applications
that provides intelligent property-level merging with conflict resolution.
"""

__version__ = "0.3.0"

from csscade.merger import CSSMerger, BatchMerger
from csscade.property_merger import PropertyMerger
from csscade.models import CSSProperty, CSSRule
from csscade.strategies.permanent import PermanentMergeStrategy
from csscade.strategies.component import ComponentMergeStrategy
from csscade.strategies.replace import ReplaceMergeStrategy
from csscade.combinator import Combinator

__all__ = [
    "CSSMerger",
    "PropertyMerger",
    "BatchMerger",
    "CSSProperty",
    "CSSRule",
    "PermanentMergeStrategy",
    "ComponentMergeStrategy",
    "ReplaceMergeStrategy",
    "Combinator",
]