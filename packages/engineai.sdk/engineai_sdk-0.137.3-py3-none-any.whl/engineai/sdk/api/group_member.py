"""Group member management."""

from dataclasses import dataclass

from engineai.sdk.api.graphql_client import GraphQLClient


@dataclass
class GroupMember:
    """Represents a member of a group in Engine AI's platform.

    Args:
        user_id (str): Unique identifier for the user.
        first_name (str): User's first name.
        last_name (str): User's last name.
        email (str): User's email address.
    """

    user_id: str
    first_name: str
    last_name: str
    email: str


class GroupMemberAPI:
    """API client for managing group members.

    This class provides methods to list, add, and remove members
    from groups within workspaces.
    """

    def __init__(self, graphql_client: GraphQLClient) -> None:
        """Initialize the GroupMemberAPI.

        Args:
            graphql_client (GraphQLClient): The GraphQL client instance to use
                for requests.
        """
        self._graphql_client = graphql_client

    def list_group_members(
        self,
        workspace_slug: str,
        group_name: str,
    ) -> list[GroupMember]:
        """List all members of a group.

        Args:
            workspace_slug (str): The slug of the workspace containing the group.
            group_name (str): The name of the group to list members from.

        Returns:
            list[GroupMember]: A list of GroupMember objects in the specified group.
        """
        content = self._graphql_client.request(
            query="""
                query GroupMembers($workspaceSlug: String!, $slug: String!) {
                    group(workspaceSlug: $workspaceSlug, slug: $slug) {
                        members {
                            user {
                                id
                                firstName
                                lastName
                                email
                            }
                        }
                    }
                }
            """,
            variables={"workspaceSlug": workspace_slug, "slug": group_name},
        )

        return [
            GroupMember(
                user_id=m["user"]["id"],
                first_name=m["user"].get("firstName", ""),
                last_name=m["user"].get("lastName", ""),
                email=m["user"]["email"],
            )
            for m in content["data"]["group"]["members"]
        ]

    def add_group_member(
        self,
        workspace_slug: str,
        group_name: str,
        email: str,
    ) -> GroupMember:
        """Add a member to a group.

        Args:
            workspace_slug (str): The slug of the workspace containing the group.
            group_name (str): The name of the group to add the member to.
            email (str): The email address of the user to add to the group.

        Returns:
            GroupMember: The added GroupMember object.
        """
        content = self._graphql_client.request(
            query="""
                mutation AddGroupMember($input: AddGroupMemberInput!) {
                    addGroupMember(input: $input) {
                        member {
                            user {
                                id
                                firstName
                                lastName
                                email
                            }
                        }
                    }
                }
                """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "groupSlug": group_name,
                    "userEmail": email,
                }
            },
        )

        user = content["data"]["addGroupMember"]["member"]["user"]

        return GroupMember(
            user_id=user["id"],
            first_name=user.get("firstName", ""),
            last_name=user.get("lastName", ""),
            email=user["email"],
        )

    def remove_group_member(
        self,
        workspace_slug: str,
        group_name: str,
        email: str,
    ) -> bool:
        """Remove a member from a group.

        Args:
            workspace_slug (str): The slug of the workspace containing the group.
            group_name (str): The name of the group to remove the member from.
            email (str): The email address of the user to remove from the group.

        Returns:
            bool: True if the member was successfully removed, False otherwise.
        """
        content = self._graphql_client.request(
            query="""
                mutation RemoveGroupMember($input: RemoveGroupMemberInput!) {
                    removeGroupMember(input: $input) {
                        success
                    }
                }
                """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "groupSlug": group_name,
                    "userEmail": email,
                }
            },
        )

        return bool(content["data"]["removeGroupMember"]["success"])
