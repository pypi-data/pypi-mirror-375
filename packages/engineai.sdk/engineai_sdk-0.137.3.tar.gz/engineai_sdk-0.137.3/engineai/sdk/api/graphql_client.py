"""GraphQL API client."""

import datetime as dt
import uuid
from typing import Any

import requests

from engineai.sdk.api.auth import AuthTokenNotFoundError
from engineai.sdk.api.auth import authenticate_with_device_flow
from engineai.sdk.api.auth import get_auth_token
from engineai.sdk.api.auth import refresh_access_token


class APIServerError(Exception):
    """Exception raised when there is an error from the API."""

    def __init__(
        self,
        request_id: str,
        error: str,
        error_code: str | None = None,
    ) -> None:
        """Construct for APIServerError class.

        Args:
            request_id (str): Request id.
            error (str): error message.
            error_code (str | None): error code.
        """
        prefix = f"{error_code} - " if error_code is not None else ""
        self.error_code = error_code
        self.error_message = (
            f"A server error occurred while processing your request "
            f"(Request ID: {request_id}): {prefix}{error}"
        )
        super().__init__(self.error_message)


class GraphQLClient:
    """GraphQL API client for the EngineAI platform.

    This class handles GraphQL request execution against the EngineAI API.
    """

    def request(self, query: str, variables: dict[str, Any] | None = None) -> Any:
        """Execute a GraphQL query against the EngineAI API.

        Args:
            query (str): The GraphQL query string to execute.
            variables (dict[str, Any] | None): Optional dictionary of variables
                for the GraphQL query.

        Returns:
            Any: The response body from the GraphQL API.

        Raises:
            APIServerError: If the API returns an error response.
        """
        try:
            auth_token = get_auth_token()
        except AuthTokenNotFoundError:
            authenticate_with_device_flow()
            auth_token = get_auth_token()
        else:
            if auth_token["expires_at"] <= dt.datetime.now().timestamp():
                auth_token = refresh_access_token(auth_token)

        response = requests.post(
            auth_token["base_url"],
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {auth_token['access_token']}",
                "x-request-id": str(uuid.uuid4()),
            },
            json={
                "query": query,
                "variables": variables or {},
            },
            timeout=15,
        )

        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            raise APIServerError(
                request_id=response.headers["x-request-id"],
                error=str(err.response.content if err.response is not None else err),
            ) from err

        response_body = response.json()

        if (response_errors := response_body.get("errors")) is not None:
            error_extensions = response_errors[0].get("extensions")

            raise APIServerError(
                request_id=response.headers["x-request-id"],
                error=response_errors[0].get("message"),
                error_code=error_extensions.get("code"),
            )

        return response_body
