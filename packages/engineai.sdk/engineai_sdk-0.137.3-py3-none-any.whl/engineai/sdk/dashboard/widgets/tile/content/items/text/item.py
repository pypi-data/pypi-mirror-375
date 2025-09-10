"""Spec for Tile Text Item."""

from typing import Any

from engineai.sdk.dashboard.formatting.text import TextFormatting
from engineai.sdk.dashboard.templated_string import DataField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.widgets.components.items.styling import TextStylingDot
from engineai.sdk.dashboard.widgets.components.items.styling import TextStylingFont

from ..base import BaseTileContentItem

TileTextStyling = TextStylingDot | TextStylingFont


class TextItem(BaseTileContentItem):
    """Spec for Tile content text Item."""

    _INPUT_KEY = "text"

    def __init__(
        self,
        *,
        data_column: TemplatedStringItem,
        formatting: TextFormatting | None = None,
        label: TemplatedStringItem | DataField | None = None,
        required: bool = True,
        styling: TileTextStyling | None = None,
    ) -> None:
        """Construct spec for the Tile Text Item class.

        Args:
            data_column: key in data that will have the valuesused by the item.
            formatting : formatting spec.
            label: str that will label the item values.
            required: Flag to make Number item mandatory. If required is True
                and no Data the widget will show an error. If
                required is False and no Data, the item is not shown.
            styling: styling spec for text item.spec for a fixed reference line.
        """
        super().__init__(
            data_column=data_column,
            formatting=formatting if formatting is not None else TextFormatting(),
            label=label,
            required=required,
        )
        self.__styling = styling

    def _build_extra_inputs(self) -> dict[str, Any]:
        if self.__styling is not None:
            return {"styling": self.__styling.build_styling()}
        return {}

    def validate(self, data: dict[str, Any]) -> None:
        """Validates Tile Item."""
        super().validate(data=data)
        if self.__styling is not None:
            self.__styling.validate(
                data=data,
                column_name="data_key",
            )
