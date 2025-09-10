"""Spec for legend of a categorical widget."""

from typing import Any

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.enum.legend_position import LegendPosition


class Legend(AbstractFactory):
    """Spec for legend of a categorical widget.

    Args:
        position: location of position relative to data, charts.
    """

    def __init__(self, *, position: LegendPosition = LegendPosition.BOTTOM) -> None:
        """Construct a legend for a categorical widget."""
        super().__init__()
        self.__position = position

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {"position": self.__position.value}
