"""Spec for Number Styling Arrow."""

from typing import Any

from engineai.sdk.dashboard.styling.color.divergent import Divergent
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.widgets.components.items.styling.base import BaseItemStyling


class NumberStylingArrow(BaseItemStyling):
    """Spec for Number Arrow Styling class."""

    _INPUT_KEY: str = "arrow"

    def __init__(
        self,
        *,
        data_column: TemplatedStringItem | None = None,
        color_divergent: Divergent,
    ) -> None:
        """Construct spec Number Arrow Styling.

        Args:
            color_divergent (ColorDivergent): specs for color.
            data_column (TemplatedStringItem): styling value key.
        """
        super().__init__(
            data_column=data_column,
        )
        self.__color_divergent = color_divergent

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "divergentPalette": self.__color_divergent.build(),
            "valueKey": build_templated_strings(items=self.column),
        }
