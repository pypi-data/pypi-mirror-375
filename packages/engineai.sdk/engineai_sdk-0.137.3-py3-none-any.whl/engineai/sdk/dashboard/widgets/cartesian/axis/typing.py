"""Specs for Axis typing."""

from engineai.sdk.dashboard.links.widget_field import WidgetField
from engineai.sdk.dashboard.widgets.cartesian.series.typing import CartesianSeries

YAxisSeries = (
    str
    | list[str]
    | WidgetField
    | list[WidgetField]
    | CartesianSeries
    | list[CartesianSeries]
)
