"""Spec for Button Action."""

from typing import Any

from typing_extensions import override

from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.widgets.components.actions.links.base import BaseLink


class ExternalEvent(BaseLink):
    """Spec for External Event Action."""

    _INPUT_KEY: str = "actionExternalEventHyperLink"

    def __init__(
        self,
        *,
        event_type: TemplatedStringItem,
        data_column: str | WidgetField,
    ) -> None:
        """Construct spec for ExternalEvent.

        Args:
            event_type: event type spec.
            data_column: event data spec.
        """
        super().__init__(data_column=data_column)
        self.__event_type = event_type

    @property
    def data_column(self) -> TemplatedStringItem:
        """Get data column."""
        return self._data_column

    @override
    def build(self) -> dict[str, Any]:
        """Builds spec for dashboard API."""
        return {
            "type": build_templated_strings(items=self.__event_type),
            "dataKey": build_templated_strings(items=self._data_column),
        }
