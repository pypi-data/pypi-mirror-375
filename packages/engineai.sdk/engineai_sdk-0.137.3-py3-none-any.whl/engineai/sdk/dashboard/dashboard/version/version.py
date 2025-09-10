"""Dashboard version class."""

from __future__ import annotations

import sys
from typing import Any
from typing import TypeAlias

from typing_extensions import override

from engineai.sdk.api.auth import get_auth_token
from engineai.sdk.api.client import api_client
from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.dashboard.page.page import Page
from engineai.sdk.dashboard.dashboard.page.page import PageContent

DashboardVersionContentStrict = Page
DashboardVersionContent: TypeAlias = DashboardVersionContentStrict | PageContent


class DashboardVersion(AbstractFactory):
    """Spec for Dashboard version."""

    def __init__(
        self,
        workspace_slug: str,
        app_slug: str,
        dashboard_slug: str,
        content: DashboardVersionContent,
        activate: bool,
    ) -> None:
        """Constructor for DashboardVersion class.

        Args:
            workspace_slug (str): The workspace's identifier.
            app_slug (str): The app's identifier.
            dashboard_slug (str): The dashboard's identifier.
            content (DashboardVersionContent): The content of the dashboard version.
            activate (bool): Whether to activate the dashboard version immediately after
                creation or not.
        """
        self.workspace_slug: str = workspace_slug
        self.app_slug: str = app_slug
        self.dashboard_slug: str = dashboard_slug
        self.content: DashboardVersionContentStrict = (
            content
            if isinstance(content, DashboardVersionContentStrict)
            else Page(content=content)
        )
        self.activate = activate

    def create_dashboard_version(self) -> None:
        """Create dashboard version in API."""
        self.prepare()
        self.validate()
        dashboard_input = self.build()
        dashboard_version = api_client.dashboard_version.create_dashboard_version(
            **dashboard_input
        )

        platform_url = (
            get_auth_token()["base_url"]
            .replace("api.", "platform.")
            .replace("http://localhost:4000", "https://localhost:3000")
        )

        dashboard_version_url = (
            f"{platform_url}/preview/workspaces/{self.workspace_slug}/apps/{self.app_slug}/"
            f"dashboards/{self.dashboard_slug}?dashboard-version={dashboard_version.version}"
        )

        if self.activate:
            api_client.dashboard_version.activate_dashboard_version(
                workspace_slug=self.workspace_slug,
                app_slug=self.app_slug,
                dashboard_slug=self.dashboard_slug,
                version=dashboard_version.version,
            )
            msg = (
                f"Dashboard version {dashboard_version.version} has been published and "
                "activated."
            )
        else:
            msg = (
                f"Dashboard version {dashboard_version.version} has been published "
                "but not activated. "
                "To activate it, please use the URL below:"
            )

        sys.stdout.write(f"\n{msg}\n")
        sys.stdout.write(f"\nURL: {dashboard_version_url}\n")

        if not self.activate:
            sys.stdout.write(
                "\nOr run this command:\n"
                f"engineai dashboard activate {self.workspace_slug} {self.app_slug} "
                f"{self.dashboard_slug} {dashboard_version.version}\n"
            )

    def prepare(self) -> None:
        """Prepares the dashboard version content."""
        self.content.prepare(dashboard_slug=self.dashboard_slug)

    def validate(self) -> None:
        """Validates the dashboard version content."""
        self.content.validate()

    @override
    def build(self) -> dict[str, Any]:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API

        Raises:
            AttributeError: if widgets were added to dashboards but not to layout, or
                vice-versa.
        """
        return {
            "workspace_slug": self.workspace_slug,
            "app_slug": self.app_slug,
            "dashboard_slug": self.dashboard_slug,
            "layout": {"page": self.content.build()},
        }
