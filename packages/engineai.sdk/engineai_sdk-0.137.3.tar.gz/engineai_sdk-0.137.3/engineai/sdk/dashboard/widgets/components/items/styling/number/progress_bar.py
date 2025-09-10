"""Spec for Number Styling Progress Bar."""

from typing import Any

from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.widgets.components.items.styling.base import BaseItemStyling


class NumberStylingProgressBar(BaseItemStyling):
    """Spec for Number Styling Progress Bar class."""

    _INPUT_KEY = "progressBar"

    def __init__(
        self,
        *,
        column: TemplatedStringItem | None = None,
    ) -> None:
        """Construct spec for Number Styling Progress Bar.

        Args:
            column (Optional[TemplatedStringItem]): styling value key.
                Defaults to None.
        """
        super().__init__(data_column=column)

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "valueKey": build_templated_strings(items=self.column),
        }
