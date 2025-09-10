"""Spec for table header columns (i.e. above normal columns)."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Union

from typing_extensions import override

from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.widgets.table.columns.items.text import TextColumn

from .columns.items.base import Column
from .exceptions import TableColumnsEmptyError
from .exceptions import TableDuplicatedItemIdError
from .exceptions import TableHeaderLevelsError

if TYPE_CHECKING:
    import pandas as pd

    from engineai.sdk.dashboard.links.typing import GenericLink


TableColumns = Union[str, "Column", "Header", list[Union[str, "Column", "Header"]]]


class Header(AbstractFactoryLinkItemsHandler):
    """Specify header columns with optional tooltips for table widget.

    Specify the columns to be displayed as headers above the normal
    columns in the table widget, along with optional tooltip text.
    """

    def __init__(
        self,
        columns: TableColumns,
        label: str | GenericLink,
        tooltip_text: list[TemplatedStringItem] | None = None,
    ) -> None:
        """Constructor for Header.

        Args:
            columns: header(s)/column(s) into the Table Widget. When this is of type
                string, it is assumed to be a text column.
            label: label to be displayed for this column.
            tooltip_text: info text to explain column. Each element of list is
                displayed as a separate paragraph.

        Examples:
            ??? example "Create a Table widget with Header"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import table
                data = pd.DataFrame(
                    {
                        "name": ["A", "B", "C"],
                        "value": [1, 2, 3],
                        "country": ["ES", "PT", "UK"],
                    },
                )
                Dashboard(
                    content=table.Table(
                        data=data,
                        columns=[
                            table.Header(
                                label="Company Info",
                                columns=[
                                    "name",
                                    table.NumberColumn(data_column="value"),
                                ]
                            ),
                            "country",
                        ],
                    )
                )
                ```
        """
        super().__init__()
        self.__label = label
        self.__tooltip_text = tooltip_text or []
        self.__children: list[Column | Header] = []
        self.__depth: int = 1
        self.__parent_header: Header | None = None
        self.__item_id: str = "Header_" + (
            label if isinstance(label, str) else label.item_id
        )
        self._set_columns(columns)

    @property
    def item_id(self) -> str:
        """Return Item ID."""
        return self.__item_id

    @property
    def tooltip_text(self) -> list[TemplatedStringItem]:
        """Return Tooltip Text."""
        return self.__tooltip_text

    @tooltip_text.setter
    def tooltip_text(self, tooltip_text: list[TemplatedStringItem]) -> None:
        """Set Tooltip Text."""
        self.__tooltip_text = tooltip_text

    @property
    def depth(self) -> int:
        """Returns Header Depth in the Hierarchy, used for Heights.

        Returns:
            int: with the following values:
                3: Header -> Header -> Column
                2: Header -> Column
                1: Header
        """
        return self.__depth + max((child.depth for child in self.__children), default=0)

    def prepare(self) -> None:
        """Prepare class."""
        for item in self.__children:
            item.prepare()

    def validate(self, *, data: pd.DataFrame) -> None:
        """Validate headers children.

        Args:
            data: pandas dataframe which will be used for table
        """
        for child in self.__children:
            child.validate(data=data)

    def validate_item_ids(
        self, widget_id: str, previous_level_item_id: set[str]
    ) -> set[str]:
        """Validate children item ids based on previous ids.

        Args:
            widget_id: Unique widget ID in the dashboard.
            previous_level_item_id: set of item_ids from the previous level.

        Raises:
            TableDuplicatedItemIdError: if item_id is duplicated
        """
        validated_item_ids: set[str] = previous_level_item_id.copy()

        for child in self.__children:
            if child.item_id in validated_item_ids:
                raise TableDuplicatedItemIdError(
                    widget_id=widget_id, item_ids=child.item_id
                )

            validated_item_ids.add(child.item_id)
            if isinstance(child, Header):
                validated_item_ids.update(
                    child.validate_item_ids(
                        widget_id=widget_id,
                        previous_level_item_id=validated_item_ids,
                    )
                )

        return validated_item_ids

    @property
    def label(self) -> str | GenericLink:
        """Label used for column.

        Returns:
            str: column label
        """
        return self.__label

    @property
    def parent_header(self) -> Header | None:
        """Parent header column.

        Returns:
            None: No Parent associated
            TableHeader: parent object
        """
        return self.__parent_header

    @parent_header.setter
    def parent_header(self, parent_header: Header) -> None:
        """Set Parent."""
        self.__parent_header = parent_header

    @property
    def children(self) -> list[Column | Header]:
        """List children.

        Returns:
            List[Union[Column, Header]]: children list.
        """
        return self.__children

    def _set_columns(self, columns: TableColumns) -> None:
        if isinstance(columns, list):
            if len(columns) == 0:
                raise TableColumnsEmptyError
            for item in columns:
                if isinstance(item, str):
                    self._add_items(TextColumn(data_column=item))
                else:
                    self._add_items(item)
        elif isinstance(columns, str):
            self._add_items(TextColumn(data_column=columns))
        else:
            self._add_items(columns)

    def _add_items(self, item: Column | Header) -> None:
        """Add Header(s) or Column(s) into the current Header.

        Args:
            item: item object.
        """
        if not isinstance(item, Column):
            item.set_children_id(self.__item_id)
            self._validate_header(item)
            item.parent_header = self
        item.set_item_id(self.__item_id)
        self.__children.append(item)

    def _validate_header(self, header: Header) -> None:
        header_child_is_header = [
            isinstance(child, Header) for child in header.children
        ]
        if any(header_child_is_header) or self.parent_header is not None:
            raise TableHeaderLevelsError

    def set_item_id(self, item_id: str) -> None:
        """Set item_id.

        Args:
            item_id: parent item_id.
        """
        self.__item_id = f"{item_id}__{self.__item_id}"

    def set_children_id(self, item_id: str) -> None:
        """Set children item_id.

        Args:
            item_id: parent item_id.
        """
        for child in self.children:
            if isinstance(child, Header):
                child.set_children_id(item_id=item_id)
            child.set_item_id(item_id=item_id)

    @override
    def build(self) -> dict[str, Any]:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return {
            "label": build_templated_strings(items=self.__label),
            "tooltipText": [
                build_templated_strings(items=tooltip)
                for tooltip in self.__tooltip_text
            ],
            "children": [
                {"header": child.build()}
                if isinstance(child, Header)
                else {"column": child.build()}
                for child in self.__children
            ],
        }
