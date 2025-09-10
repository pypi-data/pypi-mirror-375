"""Spec for Text Styling Chip."""

from engineai.sdk.dashboard.styling.color.typing import ColorSpec
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.widgets.components.items.styling.base import BaseItemStyling


class TextStylingChip(BaseItemStyling):
    """Spec for Text Chip Styling Class."""

    _INPUT_KEY = "chip"

    def __init__(
        self,
        *,
        color_spec: ColorSpec | None = None,
        data_column: TemplatedStringItem | None = None,
    ) -> None:
        """Construct spec for Text Chip Styling.

        Args:
            color_spec (Optional[ColorSpec]): specs for color.
            data_column (Optional[TemplatedStringItem]): styling value key.
        """
        super().__init__(data_column=data_column, color_spec=color_spec)
