"""Spec base for Chart Style axis lines classes."""

from typing import Any

import pandas as pd

from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.styling.color import DiscreteMap
from engineai.sdk.dashboard.styling.color import Gradient
from engineai.sdk.dashboard.styling.color.spec import build_color_spec
from engineai.sdk.dashboard.styling.color.typing import ColorSpec
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.widgets.components.charts.exceptions import (
    ChartStylingMissingDataColumnError,
)
from engineai.sdk.dashboard.widgets.components.charts.exceptions import (
    ChartStylingNoDataColumnError,
)


class AxisLineStyling(AbstractFactoryLinkItemsHandler):
    """Construct for LineStyling class."""

    def __init__(
        self,
        *,
        color_spec: ColorSpec,
        data_column: TemplatedStringItem | None = None,
    ) -> None:
        """Base spec for style a chart axis lines.

        Args:
            color_spec: spec for coloring columns.
            data_column: Column name in pandas
                DataFrame used for color spec if a gradient is used. Optional for
                single colors.
        """
        super().__init__()
        if (
            color_spec is not None
            and isinstance(color_spec, DiscreteMap | Gradient)
            and data_column is None
        ):
            raise ChartStylingMissingDataColumnError(class_name=self.__class__.__name__)
        self.__color_spec = color_spec
        self.__data_column = data_column

    @property
    def color_spec(self) -> ColorSpec:
        """Get color spec."""
        return self.__color_spec

    def validate(self, data: pd.DataFrame, **_: object) -> None:
        """Validate if data has the right columns.

        Args:
            data: pandas dataframe which will be used for table.
        """
        if self.__data_column is not None and self.__data_column not in data.columns:
            raise ChartStylingNoDataColumnError(
                class_name=self.__class__.__name__,
                data_column=str(self.__data_column),
            )

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "colorSpec": build_color_spec(spec=self.__color_spec),
            "valueKey": build_templated_strings(
                items=self.__data_column if self.__data_column else ""
            ),
        }
