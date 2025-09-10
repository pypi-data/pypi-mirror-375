"""Base spec for Table Columns that use charts."""

from __future__ import annotations

import warnings
from abc import ABC
from typing import TYPE_CHECKING
from typing import Any

import numpy as np
from typing_extensions import override

from engineai.sdk.dashboard.styling.color import Palette
from engineai.sdk.dashboard.templated_string import DataField
from engineai.sdk.dashboard.templated_string import InternalDataField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.widgets.table.columns.items.base import Column
from engineai.sdk.dashboard.widgets.table.columns.items.exceptions import (
    TableColumnChartIncorrectLengthError,
)
from engineai.sdk.dashboard.widgets.table.columns.items.exceptions import (
    TableColumnDataTypeError,
)
from engineai.sdk.dashboard.widgets.table.columns.items.exceptions import (
    TableDataColumnValueKeyError,
)
from engineai.sdk.dashboard.widgets.table.columns.styling.base import (
    TableColumnStylingBase,
)

if TYPE_CHECKING:
    import pandas as pd

    from engineai.sdk.dashboard.links import WidgetField
    from engineai.sdk.dashboard.links.typing import GenericLink

ReferenceLineType = int | float | DataField


class ChartColumn(Column, ABC):
    """Base spec for Chart Columns in a Table widget."""

    def __init__(
        self,
        *,
        data_column: str | WidgetField,
        data_key: str | WidgetField,
        label: str | GenericLink | None = None,
        styling: Palette | TableColumnStylingBase | None = None,
        hiding_priority: int = 0,
        tooltip_text: list[TemplatedStringItem] | None = None,
        min_width: int | None = None,
        reference_line: ReferenceLineType | None = None,
        optional: bool = False,
    ) -> None:
        """Base spec for Table Chart Columns in a Table widget.

        Args:
            data_column: name of column in pandas dataframe(s) used to fill this
                column.
            data_key: key in object that contains the value for the line chart.
            label: label to be displayed for this column.
            styling: styling specs.
            hiding_priority: columns with lower hiding_priority are hidden first
                if not all data can be shown.
            tooltip_text: info text to explain column. Each element of list is
                displayed as a separate paragraph.
            min_width: min width of the column in pixels.
            reference_line: reference line that will be added to the chart created.
            optional: flag to make the column optional if there is no Data for that
                columns.
        """
        super().__init__(
            data_column=data_column,
            label=label,
            hiding_priority=hiding_priority,
            tooltip_text=tooltip_text,
            min_width=min_width,
            optional=optional,
        )
        self._data_key: str | WidgetField = data_key
        self.__styling = (
            TableColumnStylingBase(color_spec=styling)
            if isinstance(styling, Palette)
            else styling
        )
        self.__set_reference_line(reference_line)

    @property
    def data_key(self) -> str | WidgetField:
        """Returns Data Key."""
        return self._data_key

    @property
    def styling(self) -> TableColumnStylingBase | None:
        """Returns Styling object."""
        return self.__styling

    @property
    def reference_line(self) -> InternalDataField | None:
        """Get chart reference line."""
        return self.__reference_line

    def __set_reference_line(self, reference_line: ReferenceLineType | None) -> None:
        if reference_line is None:
            self.__reference_line = None
        elif isinstance(reference_line, (DataField)):
            self.__reference_line = InternalDataField(reference_line)
        else:
            self.__reference_line = InternalDataField(str(reference_line))

    def _build_styling(self) -> dict[str, Any] | None:
        return None if self.styling is None else self.styling.build()

    def _validate_list_row_data(self, *, row_data: list[dict[str, Any]]) -> None:
        for value in row_data:
            if self.data_key not in value:
                raise TableDataColumnValueKeyError(
                    data_column=self.data_column, data_key=self.data_key
                )
            if self.styling:
                self.styling.validate(data=value)

    def _validate_dict_row_data(self, *, row_data: dict[str, list[Any]]) -> None:
        if self.data_key not in row_data:
            raise TableDataColumnValueKeyError(
                data_column=self.data_column, data_key=self.data_key
            )
        if self.styling:
            self.styling.validate(data=row_data)

            styling_data_column = self.styling.data_column
            if styling_data_column is not None and len(
                row_data[str(self.data_key)]
            ) != len(row_data[str(styling_data_column)]):
                raise TableColumnChartIncorrectLengthError(data_column=self.data_column)

    @override
    def _custom_validation(self, *, data: pd.DataFrame) -> None:
        """Custom validation for each columns to implement.

        Args:
            data: pandas dataframe which will be used for table.

        Raises:
            TableColumnChartIncorrectLengthError - if data and styling has not the same
                length
            TableDataColumnValueTypeError - if the chart column do not have a dictionary
                structure
            TableColumnDataTypeError - if data column is not a dictionary, list
                nor a numpy's ndarray
        """
        if self.__reference_line is not None:
            self.__reference_line.validate(data=data)

        data_to_numpy = data[self.data_column].to_numpy()
        for index in range(len(data_to_numpy)):
            row_data = data_to_numpy[index]
            self._validate_column_type(row_data=row_data)
            if row_data is None:
                warnings.warn(f"Value for data_column=`{self.data_column}` is None.")
            elif isinstance(row_data, list):
                self._validate_list_row_data(row_data=row_data)
            elif isinstance(row_data, dict):
                self._validate_dict_row_data(row_data=row_data)

    def _validate_column_type(self, *, row_data: Any) -> None:
        if row_data is not None and not isinstance(row_data, dict | list | np.ndarray):
            raise TableColumnDataTypeError(
                data_column=self.data_column,
                row_type=type(row_data),
                types="Dict, List, ndarray or None",
            )
