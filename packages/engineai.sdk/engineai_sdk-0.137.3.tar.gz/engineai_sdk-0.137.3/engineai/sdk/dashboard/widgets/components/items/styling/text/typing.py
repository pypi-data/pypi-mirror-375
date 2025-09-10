"""Typings for Text Item Stylings."""

from .chip import TextStylingChip
from .country_flag import TextStylingCountryFlag
from .dot import TextStylingDot
from .font import TextStylingFont

TextItemStyling = (
    TextStylingChip | TextStylingCountryFlag | TextStylingDot | TextStylingFont
)
