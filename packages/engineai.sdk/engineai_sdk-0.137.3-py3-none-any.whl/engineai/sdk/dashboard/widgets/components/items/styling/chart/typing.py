"""Typings for Chart Item Stylings."""

from .area import AreaChartItemStyling
from .column import ColumnChartItemStyling
from .line import LineChartItemStyling
from .stacked_bar import StackedBarChartItemStyling

ChartItemStyling = (
    AreaChartItemStyling
    | ColumnChartItemStyling
    | LineChartItemStyling
    | StackedBarChartItemStyling
)
