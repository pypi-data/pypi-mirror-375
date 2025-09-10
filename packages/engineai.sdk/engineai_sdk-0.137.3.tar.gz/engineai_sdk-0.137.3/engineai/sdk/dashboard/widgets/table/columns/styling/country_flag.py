"""Specification for styling a column with a country flag to a value."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from typing_extensions import override

from .base import TableColumnStylingBase

if TYPE_CHECKING:
    from engineai.sdk.dashboard.links import WidgetField


class CountryFlagStyling(TableColumnStylingBase):
    """Styling options for country flag column.

    Specify the styling options for a country flag column
    in the table widget, including position and data column.
    """

    def __init__(
        self,
        *,
        left: bool = True,
        data_column: str | WidgetField | None = None,
    ) -> None:
        """Constructor for CountryFlagStyling.

        Args:
            data_column: id of column which values are used to determine behavior of
                arrow.
                By default, will use values of column to which styling is applied.
            left: whether to put flag to the left (True) or right (False) of column
                value.
        """
        super().__init__(data_column=data_column, color_spec=None)
        self.__left = left

    @override
    def _build_extra_inputs(self) -> dict[str, Any]:
        return {"left": self.__left}
