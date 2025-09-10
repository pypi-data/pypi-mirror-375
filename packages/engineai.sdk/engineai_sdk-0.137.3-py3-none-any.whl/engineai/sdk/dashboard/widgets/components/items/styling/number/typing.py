"""Typings for Number Item Stylings."""

from .chip import NumberStylingChip
from .dot import NumberStylingDot
from .font import NumberStylingFont
from .progress_bar import NumberStylingProgressBar

NumberItemStyling = (
    NumberStylingFont | NumberStylingDot | NumberStylingChip | NumberStylingProgressBar
)
