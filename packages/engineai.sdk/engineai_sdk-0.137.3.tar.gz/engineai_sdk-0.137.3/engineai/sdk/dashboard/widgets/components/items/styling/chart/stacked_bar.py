"""Spec for Widget Stacked Bar Chart Styling."""

from typing import Any

from engineai.sdk.dashboard.widgets.components.items.styling.base import BaseItemStyling


class StackedBarChartItemStyling(BaseItemStyling):
    """Spec for styling used by Stacked Bar Chart Item."""

    def _build_extra_inputs(self) -> dict[str, Any]:
        return {"showTotalOnTooltip": False}
