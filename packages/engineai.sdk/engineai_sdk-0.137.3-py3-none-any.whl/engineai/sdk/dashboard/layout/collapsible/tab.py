"""Specs for Tab and TabSection."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from typing_extensions import override

from engineai.sdk.dashboard.styling.icons import Icons
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import is_valid_url

from ...interface import CollapsibleInterface
from ..selectable.base import SelectableItem
from ..selectable.base import SelectableSection

if TYPE_CHECKING:
    from engineai.sdk.dashboard.layout.typings import LayoutItem
    from engineai.sdk.dashboard.links.widget_field import WidgetField


class CollapsibleTab(SelectableItem):
    """Represents an individual tab within a TabSection."""

    INPUT_KEY = "collapsibleTab"

    def __init__(
        self,
        *,
        label: TemplatedStringItem,
        content: LayoutItem,
        icon: Icons | WidgetField | str | None = None,
        default_selected: bool = False,
    ) -> None:
        """Constructor for Tab.

        Args:
            label: label to be displayed in tab.
            content: item to be added in tab.
            icon: tab icon.
            default_selected: set tab as default selected.
        """
        super().__init__(
            label=label, content=content, default_selected=default_selected
        )
        self.validate_icon(icon)
        self.__icon = icon

    def validate_icon(self, icon: Icons | WidgetField | str | None) -> None:
        """Check if the icon is valid."""
        if icon is not None and isinstance(icon, str):
            is_valid_url(icon)

    @override
    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec."""
        return {
            "label": build_templated_strings(items=self.label),
            "item": {self.item.INPUT_KEY: self.item.build()},
            "icon": (
                build_templated_strings(
                    items=(
                        self.__icon.value
                        if isinstance(self.__icon, Icons)
                        else self.__icon
                    )
                )
                if self.__icon is not None
                else None
            ),
            "preSelected": self.default_selected,
        }


class CollapsibleTabSection(CollapsibleInterface, SelectableSection):
    """Organize dashboard content within tabs.

    The TabSection class is a crucial part of a dashboard
    layout, allowing users to organize content within tabs.

    """

    INPUT_KEY = "tabSection"

    def __init__(
        self,
        *tabs: CollapsibleTab,
        expanded: bool = False,
    ) -> None:
        """Constructor for TabSection."""
        super().__init__()
        self._add_items(*tabs)
        self.expanded = expanded

    @override
    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "options": [tab.build() for tab in self._items],
            "expanded": self.expanded,
            "height": self.height,
        }
