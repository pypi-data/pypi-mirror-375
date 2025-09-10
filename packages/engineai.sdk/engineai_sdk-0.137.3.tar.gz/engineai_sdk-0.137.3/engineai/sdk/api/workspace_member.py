"""Workspace member management."""

from dataclasses import dataclass

from engineai.sdk.api.graphql_client import GraphQLClient


@dataclass
class WorkspaceMember:
    """Represents a member of a workspace in Engine AI's platform.

    Args:
        user_id (str): Unique identifier for the user
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email address
        role (str): The role assigned to the user in the workspace
    """

    user_id: str
    first_name: str
    last_name: str
    email: str
    role: str
    is_invitee: bool = False


class WorkspaceMemberAPI:
    """API client for managing workspace members.

    This class provides methods to list, add, update, remove workspace members,
    and transfer workspace ownership within workspaces.
    """

    def __init__(self, graphql_client: GraphQLClient) -> None:
        """Initialize the WorkspaceMemberAPI.

        Args:
            graphql_client (GraphQLClient): The GraphQL client instance to use
                for requests.
        """
        self._graphql_client = graphql_client

    def list_workspace_members(self, workspace_slug: str) -> list[WorkspaceMember]:
        """List all members of a workspace.

        Args:
            workspace_slug (str): The slug of the workspace to list members from.

        Returns:
            list[WorkspaceMember]: A list of WorkspaceMember objects in the
                specified workspace.
        """
        content = self._graphql_client.request(
            query="""
                query WorkspacesMembers($slug: String!) {
                    workspace (slug: $slug){
                        members {
                            user {
                                id
                                firstName
                                lastName
                                email
                            }
                            role
                            isInvitee
                        }
                    }
                }
            """,
            variables={"slug": workspace_slug},
        )

        return [
            WorkspaceMember(
                user_id=m["user"]["id"],
                first_name=m["user"].get("firstName", ""),
                last_name=m["user"].get("lastName", ""),
                email=m["user"]["email"],
                role=m["role"],
                is_invitee=m["isInvitee"],
            )
            for m in content["data"]["workspace"]["members"]
        ]

    def invite_workspace_member(
        self,
        workspace_slug: str,
        email: str,
        role: str,
    ) -> WorkspaceMember | None:
        """Invite a new member to a workspace.

        Args:
            workspace_slug (str): The slug of the workspace to invite the member to.
            email (str): The email address of the user to invite.
            role (str): The role to assign to the invited user.

        Returns:
            WorkspaceMember | None: The WorkspaceMember object representing the
                invited user, or None if the user already belongs to the workspace
                or the invitation failed.
        """
        content = self._graphql_client.request(
            query="""
                mutation InviteWorkspaceMembers($input: InviteWorkspaceMembersInput!) {
                    inviteWorkspaceMembers(input: $input) {
                        members {
                            user {
                                id
                                firstName
                                lastName
                                email
                            }
                            role
                            isInvitee
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "usersEmails": [email],
                    "role": role,
                }
            },
        )

        members_list = content["data"]["inviteWorkspaceMembers"]["members"]
        member = members_list[0] if len(members_list) > 0 else None
        if not member:
            return None

        return WorkspaceMember(
            user_id=member["user"]["id"],
            first_name=member["user"].get("firstName", ""),
            last_name=member["user"].get("lastName", ""),
            email=member["user"]["email"],
            role=member["role"],
            is_invitee=member["isInvitee"],
        )

    def update_workspace_member(
        self,
        workspace_slug: str,
        email: str,
        role: str,
    ) -> WorkspaceMember:
        """Update a workspace member's role.

        Args:
            workspace_slug (str): The slug of the workspace containing the member.
            email (str): The email address of the user to update.
            role (str): The new role to assign to the user.

        Returns:
            WorkspaceMember: The updated WorkspaceMember object.
        """
        content = self._graphql_client.request(
            query="""
                mutation UpdateWorkspaceMember($input: UpdateWorkspaceMemberInput!) {
                    updateWorkspaceMember(input: $input) {
                        member {
                            user {
                                id
                                firstName
                                lastName
                                email
                            }
                            role
                            isInvitee
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "userEmail": email,
                    "role": role,
                }
            },
        )

        member = content["data"]["updateWorkspaceMember"]["member"]

        return WorkspaceMember(
            user_id=member["user"]["id"],
            first_name=member["user"].get("firstName", ""),
            last_name=member["user"].get("lastName", ""),
            email=member["user"]["email"],
            role=member["role"],
            is_invitee=member["isInvitee"],
        )

    def remove_workspace_member(self, workspace_slug: str, email: str) -> bool:
        """Remove a member from a workspace.

        Args:
            workspace_slug (str): The slug of the workspace to remove the member from.
            email (str): The email address of the user to remove from the workspace.

        Returns:
            bool: True if the member was successfully removed, False otherwise.
        """
        content = self._graphql_client.request(
            query="""
                mutation RemoveWorkspaceMember($input: RemoveWorkspaceMemberInput!) {
                    removeWorkspaceMember(input: $input) {
                        success
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "userEmail": email,
                }
            },
        )

        return bool(content["data"]["removeWorkspaceMember"]["success"])

    def transfer_workspace_ownership(
        self,
        workspace_slug: str,
        email: str,
    ) -> WorkspaceMember:
        """Transfer ownership of a workspace to another member.

        Args:
            workspace_slug (str): The slug of the workspace to transfer ownership of.
            email (str): The email address of the user to transfer ownership to.

        Returns:
            WorkspaceMember: The WorkspaceMember object representing the new owner.
        """
        content = self._graphql_client.request(
            query="""
                mutation TransferWorkspace($input: TransferWorkspaceInput!) {
                    transferWorkspace(input: $input) {
                        member {
                            user {
                                id
                                firstName
                                lastName
                                email
                            }
                            role
                            isInvitee
                        }
                    }
                }
            """,
            variables={"input": {"workspaceSlug": workspace_slug, "userEmail": email}},
        )

        member = content["data"]["transferWorkspace"]["member"]

        return WorkspaceMember(
            user_id=member["user"]["id"],
            first_name=member["user"].get("firstName", ""),
            last_name=member["user"].get("lastName", ""),
            email=member["user"]["email"],
            role=member["role"],
            is_invitee=member["isInvitee"],
        )
