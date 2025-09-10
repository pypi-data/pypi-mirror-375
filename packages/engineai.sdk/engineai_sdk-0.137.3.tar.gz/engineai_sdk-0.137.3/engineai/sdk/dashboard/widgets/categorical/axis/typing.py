"""Specs for Axis typing."""

from collections.abc import Sequence

from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.widgets.categorical.series.typing import CategoricalSeries

ValueAxisSeries = (
    str
    | list[str]
    | WidgetField
    | list[WidgetField]
    | CategoricalSeries
    | Sequence[CategoricalSeries]
)
