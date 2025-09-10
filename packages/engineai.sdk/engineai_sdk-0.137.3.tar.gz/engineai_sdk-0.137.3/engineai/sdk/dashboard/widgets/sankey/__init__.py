"""Specs for Sankey widgets."""

from engineai.sdk.dashboard.widgets.components.charts.tooltip import CategoryTooltipItem
from engineai.sdk.dashboard.widgets.components.charts.tooltip import DatetimeTooltipItem
from engineai.sdk.dashboard.widgets.components.charts.tooltip import NumberTooltipItem
from engineai.sdk.dashboard.widgets.components.charts.tooltip import TextTooltipItem

from .sankey import Connections
from .sankey import Nodes
from .sankey import Sankey
from .series.styling import ConnectionsStyling
from .series.styling import NodesStyling

__all__ = [
    # .tooltip
    "CategoryTooltipItem",
    # .connections
    "Connections",
    "ConnectionsStyling",
    "DatetimeTooltipItem",
    # .nodes
    "Nodes",
    "NodesStyling",
    "NumberTooltipItem",
    # .sankey,
    "Sankey",
    "TextTooltipItem",
]
