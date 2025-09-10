"""DashboardPage spec."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import TypeAlias

from typing_extensions import Unpack

from engineai.sdk.dashboard.abstract.selectable_widgets import AbstractSelectWidget
from engineai.sdk.dashboard.base import DependencyInterface
from engineai.sdk.dashboard.dashboard.page.dependency import RouteDatastoreDependency
from engineai.sdk.dashboard.links.route_link import RouteLink
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.widgets.base import Widget

from .root import RootGrid
from .root import RootGridItem
from .route import Route

if TYPE_CHECKING:
    from engineai.sdk.dashboard.abstract.typing import PrepareParams


PageContentStrict = RootGrid
PageContent: TypeAlias = PageContentStrict | RootGridItem | list[RootGridItem]


class Page:
    """Provides a flexible way to structure dashboard content."""

    def __init__(
        self,
        *,
        content: PageContent,
        title: TemplatedStringItem | None = None,
        route: Route | None = None,
        description: str | None = None,
    ) -> None:
        """Constructor for Page.

        Args:
            content: Dashboard content.
            title: Dashboard title to be displayed.
            route: Route for the page.
            description: page description.
        """
        self.grid: PageContentStrict = (
            content
            if isinstance(content, PageContentStrict)
            else RootGrid(*content)
            if isinstance(content, list)
            else RootGrid(content)
        )
        self.title: TemplatedStringItem | None = title
        self.route = route
        self.description: str | None = description

    def validate(self) -> None:
        """Validates the page content, by checking for duplicate widget IDs.

        This method raises a ValueError if any widget ID is duplicated within the page.

        Also, if the widget has JSON data, it validates the widget spec, based on the
            data received.
        """
        layout_widgets: set[str] = set()

        for widget in self.grid.items():
            if isinstance(widget, Widget):
                if widget.widget_id in layout_widgets:
                    msg = (
                        f"Widget with id '{widget.widget_id}' "
                        f"already exists in the layout."
                    )
                    raise ValueError(msg)
                layout_widgets.add(widget.widget_id)
                if widget.validation_data is not None:
                    widget.validate(data=widget.validation_data)

    def prepare(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepare layout for building."""
        kwargs["selectable_widgets"] = {
            w.widget_id: w
            for w in self.grid.items()
            if isinstance(w, AbstractSelectWidget)
        }
        kwargs["page"] = self
        self.grid.prepare_heights()
        self.grid.prepare(**kwargs)

        if self.route is not None:
            self.route.prepare(**kwargs)

    def __build_dependencies(self) -> list[dict[str, Any]]:
        dependencies: set[RouteDatastoreDependency | DependencyInterface] = set()
        if self.route is not None:
            for dependency in self.route.dependency:
                dependencies.add(dependency)

        if isinstance(self.title, list):
            for link in self.title:
                dependencies.add(link.dependency)
        elif self.title is not None and not isinstance(self.title, (str | RouteLink)):
            dependencies.add(self.title.dependency)

        return [
            {
                dependency.input_key: dependency.build(),
            }
            for dependency in dependencies
        ]

    def build(self) -> dict[str, Any]:
        """Builds spec for Dashboard Page."""
        return {
            "grid": self.grid.build(),
            "title": build_templated_strings(items=self.title),
            "description": self.description,
            "dependencies": self.__build_dependencies(),
        }
