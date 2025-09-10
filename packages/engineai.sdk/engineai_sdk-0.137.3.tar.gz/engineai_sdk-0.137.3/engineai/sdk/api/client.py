"""API Client module."""

from engineai.sdk.api.app import AppAPI
from engineai.sdk.api.app_authorization_rule import AppAuthorizationRuleAPI
from engineai.sdk.api.dashboard import DashboardAPI
from engineai.sdk.api.dashboard_version import DashboardVersionAPI
from engineai.sdk.api.graphql_client import GraphQLClient
from engineai.sdk.api.group import GroupAPI
from engineai.sdk.api.group_member import GroupMemberAPI
from engineai.sdk.api.workspace import WorkspaceAPI
from engineai.sdk.api.workspace_member import WorkspaceMemberAPI


class APIClient:
    """Main API client for interacting with the Engine AI platform.

    This client provides access to all API endpoints through dedicated API classes.
    It manages a single GraphQL client instance that is shared across all API endpoints
    for consistent authentication and connection management.

    Attributes:
        graphql_client (GraphQLClient): The GraphQL client for making API requests.
        app (AppAPI): API interface for app-related operations.
        app_authorization_rule (AppAuthorizationRuleAPI): API interface for app
            authorization rules.
        dashboard (DashboardAPI): API interface for dashboard operations.
        dashboard_version (DashboardVersionAPI): API interface for dashboard
            version management.
        group (GroupAPI): API interface for group operations.
        group_member (GroupMemberAPI): API interface for group member management.
        workspace (WorkspaceAPI): API interface for workspace operations.
        workspace_member (WorkspaceMemberAPI): API interface for workspace
            member management.
    """

    def __init__(self) -> None:
        """Initialize the API client with all available API endpoints.

        Creates a GraphQL client instance and initializes all API endpoint classes
        with the shared GraphQL client for consistent communication.
        """
        self.graphql_client = GraphQLClient()

        self.app = AppAPI(self.graphql_client)
        self.app_authorization_rule = AppAuthorizationRuleAPI(self.graphql_client)
        self.dashboard = DashboardAPI(self.graphql_client)
        self.dashboard_version = DashboardVersionAPI(self.graphql_client)
        self.group = GroupAPI(self.graphql_client)
        self.group_member = GroupMemberAPI(self.graphql_client)
        self.workspace = WorkspaceAPI(self.graphql_client)
        self.workspace_member = WorkspaceMemberAPI(self.graphql_client)


api_client = APIClient()
