"""Specifications for styling a column with an arrow next to value."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from engineai.sdk.dashboard.styling import color

from .base import TableColumnStylingBase

if TYPE_CHECKING:
    from engineai.sdk.dashboard.links import WidgetField
    from engineai.sdk.dashboard.styling.color.typing import ColorSpec


class ArrowStyling(TableColumnStylingBase):
    """Styling options for arrow column.

    Specify the styling options for an arrow column in the
    table widget, including data column, mid value, and color.
    """

    def __init__(
        self,
        *,
        data_column: str | WidgetField | None = None,
        mid: int | float = 0,
        color_spec: ColorSpec | None = None,
    ) -> None:
        """Constructor for ArrowStyling.

        Args:
            data_column: id of column which values are used to determine behavior of
                arrow. By default, will use values of column to which styling is
                applied.
            mid: value that determines when arrow flips up/down.
            color_spec: spec for color of arrows. By default, used the
                PositiveNegativeDiscreteMap.
        """
        super().__init__(
            color_spec=(
                color_spec if color_spec else color.PositiveNegativeDiscreteMap()
            ),
            data_column=data_column,
        )
        self.__mid = mid

    def _build_extra_inputs(self) -> dict[str, Any]:
        return {"mid": self.__mid}
