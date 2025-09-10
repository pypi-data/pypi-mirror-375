"""Spec for Number Styling Dot."""

from engineai.sdk.dashboard.styling.color.typing import ColorSpec
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.widgets.components.items.styling.base import BaseItemStyling


class NumberStylingDot(BaseItemStyling):
    """Spec for Number Dot Styling class."""

    _INPUT_KEY: str = "dot"

    def __init__(
        self,
        *,
        color_spec: ColorSpec,
        data_column: TemplatedStringItem | None = None,
    ) -> None:
        """Construct spec for Number Dot Styling.

        Args:
            color_spec (ColorSpec): specs for color.
            data_column (Optional[TemplatedStringItem]): styling value key.
        """
        super().__init__(
            color_spec=color_spec,
            data_column=data_column,
        )
