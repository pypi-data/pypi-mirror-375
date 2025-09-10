"""Join operation for Dashboard API."""

import enum
from typing import Any

from engineai.sdk.dashboard.base import DependencyInterface
from engineai.sdk.dashboard.data.operations.base import BaseOperation
from engineai.sdk.dashboard.links.web_component import WebComponentLink
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.widgets.utils import build_data


class JoinOperations(enum.Enum):
    """Join operations.

    Available join operations for combining datasets.

    Attributes:
        INNER_JOIN (str): Inner join operation.
        LEFT_JOIN (str): Left join operation.
        RIGHT_JOIN (str): Right join operation.
    """

    INNER_JOIN = "INNER_JOIN"
    LEFT_JOIN = "LEFT_JOIN"
    RIGHT_JOIN = "RIGHT_JOIN"


class Join(BaseOperation):
    """Join operation for Dashboard API."""

    _ITEM_ID = "join"
    _FORCE_SKIP_VALIDATION = True

    def __init__(
        self,
        *,
        link: WebComponentLink,
        left: str,
        right: str,
        operator: JoinOperations,
        alias: str,
    ) -> None:
        """Constructor for Join Class.

        Args:
            link: link to the web component data.
            left: left key to join.
            right: right key to join.
            operator: join operator.
            alias: alias for the join.
        """
        self.__link = link
        self.__left = left
        self.__right = right
        self.__operator = operator
        self.__alias = alias

    @property
    def dependencies(self) -> list[DependencyInterface]:
        """Return dependencies."""
        return [self.__link.dependency]

    def build_filter(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "data": build_data(
                path=f"{self.__link.dependency.dependency_id}."
                f"{self.__link.dependency.field}"
            ),
            "operator": self.__operator.value,
            "alias": self.__alias,
            "condition": {
                "leftKey": build_templated_strings(items=self.__left),
                "rightKey": build_templated_strings(items=self.__right),
            },
        }
