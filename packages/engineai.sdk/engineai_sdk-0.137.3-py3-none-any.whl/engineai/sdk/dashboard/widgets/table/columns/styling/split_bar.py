"""Specification for styling a column with a split color bar."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from typing_extensions import override

from engineai.sdk.dashboard.styling import color
from engineai.sdk.dashboard.styling.color.spec import build_color_spec

from .base import TableColumnStylingBase
from .exceptions import TableColumnStylingMinMaxValueError

if TYPE_CHECKING:
    from engineai.sdk.dashboard.links import WidgetField
    from engineai.sdk.dashboard.styling.color.typing import ColorSpec


class SplitBarStyling(TableColumnStylingBase):
    """Styling options for split color bar column.

    Specify the styling options for a split color bar column in the
    table widget, including color, data column, min/max values,
    and percentage fill.
    """

    def __init__(
        self,
        *,
        data_column: str | WidgetField | None = None,
        color_spec: ColorSpec | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        percentage_fill: float = 0.9,
    ) -> None:
        """Constructor for SplitBarStyling.

        Args:
            data_column: id of column which values are used to determine behavior of
                arrow.
                By default, will use values of column to which styling is applied.
            color_spec: spec for color class.
            min_value: value that determines a 0% bar. By default, takes the minimum
                value in the data.
            max_value: value that determines a full bar. By default, takes the maximum
                value in the data.
            percentage_fill: how much of the cell should the color fill.
        """
        super().__init__(data_column=data_column, color_spec=None)
        if min_value and max_value and min_value >= max_value:
            raise TableColumnStylingMinMaxValueError(
                _class=self.__class__.__name__, min_value=min_value, max_value=max_value
            )
        self.__min_value = min_value
        self.__max_value = max_value
        self.__percentage_fill = percentage_fill
        self.__color_spec = color_spec

    @override
    def _build_extra_inputs(self) -> dict[str, Any]:
        return {
            "min": self.__min_value,
            "max": self.__max_value,
            "mid": 0,
            "percentageFill": self.__percentage_fill,
        }

    def _build_color_spec(self) -> dict[str, Any]:
        return {
            "colorSpec": build_color_spec(
                spec=self.__color_spec or color.PositiveNegativeDiscreteMap()
            )
        }
