"""Dashboard version management."""

from dataclasses import dataclass
from typing import Any

from engineai.sdk.api.graphql_client import GraphQLClient


@dataclass
class DashboardVersion:
    """Represents a version of a dashboard.

    Args:
        dashboard_version_id (str): Unique identifier for the dashboard version.
        version (str): Version string identifier.
        active (bool): Whether this version is currently active.
    """

    dashboard_version_id: str
    version: str
    active: bool


class DashboardVersionAPI:
    """API client for managing dashboard versions.

    This class provides methods to list, create, activate, and deactivate
    dashboard versions.
    """

    def __init__(self, graphql_client: GraphQLClient) -> None:
        """Initialize the DashboardVersionAPI.

        Args:
            graphql_client (GraphQLClient): The GraphQL client instance to use for
                requests.
        """
        self._graphql_client = graphql_client

    def list_dashboard_versions(
        self,
        workspace_slug: str,
        app_slug: str,
        dashboard_slug: str,
    ) -> list[DashboardVersion]:
        """List all versions of a dashboard.

        Args:
            workspace_slug (str): The slug of the workspace containing the dashboard.
            app_slug (str): The slug of the app containing the dashboard.
            dashboard_slug (str): The slug of the dashboard to list versions for.

        Returns:
            list[DashboardVersion]: A list of DashboardVersion objects for the
                specified dashboard.
        """
        content = self._graphql_client.request(
            query="""
                query DashboardVersions(
                    $workspaceSlug: String!, $appSlug: String!, $slug: String!
                ) {
                    dashboard(
                        workspaceSlug: $workspaceSlug, appSlug: $appSlug, slug: $slug
                    ) {
                        versions {
                            id
                            version
                            active
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

        return [
            DashboardVersion(
                dashboard_version_id=dv["id"],
                version=dv["version"],
                active=bool(dv["active"]),
            )
            for dv in content["data"]["dashboard"]["versions"]
        ]

    def create_dashboard_version(
        self,
        workspace_slug: str,
        app_slug: str,
        dashboard_slug: str,
        layout: dict[str, Any],
    ) -> DashboardVersion:
        """Create a new version of a dashboard.

        Args:
            workspace_slug (str): The slug of the workspace containing the dashboard.
            app_slug (str): The slug of the app containing the dashboard.
            dashboard_slug (str): The slug of the dashboard to create a version for.
            layout (dict[str, Any]): The layout configuration for the new dashboard
                version.

        Returns:
            DashboardVersion: The created DashboardVersion object.
        """
        content = self._graphql_client.request(
            query="""
                mutation CreateDashboardVersion($input: CreateDashboardVersionInput!) {
                    createDashboardVersion(input: $input) {
                        dashboardVersion {
                            id
                            active
                            version
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "appSlug": app_slug,
                    "dashboardSlug": dashboard_slug,
                    "layout": layout,
                }
            },
        )

        dashboard_version = content["data"]["createDashboardVersion"][
            "dashboardVersion"
        ]

        return DashboardVersion(
            dashboard_version_id=dashboard_version["id"],
            version=dashboard_version["version"],
            active=bool(dashboard_version["active"]),
        )

    def activate_dashboard_version(
        self,
        workspace_slug: str,
        app_slug: str,
        dashboard_slug: str,
        version: str,
    ) -> DashboardVersion:
        """Activate a specific version of a dashboard.

        Args:
            workspace_slug (str): The slug of the workspace containing the dashboard.
            app_slug (str): The slug of the app containing the dashboard.
            dashboard_slug (str): The slug of the dashboard.
            version (str): The version string to activate.

        Returns:
            DashboardVersion: The activated DashboardVersion object.
        """
        content = self._graphql_client.request(
            query="""
                mutation ActivateDashboardVersion(
                    $input: ActivateDashboardVersionInput!
                ) {
                    activateDashboardVersion(input: $input) {
                        dashboardVersion {
                            id
                            active
                            version
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "appSlug": app_slug,
                    "dashboardSlug": dashboard_slug,
                    "versionSlug": version,
                }
            },
        )

        dashboard_version = content["data"]["activateDashboardVersion"][
            "dashboardVersion"
        ]

        return DashboardVersion(
            dashboard_version_id=dashboard_version["id"],
            version=dashboard_version["version"],
            active=bool(dashboard_version["active"]),
        )

    def deactivate_dashboard_version(
        self,
        workspace_slug: str,
        app_slug: str,
        dashboard_slug: str,
        version: str,
    ) -> DashboardVersion:
        """Deactivate a specific version of a dashboard.

        Args:
            workspace_slug (str): The slug of the workspace containing the dashboard.
            app_slug (str): The slug of the app containing the dashboard.
            dashboard_slug (str): The slug of the dashboard.
            version (str): The version string to deactivate.

        Returns:
            DashboardVersion: The deactivated DashboardVersion object.
        """
        content = self._graphql_client.request(
            query="""
                mutation DeactivateDashboardVersion(
                    $input: DeactivateDashboardVersionInput!
                ) {
                    deactivateDashboardVersion(input: $input) {
                        dashboardVersion {
                            id
                            active
                            version
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "appSlug": app_slug,
                    "dashboardSlug": dashboard_slug,
                    "versionSlug": version,
                }
            },
        )

        dashboard_version = content["data"]["deactivateDashboardVersion"][
            "dashboardVersion"
        ]

        return DashboardVersion(
            dashboard_version_id=dashboard_version["id"],
            version=dashboard_version["version"],
            active=bool(dashboard_version["active"]),
        )

    def delete_dashboard_version(
        self,
        workspace_slug: str,
        app_slug: str,
        dashboard_slug: str,
        version: str,
    ) -> bool:
        """Delete a dashboard version.

        Args:
            workspace_slug (str): The slug of the workspace containing the dashboard.
            app_slug (str): The slug of the app containing the dashboard.
            dashboard_slug (str): The slug of the dashboard.
            version (str): The version string to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        content = self._graphql_client.request(
            query="""
                mutation DeleteDashboardVersion($input: DeleteDashboardVersionInput!) {
                    deleteDashboardVersion(input: $input) {
                        success
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "appSlug": app_slug,
                    "dashboardSlug": dashboard_slug,
                    "versionSlugs": [version],
                }
            },
        )

        return bool(content["data"]["deleteDashboardVersion"]["success"])
