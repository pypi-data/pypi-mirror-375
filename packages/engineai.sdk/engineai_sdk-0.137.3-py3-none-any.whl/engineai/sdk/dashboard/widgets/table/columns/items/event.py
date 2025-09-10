"""Specification for External Action columns in Table widget."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from typing_extensions import override

from engineai.sdk.dashboard.widgets.components.actions.links import UrlLink
from engineai.sdk.dashboard.widgets.components.actions.links.external import (
    ExternalEvent,
)
from engineai.sdk.dashboard.widgets.table.columns.items.base import Column

if TYPE_CHECKING:
    import pandas as pd

    from engineai.sdk.dashboard.links import WidgetField
    from engineai.sdk.dashboard.templated_string import TemplatedStringItem

Actions = UrlLink | ExternalEvent


class EventColumn(Column):
    """Specifications for EventColumn class."""

    _ITEM_ID_TYPE: str = "EVENT_COLUMN"

    def __init__(
        self,
        *,
        action: Actions,
        label: str | WidgetField | None = None,
        hiding_priority: int = 0,
        tooltip_text: list[TemplatedStringItem] | None = None,
        min_width: int | None = None,
    ) -> None:
        """Class EventColumn is used as urlx column for the Table Widget.

        Args:
            action: action to be triggered on click.
            label: label to be displayed for this column.
            hiding_priority: columns with lower hiding_priority are hidden first
                if not all data can be shown.
            tooltip_text: info text to explain column. Each element of list is
                displayed as a separate paragraph.
            min_width: min width of the column in pixels.
        """
        super().__init__(
            data_column=action.data_column,  # type: ignore[arg-type]
            label=label,
            hiding_priority=hiding_priority,
            tooltip_text=tooltip_text,
            min_width=min_width,
        )
        self.__action = action

    @override
    def prepare(self) -> None:
        """Url Column has no styling."""

    @override
    def _custom_validation(
        self,
        *,
        data: pd.DataFrame,
    ) -> None:
        """Custom validation for each columns to implement."""
        self.__action.validate(data=data, widget_class="Table")

    def _build_action(self) -> dict[str, Any]:
        if isinstance(self.__action, ExternalEvent):
            return {
                "actionExternalEventHyperLink": self.__action.build(),
            }

        if isinstance(self.__action, UrlLink):
            return {"hyperLink": self.__action.build()}

        msg = "EventColumn `action` requires one of ExternalEvent, UrlLink."  # type: ignore[unreachable]
        raise TypeError(msg)

    @override
    def _build_column(self) -> dict[str, Any]:
        return {"actionColumn": {"actions": self._build_action()}}
