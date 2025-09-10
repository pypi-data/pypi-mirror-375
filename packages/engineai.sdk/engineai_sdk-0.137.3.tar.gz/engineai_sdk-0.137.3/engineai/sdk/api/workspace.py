"""Workspace management."""

from dataclasses import dataclass

from engineai.sdk.api.graphql_client import GraphQLClient


@dataclass
class Workspace:
    """Represents a workspace in Engine AI's platform.

    Args:
        workspace_id (str): Unique identifier for the workspace
        slug (str): URL-friendly identifier for the workspace
        name (str): Human-readable name of the workspace
    """

    workspace_id: str
    slug: str
    name: str


class WorkspaceAPI:
    """API client for managing workspaces.

    This class provides methods to list, create, update, and delete
    workspaces in Engine AI's platform.
    """

    def __init__(self, graphql_client: GraphQLClient) -> None:
        """Initialize the WorkspaceAPI.

        Args:
            graphql_client (GraphQLClient): The GraphQL client instance to use
                for requests.
        """
        self._graphql_client = graphql_client

    def list_user_workspaces(self) -> list[Workspace]:
        """List all workspaces accessible to the current user.

        Returns:
            list[Workspace]: A list of Workspace objects accessible to the
                authenticated user
        """
        content = self._graphql_client.request(
            query="""
                query UserWorkspaces {
                    viewer {
                        workspaces {
                            id
                            slug
                            name
                        }
                    }
                }
            """
        )

        return [
            Workspace(workspace_id=w["id"], slug=w["slug"], name=w["name"])
            for w in content["data"]["viewer"]["workspaces"]
        ]

    def create_workspace(self, slug: str, name: str) -> Workspace:
        """Create a new workspace.

        Args:
            slug (str): The URL-friendly identifier for the new workspace
            name (str): The human-readable name for the new workspace

        Returns:
            Workspace: The created Workspace object
        """
        content = self._graphql_client.request(
            query="""
                mutation CreateWorkspace($input: CreateWorkspaceInput!) {
                    createWorkspace(input: $input) {
                        workspace {
                            id
                            slug
                            name
                        }
                    }
                }
            """,
            variables={"input": {"slug": slug, "name": name}},
        )

        workspace = content["data"]["createWorkspace"]["workspace"]

        return Workspace(
            workspace_id=workspace["id"], slug=workspace["slug"], name=workspace["name"]
        )

    def update_workspace(
        self, slug: str, new_slug: str | None = None, new_name: str | None = None
    ) -> Workspace:
        """Update an existing workspace's properties.

        Args:
            slug (str): The current slug of the workspace to update
            new_slug (str | None): The new slug for the workspace (optional)
            new_name (str | None): The new name for the workspace (optional)

        Returns:
            Workspace: The updated Workspace object
        """
        content = self._graphql_client.request(
            query="""
                mutation UpdateWorkspace($input: UpdateWorkspaceInput!) {
                    updateWorkspace(input: $input) {
                        workspace {
                            id
                            slug
                            name
                        }
                    }
                }
            """,
            variables={
                "input": {"slug": slug, "newSlug": new_slug, "newName": new_name},
            },
        )

        workspace = content["data"]["updateWorkspace"]["workspace"]

        return Workspace(
            workspace_id=workspace["id"], slug=workspace["slug"], name=workspace["name"]
        )

    def delete_workspace(self, slug: str) -> bool:
        """Delete a workspace.

        Args:
            slug (str): The slug of the workspace to delete

        Returns:
            bool: True if the workspace was successfully deleted, False otherwise
        """
        content = self._graphql_client.request(
            query="""
                mutation DeleteWorkspace($input: DeleteWorkspaceInput!) {
                    deleteWorkspace(input: $input) {
                        success
                    }
                }
            """,
            variables={"input": {"slug": slug}},
        )

        return bool(content["data"]["deleteWorkspace"]["success"])
