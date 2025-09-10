"""Spec for MapSryling of a Map Geo widget."""

from typing import Any

from engineai.sdk.dashboard.base import AbstractFactory

from .label import MapStylingLabel


class MapStyling(AbstractFactory):
    """Spec for MapStyling of a Map Geo widget."""

    def __init__(self, *, label: MapStylingLabel | None = None) -> None:
        """Construct a Styling for a Map Geo widget.

        Args:
            label: label style for map
        """
        super().__init__()
        self._label = label if label is not None else MapStylingLabel()

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "label": self._label.build(),
        }
