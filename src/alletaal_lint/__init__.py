"""
alletaal-lint: Dutch Text Readability Assessment Tool

Based on LiNT (Leesbaarheids­instrument voor Nederlandse Teksten)
"""

__version__ = "1.1.0"
__author__ = "City of Amsterdam"

from .core import Document, LintScorer, Sentence

__all__ = ["Document", "Sentence", "LintScorer"]
