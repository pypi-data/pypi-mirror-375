"""Spec for Url Link."""

from collections.abc import Iterable
from typing import Any

from engineai.sdk.dashboard.templated_string import DataField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.widgets.components.actions.links.base import BaseLink


class UrlLink(BaseLink):
    """Spec for Url Link."""

    _INPUT_KEY: str = "actionHyperLink"

    def __init__(
        self,
        data_column: TemplatedStringItem,
        tooltip: list[str] | TemplatedStringItem | DataField | None = None,
    ) -> None:
        """Construct for ActionUrlLink class.

        Args:
            data_column (TemplatedStringItem): column that
                contains the url.
            tooltip (Optional[Union[List[str], TemplatedStringItem, DataField]]): static
                tooltip spec.
        """
        super().__init__(
            data_column=data_column,
            tooltip=tooltip,
        )

    @property
    def data_column(self) -> TemplatedStringItem:
        """Get data column."""
        return self._data_column

    def _build_tooltip(self) -> Iterable[Any]:
        build_tooltip = self._tooltip.build() if self._tooltip else None
        if self._tooltip and isinstance(build_tooltip, Iterable):
            tooltip = build_tooltip
        elif self._tooltip:
            tooltip = [build_tooltip]
        else:
            tooltip = []
        return tooltip

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "urlKey": build_templated_strings(items=self._data_column),
            "tooltip": self._build_tooltip(),
            "params": [],
        }
