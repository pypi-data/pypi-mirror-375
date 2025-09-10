"""Country base styling for tooltip items."""

from abc import abstractmethod
from typing import Any


class CountryTooltipItemStylingBase:
    """Country base styling for tooltip items."""

    _INPUT_KEY: str | None = None

    @property
    def _input_key(self) -> str:
        """Returns styling Input Key argument value."""
        if self._INPUT_KEY is None:
            msg = f"Class {self.__class__.__name__}._INPUT_KEY not defined."
            raise NotImplementedError(msg)
        return self._INPUT_KEY

    @abstractmethod
    def _build_styling(self) -> Any:
        """Method to build styling."""

    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            self._input_key: self._build_styling(),
        }
