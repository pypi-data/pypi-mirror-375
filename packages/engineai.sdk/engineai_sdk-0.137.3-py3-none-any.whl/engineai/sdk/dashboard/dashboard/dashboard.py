"""Spec for a Dashboard."""

from __future__ import annotations

from .version.version import DashboardVersion
from .version.version import DashboardVersionContent


class Dashboard:
    """Central component for managing layouts, widgets, cards.

    The Dashboard class is the central component for creating
    and managing dashboards. It serves as the container for various
    layout elements, widgets, and cards.
    """

    def __init__(
        self,
        *,
        workspace_slug: str,
        app_slug: str,
        slug: str,
        content: DashboardVersionContent,
        activate: bool = True,
    ) -> None:
        """Constructor for Dashboard class.

        Args:
            workspace_slug (str): The workspace's identifier.
            app_slug (str): The app's identifier.
            slug (str): The dashboard's identifier.
            content (DashboardVersionContent): The content of the dashboard version.
            activate (bool): Whether to activate the dashboard version immediately after
                creation or not.
        """
        self.workspace_slug: str = workspace_slug
        self.app_slug: str = app_slug
        self.slug: str = slug
        self.__version = DashboardVersion(
            workspace_slug=self.workspace_slug,
            app_slug=self.app_slug,
            dashboard_slug=self.slug,
            content=content,
            activate=activate,
        )
        self.__version.create_dashboard_version()
