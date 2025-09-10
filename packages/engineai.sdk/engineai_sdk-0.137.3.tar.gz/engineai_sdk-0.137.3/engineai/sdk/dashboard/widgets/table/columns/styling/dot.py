"""Specification for styling a column with an arrow next to value."""

from __future__ import annotations

from typing import TYPE_CHECKING

from engineai.sdk.dashboard.styling import color

from .base import TableColumnStylingBase

if TYPE_CHECKING:
    from engineai.sdk.dashboard.links import WidgetField
    from engineai.sdk.dashboard.styling.color.typing import ColorSpec


class DotStyling(TableColumnStylingBase):
    """Styling options for dot column.

    Specify the styling options for a dot column in the table
    widget, including color and data column.
    """

    def __init__(
        self,
        *,
        color_spec: ColorSpec | None = None,
        data_column: str | WidgetField | None = None,
    ) -> None:
        """Constructor for DotStyling.

        Args:
            data_column: id of column which values are used to determine behavior of
                color of dot. Optional if color_spec is a single color.
            color_spec: spec for color of dot.
        """
        super().__init__(
            color_spec=(
                color_spec if color_spec is not None else color.Palette.MINT_GREEN
            ),
            data_column=data_column,
        )
