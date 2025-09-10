"""Dashboard management."""

from dataclasses import dataclass
from typing import Any

from engineai.sdk.api.graphql_client import GraphQLClient


@dataclass
class Dashboard:
    """Represents a dashboard in Engine AI's platform.

    Args:
        dashboard_id (str): Unique identifier for the dashboard.
        slug (str): URL-friendly identifier for the dashboard.
        name (str): Human-readable name of the dashboard.
        active_version (str | None): Version string of the currently active
            dashboard version.
    """

    dashboard_id: str
    slug: str
    name: str
    active_version: str | None = None


class DashboardAPI:
    """API client for managing dashboards within apps.

    This class provides methods to list and create dashboards
    within apps.
    """

    def __init__(self, graphql_client: GraphQLClient) -> None:
        """Initialize the DashboardAPI.

        Args:
            graphql_client (GraphQLClient): The GraphQL client instance to use
                for requests.
        """
        self._graphql_client = graphql_client

    def _extract_active_version(self, dashboard_data: dict[str, Any]) -> str | None:
        """Extract active version from dashboard data safely."""
        active_version = dashboard_data.get("activeVersion")
        return active_version.get("version") if active_version is not None else None

    def get_dashboard(
        self,
        workspace_slug: str,
        app_slug: str,
        dashboard_slug: str,
    ) -> Dashboard:
        """Retrieve a dashboard by its slug within an app.

        Args:
            workspace_slug (str): The slug of the workspace containing the app.
            app_slug (str): The slug of the app containing the dashboard.
            dashboard_slug (str): The slug of the dashboard to retrieve.

        Returns:
            Dashboard: The Dashboard object representing the requested dashboard.
        """
        content = self._graphql_client.request(
            query="""
                query Dashboard(
                    $workspaceSlug: String!
                    $appSlug: String!
                    $slug: String!
                ) {
                    dashboard(
                        workspaceSlug: $workspaceSlug
                        appSlug: $appSlug
                        slug: $slug
                    ) {
                        id
                        name
                        slug
                        activeVersion {
                            version
                        }
                    }
                }
            """,
            variables={
                "workspaceSlug": workspace_slug,
                "appSlug": app_slug,
                "slug": dashboard_slug,
            },
        )

        dashboard = content["data"]["dashboard"]

        return Dashboard(
            dashboard_id=dashboard["id"],
            slug=dashboard["slug"],
            name=dashboard["name"],
            active_version=self._extract_active_version(dashboard),
        )

    def list_app_dashboards(
        self,
        workspace_slug: str,
        app_slug: str,
    ) -> list[Dashboard]:
        """List all dashboards in an app.

        Args:
            workspace_slug (str): The slug of the workspace containing the app.
            app_slug (str): The slug of the app to list dashboards from.

        Returns:
            list[Dashboard]: A list of Dashboard objects in the specified app.
        """
        content = self._graphql_client.request(
            query="""
                query AppDashboards($appSlug: String!, $workspaceSlug: String!) {
                    app(appSlug: $appSlug, workspaceSlug: $workspaceSlug) {
                        dashboards(includeInactives: true) {
                            id
                            name
                            slug
                            activeVersion {
                                version
                            }
                        }
                    }
                }
            """,
            variables={"appSlug": app_slug, "workspaceSlug": workspace_slug},
        )

        return [
            Dashboard(
                dashboard_id=d["id"],
                slug=d["slug"],
                name=d["name"],
                active_version=self._extract_active_version(d),
            )
            for d in content["data"]["app"]["dashboards"]
        ]

    def create_dashboard(
        self,
        workspace_slug: str,
        app_slug: str,
        slug: str,
        name: str,
    ) -> Dashboard:
        """Create a new dashboard in an app.

        Args:
            workspace_slug (str): The slug of the workspace containing the app.
            app_slug (str): The slug of the app to create the dashboard in.
            slug (str): The URL-friendly identifier for the new dashboard.
            name (str): The human-readable name for the new dashboard.

        Returns:
            Dashboard: The created Dashboard object.
        """
        content = self._graphql_client.request(
            query="""
                mutation CreateDashboard($input: CreateDashboardInput!) {
                    createDashboard(input: $input) {
                        dashboard {
                            id
                            name
                            slug
                            activeVersion {
                                version
                            }
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "appSlug": app_slug,
                    "slug": slug,
                    "name": name,
                }
            },
        )

        dashboard = content["data"]["createDashboard"]["dashboard"]

        return Dashboard(
            dashboard_id=dashboard["id"],
            slug=dashboard["slug"],
            name=dashboard["name"],
            active_version=self._extract_active_version(dashboard),
        )

    def update_dashboard(
        self,
        workspace_slug: str,
        app_slug: str,
        dashboard_slug: str,
        new_dashboard_slug: str | None,
        new_dashboard_name: str | None,
    ) -> Dashboard:
        """Update an existing dashboard's slug and/or name.

        Args:
            workspace_slug (str): The slug identifier of the workspace
                containing the dashboard.
            app_slug (str): The slug identifier of the app containing the dashboard.
            dashboard_slug (str): The current slug identifier of the dashboard
                to update.
            new_dashboard_slug (str | None): The new slug for the dashboard.
            new_dashboard_name (str | None): The new name for the dashboard.

        Returns:
            Dashboard: The updated Dashboard object.
        """
        content = self._graphql_client.request(
            query="""
                mutation UpdateDashboard($input: UpdateDashboardInput!) {
                    updateDashboard(input: $input) {
                        dashboard {
                            id
                            name
                            slug
                            activeVersion {
                                version
                            }
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "appSlug": app_slug,
                    "slug": dashboard_slug,
                    "newSlug": new_dashboard_slug,
                    "name": new_dashboard_name,
                }
            },
        )

        dashboard = content["data"]["updateDashboard"]["dashboard"]

        return Dashboard(
            dashboard_id=dashboard["id"],
            slug=dashboard["slug"],
            name=dashboard["name"],
            active_version=self._extract_active_version(dashboard),
        )

    def trash_dashboard(
        self, workspace_slug: str, app_slug: str, dashboard_slug: str
    ) -> Dashboard:
        """Move a dashboard to the trash.

        Args:
            workspace_slug (str): The slug of the workspace containing the dashboard.
            app_slug (str): The slug of the app containing the dashboard.
            dashboard_slug (str): The slug of the dashboard to trash.

        Returns:
            Dashboard: The trashed Dashboard object.
        """
        content = self._graphql_client.request(
            query="""
                mutation TrashDashboard($input: TrashDashboardInput!) {
                    trashDashboard(input: $input) {
                        dashboard {
                            id
                            slug
                            name
                            activeVersion {
                                version
                            }
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "slug": dashboard_slug,
                    "appSlug": app_slug,
                    "workspaceSlug": workspace_slug,
                }
            },
        )

        dashboard = content["data"]["trashDashboard"]["dashboard"]

        return Dashboard(
            dashboard_id=dashboard["id"],
            slug=dashboard["slug"],
            name=dashboard["name"],
            active_version=self._extract_active_version(dashboard),
        )

    def restore_dashboard(
        self, workspace_slug: str, app_slug: str, dashboard_slug: str
    ) -> Dashboard:
        """Restore a trashed dashboard.

        Args:
            workspace_slug (str): The slug of the workspace containing the dashboard.
            app_slug (str): The slug of the app containing the dashboard.
            dashboard_slug (str): The slug of the dashboard to restore.

        Returns:
            Dashboard: The restored Dashboard object.
        """
        content = self._graphql_client.request(
            query="""
                mutation RestoreDashboard($input: RestoreDashboardInput!) {
                    restoreDashboard(input: $input) {
                        dashboard {
                            id
                            slug
                            name
                            activeVersion {
                                version
                            }
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "slug": dashboard_slug,
                    "appSlug": app_slug,
                    "workspaceSlug": workspace_slug,
                }
            },
        )

        dashboard = content["data"]["restoreDashboard"]["dashboard"]

        return Dashboard(
            dashboard_id=dashboard["id"],
            slug=dashboard["slug"],
            name=dashboard["name"],
            active_version=self._extract_active_version(dashboard),
        )

    def delete_dashboard(
        self, workspace_slug: str, app_slug: str, dashboard_slug: str
    ) -> bool:
        """Permanently delete a dashboard.

        Args:
            workspace_slug (str): The slug of the workspace containing the dashboard.
            app_slug (str): The slug of the app containing the dashboard.
            dashboard_slug (str): The slug of the dashboard to delete.

        Returns:
            bool: True if the dashboard was successfully deleted, False otherwise.
        """
        content = self._graphql_client.request(
            query="""
                mutation DeleteDashboard($input: DeleteDashboardInput!) {
                    deleteDashboard(input: $input) {
                        success
                    }
                }
            """,
            variables={
                "input": {
                    "slug": dashboard_slug,
                    "appSlug": app_slug,
                    "workspaceSlug": workspace_slug,
                }
            },
        )

        return bool(content["data"]["deleteDashboard"]["success"])
