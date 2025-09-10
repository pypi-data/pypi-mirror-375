"""Spec for Base Url Link."""

import warnings
from abc import abstractmethod
from typing import Any

import pandas as pd

from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.templated_string import DataField
from engineai.sdk.dashboard.templated_string import InternalDataField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from .exceptions import ActionLinkMissingColumnError


class BaseLink(AbstractFactoryLinkItemsHandler):
    """Spec for Base Action Link."""

    _INPUT_KEY: str | None = None

    def __init__(
        self,
        data_column: TemplatedStringItem,
        tooltip: list[str] | TemplatedStringItem | DataField | None = None,
    ) -> None:
        """Construct for ActionLink class.

        Args:
            data_column (TemplatedStringItem): column that
                contains the url.
            tooltip (Union[List[str], TemplatedStringItem, DataField]): tooltip
                information from a data columns.
        """
        super().__init__()
        self._data_column = data_column
        self._tooltip = InternalDataField(tooltip) if tooltip else None

    @property
    def input_key(self) -> str:
        """Return input key."""
        if self._INPUT_KEY is None:
            msg = (
                "Input key is not defined for this class. "
                "Please define it in the child class."
            )
            raise NotImplementedError(msg)
        return self._INPUT_KEY

    def validate(
        self,
        *,
        data: dict[str, Any] | pd.DataFrame,
        widget_class: str,
        warnings_flag: bool = False,
        key: str | None = None,
    ) -> None:
        """Validate action URL Link."""
        columns = data.columns if isinstance(data, pd.DataFrame) else data
        data_column = str(self._data_column)

        if data_column not in columns:
            if warnings_flag:
                warnings.warn(
                    f"Missing TreeNodesTitleLink `UrlLink` "
                    f"{data_column=} on "
                    f"provided data in node `{key}`."
                )
            else:
                raise ActionLinkMissingColumnError(
                    column_name="data_column",
                    column_value=data_column,
                    class_name=widget_class,
                    key=key,
                )

        if self._tooltip:
            self._tooltip.validate(
                data=data,
                column_name=data_column,
                node=key,
                warning_flags=warnings_flag,
            )

    @abstractmethod
    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """

    def build_action(self) -> dict[str, Any]:
        """Builds spec for dashboard API."""
        return {self.input_key: self.build()}
