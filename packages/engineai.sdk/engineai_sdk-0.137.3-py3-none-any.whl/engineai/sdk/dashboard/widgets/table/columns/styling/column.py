"""Specification for styling a column chart."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import TableSparklineColumnStylingBase

if TYPE_CHECKING:
    from engineai.sdk.dashboard.links import WidgetField
    from engineai.sdk.dashboard.styling.color.typing import ColorSpec


class ColumnChartStyling(TableSparklineColumnStylingBase):
    """Styling options for column chart column.

    Specify the styling options for a column chart column in
    the table widget, including color and data key.
    """

    def __init__(
        self,
        *,
        color_spec: ColorSpec,
        data_key: str | WidgetField | None = None,
    ) -> None:
        """Constructor for ColumnChartStyling.

        Args:
            data_key: Dictionary key, stored in data, that is used for chart.
                By default, will use values of column to which styling is applied.
            color_spec: spec for color of column chart.
        """
        super().__init__(
            data_column=data_key,
            color_spec=color_spec,
        )
