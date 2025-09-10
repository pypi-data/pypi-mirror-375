"""Specs for chart toolbar."""

from typing import Any


def build_chart_toolbar(enable: bool) -> dict[str, Any]:
    """Build chart toolbar method."""
    return {"disabled": not enable}
