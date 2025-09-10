"""Spec for ColorAxis of a Map Shape widget."""

from typing import Any

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.formatting.number import NumberFormatting
from engineai.sdk.dashboard.widgets.maps.enums import LegendPosition


class ColorAxis(AbstractFactory):
    """Spec for ColorAxis of a Map widget."""

    def __init__(
        self,
        *,
        position: LegendPosition = LegendPosition.BOTTOM,
        formatting: NumberFormatting | None = None,
    ) -> None:
        """Construct a ColorAxis for a Map Shape widget.

        Args:
            position: location of position
                relative to data, maps.
            formatting: formatting spec for value.
        """
        super().__init__()
        self._position = position
        self._formatting = formatting if formatting else NumberFormatting()

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "position": self._position.value,
            "formatting": self._formatting.build(),
        }
