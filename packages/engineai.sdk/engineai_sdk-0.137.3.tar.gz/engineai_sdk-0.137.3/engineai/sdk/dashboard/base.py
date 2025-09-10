"""Top-level package for Dashboard factories."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from typing_extensions import override

HEIGHT_ROUND_VALUE = 2


class AbstractFactory(ABC):
    """Abstract Class implemented by all factories."""

    @abstractmethod
    def build(self) -> dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """


class DependencyInterface(AbstractFactory, ABC):
    """Generic interface for dependencies."""

    _INPUT_KEY: str | None = None

    @property
    def input_key(self) -> str:
        """Input Key."""
        if self._INPUT_KEY is None:
            msg = f"Class {self.__class__.__name__}._INPUT_KEY not defined."
            raise NotImplementedError(msg)
        return self._INPUT_KEY

    def prepare(self, _: str) -> None:
        """Prepare dependency."""
        return


class AbstractLink(ABC):
    """Abstract class to implement links."""

    @override
    def __str__(self) -> str:
        return self._generate_templated_string()

    @property
    def link_component(self) -> Any:
        """Return link component.

        Widget for WidgetField
        Route for RouteLink
        """
        return None

    @property
    @abstractmethod
    def dependency(self) -> DependencyInterface:
        """Return DependencyInterface."""

    @abstractmethod
    def _generate_templated_string(self, *, selection: int = 0) -> str:
        """Generates template string to be used in dependency."""
