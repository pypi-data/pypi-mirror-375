"""Spec base for Chart Style series classes."""

from typing import Any

import pandas as pd

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.links.typing import GenericLink
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

from .enums import MarkerSymbol


class BaseChartSeriesStyling(AbstractFactory):
    """Spec base for style a chart series."""

    def __init__(
        self,
        *,
        color_spec: ColorSpec,
        data_column: TemplatedStringItem | None = None,
        marker_symbol: MarkerSymbol | None = None,
    ) -> None:
        """Construct for BaseChartSeriesStyling class.

        Args:
            color_spec: spec for coloring columns.
            data_column: name of column in pandas dataframe(s) used for color spec if
                a gradient is used. Optional for single colors.
            marker_symbol: symbol for marker in tooltips and legends.
        """
        super().__init__()
        self.__color_spec = color_spec
        self.__data_column = data_column
        self.__marker_symbol = marker_symbol

    def prepare(
        self, data_column: str | TemplatedStringItem | GenericLink | None
    ) -> None:
        """Prepare data column."""
        if (
            isinstance(self.__color_spec, DiscreteMap | Gradient)
            and self.__data_column is None
        ):
            self.__data_column = data_column

    def validate(
        self,
        *,
        data: pd.DataFrame,
    ) -> None:
        """Validate if data has the right columns.

        Args:
            data: pandas dataframe which will be used for table.

        Raises:
            ChartStylingNoDataColumnError: if a specific column does not exists in data
        """
        if (
            self.__color_spec is not None
            and isinstance(self.__color_spec, DiscreteMap | Gradient)
            and self.__data_column is None
        ):
            raise ChartStylingMissingDataColumnError(class_name=self.__class__.__name__)

        if self.__data_column is not None and self.__data_column not in data.columns:
            raise ChartStylingNoDataColumnError(
                class_name=self.__class__.__name__,
                data_column=str(self.__data_column),
            )

    def _build_extra_fields(
        self,
    ) -> dict[str, Any]:
        return {}

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        if self.__marker_symbol is not None:
            maker_symbol = {"markerSymbol": self.__marker_symbol.value}
        else:
            maker_symbol = {}

        return {
            "colorSpec": build_color_spec(spec=self.__color_spec),
            "valueKey": build_templated_strings(items=self.__data_column),
            **maker_symbol,
            **self._build_extra_fields(),
        }
