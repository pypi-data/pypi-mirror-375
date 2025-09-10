"""Spec to build different series supported by Map widget."""

from typing import Any

from .numeric import NumericSeries

MapSeries = NumericSeries


def build_map_series(series: MapSeries) -> dict[str, Any]:
    """Builds spec for dashboard API.

    Args:
        series: series spec

    Returns:
        Input object for Dashboard API
    """
    # if isinstance(series, NumericSeries):
    return {"numeric": series.build()}
