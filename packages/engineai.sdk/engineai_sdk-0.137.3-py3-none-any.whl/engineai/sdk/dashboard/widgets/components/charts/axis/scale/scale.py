"""Spec to build different scales supported by y axis."""

from typing import Any

from .dynamic import AxisScaleDynamic
from .positive import AxisScalePositive
from .symmetric import AxisScaleSymmetric
from .typing import AxisScale


def build_axis_scale(scale: AxisScale) -> dict[str, Any]:
    """Builds spec for dashboard API.

    Returns:
        Input object for Dashboard API
    """
    return {_get_input_key(scale): scale.build()}


def _get_input_key(scale: AxisScale) -> str:
    if isinstance(scale, AxisScaleDynamic):
        return "dynamic"
    if isinstance(scale, AxisScaleSymmetric):
        return "symmetrical"
    if isinstance(scale, AxisScalePositive):
        return "positive"
    # isinstance(scale, AxisScaleNegative):
    return "negative"
