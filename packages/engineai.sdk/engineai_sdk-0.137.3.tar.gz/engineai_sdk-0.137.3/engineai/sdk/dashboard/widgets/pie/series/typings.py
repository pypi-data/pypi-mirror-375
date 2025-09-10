"""Pie Widget Series typings."""

from .country import CountrySeries
from .series import Series

ChartSeries = Series | CountrySeries
