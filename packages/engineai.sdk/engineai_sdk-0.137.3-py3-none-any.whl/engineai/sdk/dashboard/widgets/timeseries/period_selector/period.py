"""Spec to build different periods supported by period selector."""

from typing import Any

from .custom_period import CustomPeriod
from .standard import Period

PeriodType = Period | CustomPeriod


def build_timeseries_period(period: PeriodType) -> dict[str, Any]:
    """Builds spec for dashboard API.

    Returns:
        Input object for Dashboard API
    """
    return _get_input(period)


def _get_input(period: PeriodType) -> dict[str, Any]:
    if isinstance(period, Period):
        return {"standard": {"period": period.value}}
    # if isinstance(period, CustomPeriod):
    return {"custom": period.build()}
