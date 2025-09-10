"""Specification for styling the stacked bar column."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from typing_extensions import override

from engineai.sdk.dashboard.styling.color.spec import build_color_spec

from .base import TableSparklineColumnStylingBase

if TYPE_CHECKING:
    from engineai.sdk.dashboard.links import WidgetField
    from engineai.sdk.dashboard.styling.color import DiscreteMap


class StackedBarStyling(TableSparklineColumnStylingBase):
    """Styling options for stacked bar column.

    Specify the styling options for a stacked bar column in
    the table widget, including color, data column, and total display.
    """

    def __init__(
        self,
        *,
        color_spec: DiscreteMap,
        data_column: str | WidgetField | None = None,
    ) -> None:
        """Constructor for StackedBarStyling.

        Args:
            data_column: id of column which values are used for chart.
            color_spec: spec for discrete color map of stacked bar column chart.
        """
        super().__init__(
            data_column=data_column,
            color_spec=color_spec,
        )

    @override
    def _build_color_spec(self) -> dict[str, Any]:
        return (
            {
                "colorSpec": build_color_spec(spec=self.color_spec),
            }
            if self.color_spec is not None
            else {}
        )
