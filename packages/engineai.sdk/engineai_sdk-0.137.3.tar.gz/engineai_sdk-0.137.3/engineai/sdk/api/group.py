"""Group management."""

from dataclasses import dataclass

from engineai.sdk.api.graphql_client import GraphQLClient


@dataclass
class Group:
    """Represents a group in Engine AI's platform.

    Args:
        group_id (str): Unique identifier for the group.
        name (str): Name of the group.
    """

    group_id: str
    name: str


class GroupAPI:
    """API client for managing groups within workspaces.

    This class provides methods to list, create, update, and delete groups
    within workspaces.
    """

    def __init__(self, graphql_client: GraphQLClient) -> None:
        """Initialize the GroupAPI.

        Args:
            graphql_client (GraphQLClient): The GraphQL client instance to use
                for requests.
        """
        self._graphql_client = graphql_client

    def list_workspace_groups(self, workspace_slug: str) -> list[Group]:
        """List all groups in a workspace.

        Args:
            workspace_slug (str): The slug of the workspace to list groups from.

        Returns:
            list[Group]: A list of Group objects in the specified workspace.
        """
        content = self._graphql_client.request(
            query="""
                query WorkspaceGroups($slug: String!) {
                    workspace(slug: $slug) {
                        groups {
                            id
                            slug
                        }
                    }
                }
            """,
            variables={"slug": workspace_slug},
        )

        return [
            Group(group_id=g["id"], name=g["slug"])
            for g in content["data"]["workspace"]["groups"]
        ]

    def create_group(self, workspace_slug: str, name: str) -> Group:
        """Create a new group in a workspace.

        Args:
            workspace_slug (str): The slug of the workspace to create the group in.
            name (str): The name/slug for the new group.

        Returns:
            Group: The created Group object.
        """
        content = self._graphql_client.request(
            query="""
                mutation CreateGroup($input: CreateGroupInput!) {
                    createGroup(input: $input) {
                        group {
                            id
                            slug
                        }
                    }
                }
            """,
            variables={"input": {"slug": name, "workspaceSlug": workspace_slug}},
        )

        group = content["data"]["createGroup"]["group"]

        return Group(group_id=group["id"], name=group["slug"])

    def update_group(self, workspace_slug: str, name: str, new_name: str) -> Group:
        """Update an existing group's name.

        Args:
            workspace_slug (str): The slug of the workspace containing the group.
            name (str): The current name of the group to update.
            new_name (str): The new name for the group.

        Returns:
            Group: The updated Group object.
        """
        content = self._graphql_client.request(
            query="""
                mutation UpdateGroup($input: UpdateGroupInput!) {
                    updateGroup(input: $input) {
                        group {
                            id
                            slug
                        }
                    }
                }""",
            variables={
                "input": {
                    "slug": name,
                    "newSlug": new_name,
                    "workspaceSlug": workspace_slug,
                }
            },
        )

        group = content["data"]["updateGroup"]["group"]

        return Group(group_id=group["id"], name=group["slug"])

    def delete_group(self, workspace_slug: str, name: str) -> bool:
        """Delete a group from a workspace.

        Args:
            workspace_slug (str): The slug of the workspace containing the group.
            name (str): The name of the group to delete.

        Returns:
            bool: True if the group was successfully deleted, False otherwise.
        """
        content = self._graphql_client.request(
            query="""
                mutation DeleteGroup($input: DeleteGroupInput!) {
                    deleteGroup(input: $input) {
                        success
                    }
                }
            """,
            variables={"input": {"slug": name, "workspaceSlug": workspace_slug}},
        )

        return bool(content["data"]["deleteGroup"]["success"])
