"""App management."""

from dataclasses import dataclass

from engineai.sdk.api.graphql_client import GraphQLClient


@dataclass
class App:
    """Represents an app in Engine AI's platform.

    Args:
        app_id (str): Unique identifier for the app.
        slug (str): URL-friendly identifier for the app.
        name (str): Human-readable name of the app.
    """

    app_id: str
    slug: str
    name: str


class AppAPI:
    """API client for managing apps within workspaces.

    This class provides methods to list, create, and update apps
    within a workspace.
    """

    def __init__(self, graphql_client: GraphQLClient) -> None:
        """Initialize the AppAPI.

        Args:
            graphql_client (GraphQLClient): The GraphQL client instance to use for
                requests.
        """
        self._graphql_client = graphql_client

    def get_app(self, workspace_slug: str, app_slug: str) -> App:
        """Retrieve an app by its slug within a workspace.

        Args:
            workspace_slug (str): The slug of the workspace containing the app.
            app_slug (str): The slug of the app to retrieve.

        Returns:
            App: The App object representing the requested app.
        """
        content = self._graphql_client.request(
            query="""
                    query App($appSlug: String!, $workspaceSlug: String!) {
                        app(appSlug: $appSlug, workspaceSlug: $workspaceSlug) {
                            id
                            slug
                            name
                        }
                    }
                """,
            variables={
                "appSlug": app_slug,
                "workspaceSlug": workspace_slug,
            },
        )

        app = content["data"]["app"]
        return App(
            app_id=app["id"],
            slug=app["slug"],
            name=app["name"],
        )

    def list_workspace_apps(self, workspace_slug: str) -> list[App]:
        """List all apps in a workspace.

        Args:
            workspace_slug (str): The slug of the workspace to list apps from.

        Returns:
            list[App]: A list of App objects in the specified workspace.
        """
        content = self._graphql_client.request(
            query="""
                query WorkspaceApps($slug: String!) {
                    workspace(slug: $slug) {
                        apps {
                            id
                            slug
                            name
                        }
                    }
                }
            """,
            variables={"slug": workspace_slug},
        )

        return [
            App(app_id=a["id"], slug=a["slug"], name=a["name"])
            for a in content["data"]["workspace"]["apps"]
        ]

    def create_app(self, workspace_slug: str, slug: str, name: str) -> App:
        """Create a new app in a workspace.

        Args:
            workspace_slug (str): The slug of the workspace to create the app in.
            slug (str): The URL-friendly identifier for the new app.
            name (str): The human-readable name for the new app.

        Returns:
            App: The created App object.
        """
        content = self._graphql_client.request(
            query="""
                mutation CreateApp($input: CreateAppInput!) {
                    createApp(input: $input) {
                        app {
                            id
                            slug
                            name
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "slug": slug,
                    "name": name,
                }
            },
        )

        app = content["data"]["createApp"]["app"]

        return App(app_id=app["id"], slug=app["slug"], name=app["name"])

    def update_app(
        self,
        workspace_slug: str,
        app_slug: str,
        new_app_slug: str | None,
        new_app_name: str | None,
    ) -> App:
        """Update an existing app's properties.

        Args:
            workspace_slug (str): The slug of the workspace containing the app.
            app_slug (str): The current slug of the app to update.
            new_app_slug (str | None): The new slug for the app (optional).
            new_app_name (str | None): The new name for the app (optional).

        Returns:
            App: The updated App object.
        """
        content = self._graphql_client.request(
            query="""
                mutation UpdateApp($input: UpdateAppInput!) {
                    updateApp(input: $input) {
                        app {
                            id
                            slug
                            name
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "slug": app_slug,
                    "newSlug": new_app_slug,
                    "name": new_app_name,
                }
            },
        )

        app = content["data"]["updateApp"]["app"]

        return App(app_id=app["id"], slug=app["slug"], name=app["name"])

    def trash_app(self, workspace_slug: str, app_slug: str) -> App:
        """Move an app to the trash.

        Args:
            workspace_slug (str): The slug of the workspace containing the app.
            app_slug (str): The slug of the app to move to trash.

        Returns:
            App: The App object representing the trashed app.
        """
        content = self._graphql_client.request(
            query="""
                mutation TrashApp($input: TrashAppInput!) {
                    trashApp(input: $input) {
                        app {
                            id
                            slug
                            name
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "slug": app_slug,
                    "workspaceSlug": workspace_slug,
                }
            },
        )

        app = content["data"]["trashApp"]["app"]

        return App(app_id=app["id"], slug=app["slug"], name=app["name"])

    def restore_app(self, workspace_slug: str, app_slug: str) -> App:
        """Restore a trashed app.

        Args:
            workspace_slug (str): The slug of the workspace containing the app.
            app_slug (str): The slug of the app to restore.

        Returns:
            App: The restored App object.
        """
        content = self._graphql_client.request(
            query="""
                mutation RestoreApp($input: RestoreAppInput!) {
                    restoreApp(input: $input) {
                        app {
                            id
                            slug
                            name
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "slug": app_slug,
                    "workspaceSlug": workspace_slug,
                }
            },
        )

        app = content["data"]["restoreApp"]["app"]
        return App(app_id=app["id"], slug=app["slug"], name=app["name"])

    def delete_app(self, workspace_slug: str, app_slug: str) -> bool:
        """Permanently delete an app.

        Args:
            workspace_slug (str): The slug of the workspace containing the app.
            app_slug (str): The slug of the app to delete.

        Returns:
            bool: True if the app was successfully deleted, False otherwise.
        """
        content = self._graphql_client.request(
            query="""
                mutation DeleteApp($input: DeleteAppInput!) {
                    deleteApp(input: $input) {
                        success
                    }
                }
            """,
            variables={
                "input": {
                    "slug": app_slug,
                    "workspaceSlug": workspace_slug,
                }
            },
        )

        return bool(content["data"]["deleteApp"]["success"])
