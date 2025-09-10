"""Enums for Table Grid Widget."""

import enum

from engineai.sdk.dashboard.enum.align import HorizontalAlignment

__all__ = ["HorizontalAlignment"]


class SummaryRowPosition(enum.Enum):
    """Enum with summary row position options.

    Options for positioning the summary row in table widgets.

    Attributes:
        TOP (str): Summary row is placed at the top.
        BOTTOM (str): Summary row is placed at the bottom.
    """

    TOP = "TOP"
    BOTTOM = "BOTTOM"


class SummaryOperation(enum.Enum):
    """Enum with summary operations.

    Available operations for calculating summary values in table widgets.

    Attributes:
        SUM (str): Sum operation.
        AVG (str): Average operation.
        MIN (str): Minimum operation.
        MAX (str): Maximum operation.
        COUNT (str): Count operation.
        COUNT_UNIQUE (str): Count unique operation.
    """

    SUM = "SUM"
    AVG = "AVG"
    MIN = "MIN"
    MAX = "MAX"
    COUNT = "COUNT"
    COUNT_UNIQUE = "COUNT_UNIQUE"
