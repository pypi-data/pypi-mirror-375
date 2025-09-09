"""Tukuy - A flexible data transformation library with a plugin system."""

from .transformers import TukuyTransformer
from .base import BaseTransformer, ChainableTransformer
from .plugins.base import TransformerPlugin, PluginRegistry
from .exceptions import ValidationError, TransformationError
from .types import TransformContext, TransformResult

__version__ = '0.2.0'

__all__ = [
    'TukuyTransformer',
    'BaseTransformer',
    'ChainableTransformer',
    'TransformerPlugin',
    'PluginRegistry',
    'ValidationError',
    'TransformationError',
    'TransformContext',
    'TransformResult',
]
