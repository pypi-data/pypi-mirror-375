"""Specs for x axis of a Cartesian chart."""

import pandas as pd

from engineai.sdk.dashboard.formatting import AxisNumberFormatting
from engineai.sdk.dashboard.links.typing import GenericLink
from engineai.sdk.dashboard.widgets.cartesian.exceptions import (
    CartesianValidateDataColumnNotFoundError,
)
from engineai.sdk.dashboard.widgets.components.charts.axis.scale import AxisScale

from .base import CartesianBaseAxis


class XAxis(CartesianBaseAxis):
    """Specs for X Axis of a Cartesian chart."""

    def __init__(
        self,
        data_column: str | GenericLink,
        *,
        title: str | GenericLink = "X",
        enable_crosshair: bool = False,
        formatting: AxisNumberFormatting | None = None,
        scale: AxisScale | None = None,
    ) -> None:
        """Construct x axis for a Cartesian chart.

        Args:
            data_column: name of column in pandas
                dataframe(s) used for X axis values.
            title: axis title
            enable_crosshair: whether to enable crosshair that follows either
                the mouse pointer or the hovered point.
            formatting: formatting spec for axis labels.
            scale: X axis scale.
        """
        super().__init__(
            title=title,
            enable_crosshair=enable_crosshair,
            formatting=formatting,
            scale=scale,
        )

        self.__data_column = data_column

    @property
    def data_column(self) -> str | GenericLink:
        """Get X axis data column."""
        return self.__data_column

    def _axis_validate(self, *, data: pd.DataFrame) -> None:
        if isinstance(self.data_column, str) and self.data_column not in data.columns:
            raise CartesianValidateDataColumnNotFoundError(
                class_name=self.__class__.__name__,
                column_name="data_column",
                column_value=self.data_column,
            )
