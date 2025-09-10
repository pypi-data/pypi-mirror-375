"""Specs for dashboard Route."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from typing_extensions import Unpack
from typing_extensions import override

from engineai.sdk.dashboard.dashboard.page.dependency import RouteDatastoreDependency
from engineai.sdk.dashboard.data.manager.manager import DataType
from engineai.sdk.dashboard.data.manager.manager import DependencyManager
from engineai.sdk.dashboard.interface import RouteInterface
from engineai.sdk.dashboard.links.route_link import RouteLink
from engineai.sdk.dashboard.selected import Selected

if TYPE_CHECKING:
    import pandas as pd

    from engineai.sdk.dashboard.abstract.typing import PrepareParams
    from engineai.sdk.dashboard.base import DependencyInterface


class _Selected(Selected["Route", RouteLink, "Route"]):  # type: ignore[type-var]
    """Route Selected property configuration."""


class Route(DependencyManager, RouteInterface):
    """Specs for dashboard Route."""

    _DEPENDENCY_ID = "__ROUTE__"

    def __init__(
        self,
        data: DataType | pd.DataFrame,
        *,
        query_parameter: str,
    ) -> None:
        """Constructor for dashboard Route.

        Args:
            data: data for the widget. Can be a
                pandas dataframe or Storage object if the data is to be retrieved
                from a storage.
            query_parameter: parameter that will be used to apply url queries.
        """
        super().__init__(data=data)
        self.__query_parameter = query_parameter
        self.__dependency: RouteDatastoreDependency = RouteDatastoreDependency(
            query_parameter=query_parameter,
            dependency_id=f"{self.dependency_id}{query_parameter}",
        )
        self.selected = _Selected(component=self)
        self._route_data_dependency: DependencyInterface | None = None

    @property
    @override
    def data_id(self) -> str:
        """Returns data id."""
        return "route"

    @property
    @override
    def query_parameter(self) -> str:
        """Query parameter."""
        return self.__query_parameter

    def prepare(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepare page routing."""
        self._prepare_dependencies(**kwargs)
        if self.dependencies:
            self._route_data_dependency = next(
                iter(self.dependencies)
            )  # Will always be one dependency
            self._route_data_dependency.prepare(self.__dependency.dependency_id)

    def validate(self, data: pd.DataFrame, **_: Any) -> None:
        """Page routing has no validations to do."""

    @property
    def dependency(self) -> list[RouteDatastoreDependency | DependencyInterface]:
        """Returns dependency."""
        dependencies: list[RouteDatastoreDependency | DependencyInterface] = [
            self.__dependency
        ]
        if self._route_data_dependency is not None:
            dependencies.append(self._route_data_dependency)
        return dependencies

    @override
    def build(self) -> dict[str, Any]:
        """Build Item."""
        # TODO: Need to validate if we can remove this method.
        return {}
