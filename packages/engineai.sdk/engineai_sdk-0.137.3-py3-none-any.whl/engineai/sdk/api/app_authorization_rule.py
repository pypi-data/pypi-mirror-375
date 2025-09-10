"""App authorization rule management."""

from dataclasses import dataclass

from engineai.sdk.api.graphql_client import GraphQLClient
from engineai.sdk.api.group import Group


@dataclass
class User:
    """User representation for app authorization.

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


@dataclass
class AppAuthorizationRule:
    """App authorization rule linking a subject (user or group) to a role.

    Args:
        role (str): The role assigned to the subject.
        subject (Group | User): Either a User or Group that the rule applies to.
    """

    role: str
    subject: Group | User


class AppAuthorizationRuleAPI:
    """API client for managing app authorization rules.

    This class provides methods to list, add, update, and remove authorization
    rules for apps.
    """

    def __init__(self, graphql_client: GraphQLClient) -> None:
        """Initialize the AppAuthorizationRuleAPI.

        Args:
            graphql_client (GraphQLClient): The GraphQL client instance to use for
                requests.
        """
        self._graphql_client = graphql_client

    def list_app_authorization_rules(
        self,
        workspace_slug: str,
        app_slug: str,
    ) -> list[AppAuthorizationRule]:
        """List all authorization rules for a specific app.

        Args:
            workspace_slug (str): The slug of the workspace containing the app.
            app_slug (str): The slug of the app to list rules for.

        Returns:
            list[AppAuthorizationRule]: A list of AppAuthorizationRule objects
                for the specified app.
        """
        content = self._graphql_client.request(
            query="""
                query AppRules($appSlug: String, $workspaceSlug: String){
                    app(appSlug: $appSlug, workspaceSlug: $workspaceSlug) {
                        authorizationRules {
                            role
                            subject {
                                ... on User {
                                    id
                                    firstName
                                    lastName
                                    email
                                }
                                ... on Group {
                                    id
                                    slug
                                }
                                __typename
                            }
                        }
                    }
                }
            """,
            variables={"workspaceSlug": workspace_slug, "appSlug": app_slug},
        )

        return [
            AppAuthorizationRule(
                role=r["role"],
                subject=(
                    Group(
                        group_id=r["subject"]["id"],
                        name=r["subject"]["slug"],
                    )
                    if "Group" in r["subject"]["__typename"]
                    else User(
                        user_id=r["subject"]["id"],
                        first_name=r["subject"].get("firstName", ""),
                        last_name=r["subject"].get("lastName", ""),
                        email=r["subject"]["email"],
                    )
                ),
            )
            for r in content["data"]["app"]["authorizationRules"]
        ]

    def add_app_authorization_rule(
        self,
        workspace_slug: str,
        app_slug: str,
        user: str | None,
        user_group: str | None,
        role: str,
    ) -> AppAuthorizationRule:
        """Add a new authorization rule to an app.

        Args:
            workspace_slug (str): The slug of the workspace containing the app.
            app_slug (str): The slug of the app to add the rule to.
            user (str | None): Email of the user to add (mutually exclusive with
                user_group).
            user_group (str | None): Slug of the group to add (mutually exclusive with
                user).
            role (str): The role to assign to the user or group.

        Returns:
            AppAuthorizationRule: The created AppAuthorizationRule object.
        """
        content = self._graphql_client.request(
            query="""
                mutation AddAuthorizationRule($input: AddAppAuthorizationRuleInput!){
                    addAppAuthorizationRule(input: $input) {
                        rule {
                            role
                            subject {
                                ... on User {
                                    id
                                    firstName
                                    lastName
                                    email
                                }
                                ... on Group {
                                    id
                                    slug
                                }
                            }
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "appSlug": app_slug,
                    "subject": (
                        {"userEmail": user}
                        if user is not None
                        else {"groupSlug": user_group}
                    ),
                    "role": role,
                }
            },
        )

        rule = content["data"]["addAppAuthorizationRule"]["rule"]

        return AppAuthorizationRule(
            role=rule["role"],
            subject=(
                Group(
                    group_id=rule["subject"]["id"],
                    name=rule["subject"]["slug"],
                )
                if user_group is not None
                else User(
                    user_id=rule["subject"]["id"],
                    first_name=rule["subject"].get("firstName", ""),
                    last_name=rule["subject"].get("lastName", ""),
                    email=rule["subject"]["email"],
                )
            ),
        )

    def update_app_authorization_rule(
        self,
        workspace_slug: str,
        app_slug: str,
        user: str | None,
        user_group: str | None,
        role: str,
    ) -> AppAuthorizationRule:
        """Update an existing authorization rule for an app.

        Args:
            workspace_slug (str): The slug of the workspace containing the app.
            app_slug (str): The slug of the app to update the rule for.
            user (str | None): Email of the user to update (mutually exclusive with
                user_group).
            user_group (str | None): Slug of the group to update (mutually exclusive
                with user).
            role (str): The new role to assign to the user or group.

        Returns:
            AppAuthorizationRule: The updated AppAuthorizationRule object.
        """
        content = self._graphql_client.request(
            query="""
                mutation updateAuthorizationRule(
                    $input: UpdateAppAuthorizationRuleInput!
                ){
                    updateAppAuthorizationRule(input: $input) {
                        rule {
                            role
                            subject {
                                ... on User {
                                    id
                                    firstName
                                    lastName
                                    email
                                }
                                ... on Group {
                                    id
                                    slug
                                }
                            }
                        }
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "appSlug": app_slug,
                    "subject": (
                        {"userEmail": user}
                        if user is not None
                        else {"groupSlug": user_group}
                    ),
                    "role": role,
                }
            },
        )

        rule = content["data"]["updateAppAuthorizationRule"]["rule"]

        return AppAuthorizationRule(
            role=rule["role"],
            subject=(
                Group(
                    group_id=rule["subject"]["id"],
                    name=rule["subject"]["slug"],
                )
                if user_group is not None
                else User(
                    user_id=rule["subject"]["id"],
                    first_name=rule["subject"].get("firstName", ""),
                    last_name=rule["subject"].get("lastName", ""),
                    email=rule["subject"]["email"],
                )
            ),
        )

    def remove_app_authorization_rule(
        self,
        workspace_slug: str,
        app_slug: str,
        user: str | None,
        user_group: str | None,
    ) -> bool:
        """Remove an authorization rule from an app.

        Args:
            workspace_slug (str): The slug of the workspace containing the app.
            app_slug (str): The slug of the app to remove the rule from.
            user (str | None): Email of the user to remove (mutually exclusive with
                user_group).
            user_group (str | None): Slug of the group to remove (mutually exclusive
                with user).

        Returns:
            bool: True if the rule was successfully removed, False otherwise.
        """
        content = self._graphql_client.request(
            query="""
                mutation RemoveAuthorizationRule(
                    $input: RemoveAppAuthorizationRuleInput!
                ){
                    removeAppAuthorizationRule(input: $input) {
                        success
                    }
                }
            """,
            variables={
                "input": {
                    "workspaceSlug": workspace_slug,
                    "appSlug": app_slug,
                    "subject": (
                        {"userEmail": user}
                        if user is not None
                        else {"groupSlug": user_group}
                    ),
                }
            },
        )

        return bool(content["data"]["removeAppAuthorizationRule"]["success"])
