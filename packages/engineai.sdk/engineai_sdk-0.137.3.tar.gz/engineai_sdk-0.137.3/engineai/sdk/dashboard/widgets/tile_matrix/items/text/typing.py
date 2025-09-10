"""Typing for text tile matrix items."""

from engineai.sdk.dashboard.widgets.components.items.styling import TextStylingDot
from engineai.sdk.dashboard.widgets.components.items.styling import TextStylingFont

from .styling.background import TextStylingBackground

TileMatrixTextItemStyling = TextStylingDot | TextStylingFont | TextStylingBackground
