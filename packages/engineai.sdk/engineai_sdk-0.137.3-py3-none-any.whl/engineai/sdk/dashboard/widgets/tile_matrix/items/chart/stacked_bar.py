"""Spec for Tile Matrix Widget Stacked Bar Chart Item."""

from typing import Any

from engineai.sdk.dashboard.formatting.number import NumberFormatting
from engineai.sdk.dashboard.styling.color.palette import Palette
from engineai.sdk.dashboard.templated_string import DataField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.widgets.components.items.styling import (
    StackedBarChartItemStyling,
)

from ..typing import Actions
from .base import BaseTileMatrixChartItem


class StackedBarChartItem(BaseTileMatrixChartItem):
    """Spec for Tile Matrix Stacked Bar Chart Item."""

    _API_CHART_TYPE = "stackedBar"

    def __init__(
        self,
        *,
        data_column: TemplatedStringItem,
        label: TemplatedStringItem | DataField | None = None,
        icon: TemplatedStringItem | DataField | None = None,
        bar_label_column: TemplatedStringItem | None = None,
        link: Actions | None = None,
        formatting: NumberFormatting | None = None,
        styling: Palette | StackedBarChartItemStyling | None = None,
    ) -> None:
        """Construct spec for the TileMatrixStackedBarChartItem class.

        Args:
            data_column: column that has the value to be represented.
            label: Label text to be displayed.
            icon: icon to be displayed.
            bar_label_column: column in data that will
                have the labels used by each bar.
            link: link or action to be executed in the URL Icon.
            formatting: formatting spec.
            styling: styling spec.
        """
        super().__init__(
            data_column=data_column,
            label=label,
            icon=icon,
            link=link,
            formatting=formatting or NumberFormatting(),
            styling=(
                StackedBarChartItemStyling(color_spec=styling)
                if isinstance(styling, Palette)
                else StackedBarChartItemStyling()
                if styling is None
                else styling
            ),
        )
        self.__bar_label_column = bar_label_column

    def _build_extra_chart_inputs(self) -> dict[str, Any]:
        """Build extra inputs for the chart."""
        return {"barLabelKey": build_templated_strings(items=self.__bar_label_column)}
