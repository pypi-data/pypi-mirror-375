"""Specs for NumericCondition."""

import enum
from typing import Any

from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings

from .base import BaseOperation


class NumericConditionOperator(enum.Enum):
    """Numeric condition operator keys.

    Available comparison operators for numeric conditions.

    Attributes:
        GREATER (str): Greater than operator.
        GREATER_OR_EQUAL (str): Greater than or equal operator.
        EQUAL (str): Equal operator.
        NOT_EQUAL (str): Not equal operator.
        LESS (str): Less than operator.
        LESS_OR_EQUAL (str): Less than or equal operator.
    """

    GREATER = "GREATER"
    GREATER_OR_EQUAL = "GREATER_OR_EQUAL"
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS = "LESS"
    LESS_OR_EQUAL = "LESS_OR_EQUAL"


class NumericCondition(BaseOperation):
    """Specs for NumericCondition."""

    _ITEM_ID = "numericCondition"

    def __init__(
        self,
        *,
        data_column: TemplatedStringItem,
        operator: NumericConditionOperator,
        scalar: int | float,
    ) -> None:
        """Construct for NumericCondition class.

        Args:
            data_column: column in dataframe to use in comparison.
            operator: comparison operator.
            scalar: number to compare against values in value_column.
        """
        super().__init__()
        self.__operator = operator.value
        self.__data_column = data_column
        self.__scalar = scalar

    def build_filter(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "operator": self.__operator,
            "valueKey": build_templated_strings(items=self.__data_column),
            "scalar": self.__scalar,
        }
