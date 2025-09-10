"""Specs for OperationDataFilterLimit."""

from typing import Any

from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings

from .base import BaseOperation
from .exceptions import OrderByDuplicatedColumnsError


class OrderByItem:
    """Spec for OrderBy."""

    def __init__(
        self,
        *,
        data_column: TemplatedStringItem,
        ascending: bool = False,
    ) -> None:
        """Construct for OperationDataFilterOrderBy class.

        Args:
            data_column: column to order by.
            ascending: ascending sorting operation.
        """
        self._data_column = data_column
        self._sort = "ASC" if ascending else "DESC"

    def __hash__(self) -> int:
        return hash(f"{self._data_column}_{self._sort}")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and (
            self._sort == other._sort and self._data_column == other._data_column
        )

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "dataKey": build_templated_strings(items=self._data_column),
            "sort": self._sort,
        }


class OrderBy(BaseOperation):
    """Specs for OrderBy."""

    _ITEM_ID = "orderBy"

    def __init__(self, *items: str | OrderByItem) -> None:
        """Construct for OrderBy class.

        Args:
            items: order by items.
        """
        super().__init__()
        self.__order_by_list: list[OrderByItem] = self.__set_items(list(items))

    def __set_items(self, items: list[str | OrderByItem]) -> list[OrderByItem]:
        set_items = []
        for item in items:
            if isinstance(item, str):
                set_items.append(OrderByItem(data_column=item))
            else:
                set_items.append(item)

        if len(items) != len(set(set_items)):
            raise OrderByDuplicatedColumnsError
        return set_items

    def build_filter(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "conditions": [condition.build() for condition in self.__order_by_list],
        }
