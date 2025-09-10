"""Typings for categorical series."""

from .area import AreaSeries
from .area_range import AreaRangeSeries
from .bubble import BubbleSeries
from .column import ColumnSeries
from .error_bar import ErrorBarSeries
from .line import LineSeries
from .point import PointSeries
from .scatter import ScatterSeries

CategoricalSeries = (
    LineSeries
    | AreaSeries
    | AreaRangeSeries
    | ColumnSeries
    | BubbleSeries
    | ScatterSeries
    | ErrorBarSeries
    | PointSeries
)
