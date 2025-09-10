"""SDK Dashboard Web Component Dependency."""

from collections.abc import Iterator
from typing import Any

from engineai.sdk.dashboard.base import DependencyInterface


class WebComponentDependency(DependencyInterface):
    """Web Component Dependency."""

    _INPUT_KEY = "webComponent"

    def __init__(self, path: list[str]) -> None:
        """Constructor for WebComponentDependency Class.

        Args:
            path: path to the web component data. Represents the path to the data
                injected by the web component, e.g. ['path', 'to', 'data'], where
                'data' is the field to be used.
        """
        self.__field: str | None = path.pop(-1) if len(path) >= 2 else None
        self.__path = path
        self.__dependency_id = f"web_component_{'_'.join(path)}"

    def __str__(self) -> str:
        return (
            f"{{{{{self.dependency_id}.{self.__field}}}}}"
            if self.__field is not None
            else f"{{{{{self.dependency_id}}}}}"
        )

    def __iter__(self) -> Iterator[tuple[str, str]]:
        yield "dependency_id", self.__dependency_id
        yield "field", self.__field or ""

    def __hash__(self) -> int:
        return hash(self.__dependency_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WebComponentDependency):
            return False
        return self.__dependency_id == other.dependency_id

    @property
    def dependency_id(self) -> str:
        """Returns dependency id."""
        return self.__dependency_id

    @property
    def field(self) -> str:
        """Returns field."""
        return self.__field or ""

    def build_item(self) -> dict[str, Any]:
        """Build item."""
        return {
            "name": self.__dependency_id,
            "path": ".".join(self.__path),
        }

    def build(self) -> dict[str, Any]:
        """Method to build specs."""
        return self.build_item()
