"""Formatting typing."""

from .datetime import DateTimeFormatting
from .mapper import MapperFormatting
from .number import NumberFormatting
from .text import TextFormatting

FormattingType = (
    DateTimeFormatting | MapperFormatting | NumberFormatting | TextFormatting
)

__all__ = ["FormattingType"]
