"""Spec for a Point Series of a Categorical widget."""

from typing import Any

import pandas as pd

from engineai.sdk.dashboard.links.typing import GenericLink
from engineai.sdk.dashboard.styling.color import Palette
from engineai.sdk.dashboard.widgets.components.charts.styling.point import (
    PointSeriesStyling,
)
from engineai.sdk.dashboard.widgets.components.charts.typing import TooltipItem

from .base import CategoricalBaseSeries


class PointSeries(CategoricalBaseSeries):
    """Spec for a Point Series of a Categorical widget."""

    _INPUT_KEY = "point"

    def __init__(
        self,
        *,
        data_column: str | GenericLink,
        name: str | GenericLink | None = None,
        styling: Palette | PointSeriesStyling | None = None,
        show_in_legend: bool = True,
        required: bool = True,
        visible: bool = True,
        tooltips: list[TooltipItem] | None = None,
    ) -> None:
        """Construct Point Series.

        Args:
            data_column: name of column in pandas dataframe(s) used for the values of
                this series for the Y Axis.
            name: series name (shown in legend and tooltip).
            styling: styling spec.
            show_in_legend: whether to show series in legend or not.
            required: Flag to make the Series mandatory. If required == True
                and no Data the widget will show an error. If required==False and no
                Data, the widget hides the Series.
            visible: Flag to make the Series visible when chart is loaded.
            tooltips: Tooltip items to show in the tooltip.
        """
        super().__init__(
            data_column=data_column,
            name=name,
            show_in_legend=show_in_legend,
            required=required,
            visible=visible,
            tooltips=tooltips,
        )
        self._styling = (
            PointSeriesStyling(color_spec=styling)
            if isinstance(styling, Palette)
            else styling
        )

    def validate(self, data: pd.DataFrame, **kwargs: Any) -> None:
        """Validate Point Series elements and Data.

        Args:
            data: Data associated with the Series.
            kwargs (Any): Additional keyword arguments.
        """
        super().validate(data=data, **kwargs)
        if self._styling:
            self._styling.validate(data=data)
