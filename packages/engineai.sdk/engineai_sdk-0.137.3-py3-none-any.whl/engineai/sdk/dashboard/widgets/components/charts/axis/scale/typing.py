"""Specs for Scale in Chart Axis ."""

from .dynamic import AxisScaleDynamic
from .negative import AxisScaleNegative
from .positive import AxisScalePositive
from .symmetric import AxisScaleSymmetric

AxisScale = (
    AxisScaleDynamic | AxisScaleSymmetric | AxisScalePositive | AxisScaleNegative
)
