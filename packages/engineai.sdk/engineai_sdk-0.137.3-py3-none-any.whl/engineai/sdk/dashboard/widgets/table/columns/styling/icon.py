"""Specification for styling a column with an icon to a value."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from typing_extensions import override

from .base import TableColumnStylingBase

if TYPE_CHECKING:
    from engineai.sdk.dashboard.links import WidgetField


class IconStyling(TableColumnStylingBase):
    """Styling options for icon column.

    Specify the styling options for an icon column in the
    table widget, including data column and position.
    """

    def __init__(
        self,
        *,
        data_column: str | WidgetField | None,
        left: bool = True,
    ) -> None:
        """Constructor for IconStyling.

        Args:
            data_column: id of column which values are used to determine behavior of
                arrow.
                By default, will use values of column to which styling is applied.
            left: whether to put icon to the left (True) or right (False) of column
                value.
        """
        super().__init__(data_column=data_column, color_spec=None)
        self.__left = left

    @override
    def _build_extra_inputs(self) -> dict[str, Any]:
        return {"left": self.__left}
