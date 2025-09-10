"""Specs for Cartesian widget."""

from engineai.sdk.dashboard.widgets.components.charts.axis.scale import AxisScaleDynamic
from engineai.sdk.dashboard.widgets.components.charts.axis.scale import (
    AxisScaleNegative,
)
from engineai.sdk.dashboard.widgets.components.charts.axis.scale import (
    AxisScalePositive,
)
from engineai.sdk.dashboard.widgets.components.charts.axis.scale import (
    AxisScaleSymmetric,
)
from engineai.sdk.dashboard.widgets.components.charts.series.entities.country import (
    CountryEntity,
)
from engineai.sdk.dashboard.widgets.components.charts.series.entities.custom import (
    CustomEntity,
)
from engineai.sdk.dashboard.widgets.components.charts.styling.enums import DashStyle
from engineai.sdk.dashboard.widgets.components.charts.styling.enums import MarkerSymbol
from engineai.sdk.dashboard.widgets.components.charts.tooltip import CategoryTooltipItem
from engineai.sdk.dashboard.widgets.components.charts.tooltip import DatetimeTooltipItem
from engineai.sdk.dashboard.widgets.components.charts.tooltip import NumberTooltipItem
from engineai.sdk.dashboard.widgets.components.charts.tooltip import TextTooltipItem

from .axis.x_axis import XAxis
from .axis.y_axis import YAxis
from .cartesian import Cartesian
from .chart import Chart
from .legend import LegendPosition
from .series.area import AreaSeries
from .series.area import AreaSeriesStyling
from .series.area_range import AreaRangeSeries
from .series.area_range import AreaRangeSeriesStyling
from .series.bubble import BubbleCircleSeriesStyling
from .series.bubble import BubbleCountrySeriesStyling
from .series.bubble import BubbleSeries
from .series.column import ColumnSeries
from .series.column import ColumnSeriesStyling
from .series.line import LineSeries
from .series.line import LineSeriesStyling
from .series.scatter import ScatterSeries
from .series.scatter import ScatterSeriesStyling

__all__ = [
    "AreaRangeSeries",
    "AreaRangeSeriesStyling",
    "AreaSeries",
    "AreaSeriesStyling",
    # .scales
    "AxisScaleDynamic",
    "AxisScaleNegative",
    "AxisScalePositive",
    "AxisScaleSymmetric",
    "BubbleCircleSeriesStyling",
    "BubbleCountrySeriesStyling",
    "BubbleSeries",
    # .cartesian
    "Cartesian",
    # .tooltip
    "CategoryTooltipItem",
    # .chart
    "Chart",
    "ColumnSeries",
    "ColumnSeriesStyling",
    # .entities
    "CountryEntity",
    "CustomEntity",
    # ..charts
    "DashStyle",
    "DatetimeTooltipItem",
    # .legend
    "LegendPosition",
    # .series
    "LineSeries",
    "LineSeriesStyling",
    "MarkerSymbol",
    "NumberTooltipItem",
    "ScatterSeries",
    "ScatterSeriesStyling",
    "TextTooltipItem",
    # .axis
    "XAxis",
    "YAxis",
]
