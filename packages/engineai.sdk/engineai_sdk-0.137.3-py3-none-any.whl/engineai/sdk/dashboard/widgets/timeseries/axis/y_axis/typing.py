"""Specs for YAxis typing."""

from engineai.sdk.dashboard.widgets.timeseries.axis.y_axis.y_axis import YAxis
from engineai.sdk.dashboard.widgets.timeseries.axis.y_axis.y_axis_mirror import (
    MirrorYAxis,
)

YAxisSpec = YAxis | MirrorYAxis
