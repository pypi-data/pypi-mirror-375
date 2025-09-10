"""Specification for column font styling."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from typing_extensions import override

from .base import TableColumnStylingBase

if TYPE_CHECKING:
    from engineai.sdk.dashboard.links import WidgetField
    from engineai.sdk.dashboard.styling.color.typing import ColorSpec


class FontStyling(TableColumnStylingBase):
    """Font styling options.

    Specify the font styling options for a column in the table widget,
    including color, data column, and background highlighting.
    """

    def __init__(
        self,
        *,
        color_spec: ColorSpec,
        data_column: str | WidgetField | None = None,
        highlight_background: bool = False,
    ) -> None:
        """Constructor for FontStyling.

        Args:
            data_column: id of column which values are used to determine behavior of
                color of dot. Optional if color_spec is a single color.
            color_spec: spec for color of dot.
            highlight_background: Highlight value background.
        """
        super().__init__(data_column=data_column, color_spec=color_spec)
        self.__highlight_background = highlight_background

    @override
    def _build_extra_inputs(self) -> dict[str, Any]:
        return {"highlightBackground": self.__highlight_background}
