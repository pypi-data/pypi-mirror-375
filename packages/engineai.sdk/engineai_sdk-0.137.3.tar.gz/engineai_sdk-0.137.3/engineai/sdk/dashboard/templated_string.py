"""Spec to build different templated strings."""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

import pandas as pd

from engineai.sdk.dashboard.exceptions import DataFieldColumnNameNotProvidedError
from engineai.sdk.dashboard.exceptions import DataFieldInItemIDKeyNotFoundError
from engineai.sdk.dashboard.exceptions import DataFieldNotFoundError

from .base import AbstractLink

if TYPE_CHECKING:
    from collections.abc import Iterable

TemplatedStringItem = str | AbstractLink | list[AbstractLink]


@dataclass
class DataField:
    """Spec for DataField."""

    field: str
    default: str | None = None


class InternalDataField:
    """Internal Data Field object."""

    def __init__(
        self, item: list[str] | TemplatedStringItem | DataField | None = None
    ) -> None:
        """Internal Data Field __init__ method."""
        self._value, self._value_key = self._set_value_and_value_key(item)
        self.__dependency_id = ""

    def _set_value_and_value_key(
        self,
        item: list[str] | TemplatedStringItem | DataField | None,
    ) -> tuple[list[str] | TemplatedStringItem | None, TemplatedStringItem | None]:
        if isinstance(item, DataField):
            return cast("TemplatedStringItem", item.default), item.field
        return item, None

    @property
    def dependency_id(self) -> str:
        """Get dependency_id value."""
        return self.__dependency_id

    def set_dependency_id(self, dependency_id: str, indexed: bool = True) -> None:
        """Set dependency_id value.

        Args:
            dependency_id (str): The dependency identifier for the data field.
            indexed (bool, optional): Whether data used is a DataFrame (True)
                or a dict (False). Defaults to True.
        """
        # TODO: The current dependency_id depends on the Widget, we need to
        # validate this as we add more widgets
        if indexed:
            self.__dependency_id = f"{dependency_id}.0."
        else:
            self.__dependency_id = dependency_id

    def __contains_key(
        self,
        param: TemplatedStringItem,
        data: pd.DataFrame | dict[str, Any],
    ) -> bool:
        if isinstance(data, pd.DataFrame):
            return param in data.columns
        return param in data

    def __build_value_dependency(
        self,
        value: TemplatedStringItem | None = None,
        value_key: TemplatedStringItem | None = None,
    ) -> dict[str, Any] | None:
        """Builds spec for value dependency.

        Args:
            value (TemplatedStringItem]): value to be
                displayed in the templated string.
            value_key (TemplatedStringItem]): value key to be
                displayed in the templated string.

        """
        if value is None and value_key is None:
            return {
                "value": build_templated_strings(items=None),
                "valueKey": build_templated_strings(items=None),
            }
        return {
            "value": (
                build_templated_strings(items=value) if value is not None else None
            ),
            "valueKey": build_templated_strings(items=value_key) if value_key else None,
        }

    def validate(
        self,
        data: pd.DataFrame | dict[str, Any],
        column_name: str | None = None,
        node: str | None = None,
        item_id_key: str | None = None,
        warning_flags: bool = False,
    ) -> None:
        """Validate if key or column exists in data.

        Args:
            data (Union[pd.DataFrame, dict[str, Any]]): pandas DataFrame or dict where
                the data is present.
            column_name (Optional[str]): column name for additional checks.
            node (Optional[str]): On which node (if using data as dict) the check is to
                be made.
            item_id_key: (Optional[str]): key in data (if using data as dict) used to
                identify the data that feeds this item.
            warning_flags (bool): Whether to raise error or warning.
        """
        if self._value_key:
            if (
                item_id_key
                and item_id_key in data
                and self._value_key not in data[item_id_key]
            ):
                raise DataFieldInItemIDKeyNotFoundError(
                    field=str(self._value_key),
                    item_id_key=item_id_key,
                )

            if not self.__contains_key(param=self._value_key, data=data):
                if self._value is None and not warning_flags:
                    raise DataFieldNotFoundError(field=str(self._value_key))
                if self._value is None and warning_flags:
                    if column_name is None or node is None:
                        raise DataFieldColumnNameNotProvidedError
                    warnings.warn(
                        f"Missing data_column=`{column_name}` on provided "
                        "data in {node=}."
                    )
                self._value_key = None

    def build(self) -> Any | None:
        """Builds spec for value dependency."""
        if isinstance(self._value, list) and all(
            isinstance(value, str) for value in self._value
        ):
            return [
                self.__build_value_dependency(value=value, value_key=self._value_key)
                for value in self._value
            ]
        return self.__build_value_dependency(
            value=cast("TemplatedStringItem", self._value), value_key=self._value_key
        )


def build_templated_strings(
    *,
    items: TemplatedStringItem | None = None,
    separator: str = "-",
    prefix: str = "",
    suffix: str = "",
) -> Any | None:
    """Builds spec for templated strings.

    Args:
        items (Optional[TemplatedStringItem]): items to be displayed in the
            templated string.
        separator (str): items separator in case of a list of WidgetLinks
            Defaults to `-` character.
        prefix (str): prefix value to use in before each item.
            Defaults to empty string.
        suffix (str): suffix value to use in after each item.
            Defaults to empty string.

    Raises:
        TypeError: if no type match found.
    """
    if items is not None:
        template = _build_template(
            items=items, separator=separator, prefix=prefix, suffix=suffix
        )
        return {"template": template}
    return {"template": ""}


def _build_template(
    *,
    items: TemplatedStringItem,
    separator: str = "-",
    prefix: str = "",
    suffix: str = "",
) -> str:
    if isinstance(items, AbstractLink):
        return _build_list_template(items=[items], prefix=prefix, suffix=suffix)
    if isinstance(items, list):
        return _build_list_template(
            items=items, prefix=prefix, suffix=suffix, separator=separator
        )
    return _build_string_template(items=str(items), prefix=prefix, suffix=suffix)


def _build_string_template(
    *,
    items: str,
    prefix: str = "",
    suffix: str = "",
) -> str:
    if prefix or suffix:
        warnings.warn(
            "You don't need to specified `prefix` or "
            "`suffix` when using string as label. You can use them"
            "directly in the `label`."
        )
    return f"{prefix}{items}{suffix}"


def _build_list_template(
    *,
    items: Iterable[AbstractLink],
    separator: str = "-",
    prefix: str = "",
    suffix: str = "",
) -> str:
    template = separator.join(f"{item}" for item in items)
    return f"{prefix}{template}{suffix}"
