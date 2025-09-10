"""Spec for Text Styling Country Flag."""

from typing import Any

from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.widgets.components.items.styling.base import BaseItemStyling


class TextStylingCountryFlag(BaseItemStyling):
    """Spec for Text Country Flag Styling Class."""

    _INPUT_KEY: str = "countryFlag"

    def __init__(
        self,
        *,
        left: bool = True,
        data_column: TemplatedStringItem | None = None,
    ) -> None:
        """Construct spec for Text Country Flag Styling.

        Args:
            data_column (Optional[TemplatedStringItem]): styling value key.
            left (bool): whether to put flag to the left (True) or
                right (False) of column value.
        """
        super().__init__(data_column=data_column, color_spec=None)
        self.__left = left

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "left": self.__left,
            "valueKey": build_templated_strings(items=self.column),
        }
