"""Specification for styling a column with an arrow next to value."""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from typing import Any

from typing_extensions import override

from .base import TableColumnStylingBase

if TYPE_CHECKING:
    from engineai.sdk.dashboard.links import WidgetField
    from engineai.sdk.dashboard.styling.color.typing import ColorSpec


class RangeShape(enum.Enum):
    """Range shape options.

    Available shape options for range styling in table columns.

    Attributes:
        CIRCLE (str): Circle shape.
        RECTANGLE (str): Rectangle shape.
    """

    CIRCLE = "CIRCLE"
    RECTANGLE = "RECTANGLE"


class RangeStyling(TableColumnStylingBase):
    """Styling options for range column.

    Specify the styling options for a range column in the
    table widget, including color, data column, and shape.
    """

    def __init__(
        self,
        *,
        color_spec: ColorSpec,
        data_column: str | WidgetField | None = None,
        shape: RangeShape = RangeShape.CIRCLE,
    ) -> None:
        """Constructor for RangeStyling.

        Args:
            data_column: id of column which values are used to determine behavior of
                arrow.
            color_spec: spec for color of range value.
            shape: shape of range indicator.
        """
        super().__init__(
            data_column=data_column,
            color_spec=color_spec,
        )
        self.__shape = shape

    @override
    def _build_extra_inputs(self) -> dict[str, Any]:
        return {"shape": self.__shape.value}
