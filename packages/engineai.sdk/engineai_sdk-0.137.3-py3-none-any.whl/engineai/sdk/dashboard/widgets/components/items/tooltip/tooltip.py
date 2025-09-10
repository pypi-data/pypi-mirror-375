"""Specs for chart tooltip."""

from typing import Any

import pandas as pd

from engineai.sdk.dashboard.formatting.text import TextFormatting
from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.templated_string import DataField
from engineai.sdk.dashboard.widgets.components.charts.tooltip.base import (
    TooltipItemFormatter,
)

from .header import HeaderTooltip


class ChartTooltip(AbstractFactoryLinkItemsHandler):
    """Specs for number item for a tooltip."""

    def __init__(
        self,
        title: str | DataField,
        formatting: TooltipItemFormatter | None = None,
    ) -> None:
        """Construct for ChartTooltip class.

        Args:
            title (Union[str, DataField]): header title spec.
            formatting (Optional[TooltipItemFormatter]): header tooltip formatting.
        """
        super().__init__()
        self._header = HeaderTooltip(
            title=title,
            formatting=formatting or TextFormatting(),
        )

    def validate(
        self,
        data: pd.DataFrame | dict[str, Any],
        item_id_key: str | None = None,
    ) -> None:
        """Validate tooltip data dependencies.

        Args:
            data (Union[pd.DataFrame, Dict[str, Any]]): pandas DataFrame or dict where
                the data is present.
            item_id_key: Optional[str]: key in data (if using data as dict) used to
                identify the data that feeds this item.
        """
        self._header.validate(data=data, item_id_key=item_id_key)

    def build(self) -> dict[str, Any]:
        """Builds spec for dashboard API.

        Returns:
            Any: Input object for Dashboard API
        """
        return {
            "header": self._header.build(),
        }
