"""Specification for text columns."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pandas as pd
from typing_extensions import override

from engineai.sdk.dashboard.formatting import DateTimeFormatting
from engineai.sdk.dashboard.styling.color import Palette
from engineai.sdk.dashboard.widgets.table.columns.styling.cell import CellStyling
from engineai.sdk.dashboard.widgets.table.columns.styling.country_flag import (
    CountryFlagStyling,
)
from engineai.sdk.dashboard.widgets.table.columns.styling.dot import DotStyling
from engineai.sdk.dashboard.widgets.table.columns.styling.font import FontStyling
from engineai.sdk.dashboard.widgets.table.columns.styling.utils import (
    build_styling_input,
)
from engineai.sdk.dashboard.widgets.table.enums import HorizontalAlignment

from .base import Column
from .exceptions import TableDatetimeColumnMappingError

if TYPE_CHECKING:
    from engineai.sdk.dashboard.links import WidgetField
    from engineai.sdk.dashboard.links.typing import GenericLink
    from engineai.sdk.dashboard.templated_string import TemplatedStringItem

DatetimeColumnStyling = CellStyling | CountryFlagStyling | DotStyling | FontStyling


class DatetimeColumn(Column):
    """Define table widget column: Datetime information with data source.

    Define a column in the table widget that displays datetime information,
    including options for data source, label, formatting, and alignment.
    """

    _ITEM_ID_TYPE: str = "DATETIME"

    def __init__(
        self,
        *,
        data_column: str | WidgetField,
        label: str | GenericLink | None = None,
        formatting: DateTimeFormatting | None = None,
        styling: Palette | DatetimeColumnStyling | None = None,
        align: HorizontalAlignment = HorizontalAlignment.CENTER,
        hiding_priority: int = 0,
        tooltip_text: list[TemplatedStringItem] | None = None,
        min_width: int | None = None,
        sortable: bool = True,
        optional: bool = False,
    ) -> None:
        """Constructor for DatetimeColumn.

        Args:
            data_column: name of column in pandas dataframe(s) used for this widget.
            label: label to be displayed for this column.
            formatting: formatting spec.
            styling: styling spec for column. One of TableColumnStylingCell,
                TableColumnStylingCountryFlag or TableColumnStylingDot.
            align: horizontal alignment of the column.
            hiding_priority: columns with lower hiding_priority are hidden first
                if not all data can be shown.
            tooltip_text: info text to explain column. Each element of list is
                displayed as a separate paragraph.
            min_width: min width of the column in pixels.
            sortable: determines if column can be sorted.
            optional: flag to make the column optional if there is no Data for that
                columns.

        Examples:
            ??? example "Create a Table widget with DatetimeColumn"
                ```py linenums="1"
                import pandas as pd
                import datetime
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import table
                data = pd.DataFrame(
                    {
                        "datetime": datetime.datetime.now().timestamp(),
                    },
                )
                Dashboard(
                    content=table.Table(
                        data=data,
                        columns=[
                            table.DatetimeColumn(
                                data_column="datetime",
                                ),
                            ),
                        ],
                    )
                )
                ```
        """
        super().__init__(
            data_column=data_column,
            label=label,
            hiding_priority=hiding_priority,
            tooltip_text=tooltip_text,
            min_width=min_width,
            optional=optional,
        )
        self.__align = align
        self.__styling = (
            CellStyling(color_spec=styling) if isinstance(styling, Palette) else styling
        )
        self.__sortable = sortable
        self.__formatting = formatting if formatting else DateTimeFormatting()

    @override
    def prepare(self) -> None:
        """Prepare data column."""
        if self.__styling is not None:
            self.__styling.prepare(self._data_column)

    @override
    def _custom_validation(self, *, data: pd.DataFrame) -> None:
        """Custom validation for each columns to implement.

        Args:
            data: pandas dataframe which will be used for table.

        Raises:
            TableDatetimeColumnMappingError: if data contains data_column which are
                not epoch time
        """
        try:
            pd.to_datetime(data[self.data_column], unit="ms")
        except ValueError as e:
            raise TableDatetimeColumnMappingError(data_column=self.data_column) from e

        if self.__styling:
            self.__styling.validate(data=data)

    def _build_styling(self) -> dict[str, Any] | None:
        return (
            None
            if self.__styling is None
            else build_styling_input(
                data_column=self.data_column, styling=self.__styling
            )
        )

    @override
    def _build_column(self) -> dict[str, Any]:
        return {
            "dateTimeColumn": {
                "sortable": self.__sortable,
                "formatting": self.__formatting.build(),
                "align": self.__align.value,
                "styling": self._build_styling(),
                "optional": self._optional,
            }
        }
