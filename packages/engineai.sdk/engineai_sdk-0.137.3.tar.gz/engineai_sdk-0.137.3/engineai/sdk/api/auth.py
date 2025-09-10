"""Authentication module."""

import datetime as dt
import json
import sys
import webbrowser
from pathlib import Path
from time import sleep
from typing import Final
from typing import TypedDict
from typing import cast
from urllib.parse import urlparse

import requests

DEFAULT_API_URL: Final[str] = "https://api.engineai.com"

TOKEN_FILE: Final[Path] = Path("~/.engineai/auth_token.json").expanduser()

AUTH_CONFIG: Final[dict[str, dict[str, str]]] = {
    "api.engineai.dev": {
        "device_code_url": "https://login.engineai.dev/oauth/device/code",
        "token_url": "https://login.engineai.dev/oauth/token",
        "client_id": "UxR3Nhc03f0MlURPGKK4W7uuj0m8ZH9t",
        "audience": "https://api.dystematic.dev",
    },
    "api.engineai.review": {
        "device_code_url": "https://login.engineai.review/oauth/device/code",
        "token_url": "https://login.engineai.review/oauth/token",
        "client_id": "2woAkEoVBZ2PyFRWMOW8nFvD0iaeNga5",
        "audience": "https://api.dystematic.review",
    },
    "api.engineai.com": {
        "device_code_url": "https://login.engineai.com/oauth/device/code",
        "token_url": "https://login.engineai.com/oauth/token",
        "client_id": "PeBZtJkx9cFmoDUY7v6wlXBVA1I2Wigd",
        "audience": "https://api.dystematic.com",
    },
    "localhost:4000": {
        "device_code_url": "https://dystematic-dev.eu.auth0.com/oauth/device/code",
        "token_url": "https://dystematic-dev.eu.auth0.com/oauth/token",
        "client_id": "UxR3Nhc03f0MlURPGKK4W7uuj0m8ZH9t",
        "audience": "http://api.dystematic.local:4000",
    },
}


class AuthenticationError(Exception):
    """Authentication-related error."""


class AuthTokenNotFoundError(Exception):
    """Authentication-related error."""


class AuthToken(TypedDict):
    """Dictionary type for storing authentication token details."""

    base_url: str
    access_token: str
    refresh_token: str
    expires_in: float
    expires_at: float


def _save_auth_token(url: str, auth_token: AuthToken) -> None:
    """Save the authentication token to a local file.

    Args:
        url (str): The base URL of the API.
        auth_token (dict[str, Any]): The authentication token dictionary
            containing 'access_token', 'expires_in', 'refresh_token', etc.
    """
    auth_token["base_url"] = url
    auth_token["expires_at"] = (
        dt.datetime.now() + dt.timedelta(seconds=auth_token["expires_in"] - 5)
    ).timestamp()  # using timestamp since datetime is not json serializable by default

    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(auth_token), encoding="utf-8")


def get_auth_token() -> AuthToken:
    """Get authentication token.

    Retrieves the authentication token from the local file system.

    Returns:
        dict[str, Any]: A dictionary containing the valid authentication token
            with keys like 'access_token', 'expires_at', 'refresh_token', etc.

    Raises:
        AuthenticationTokenNotFoundError: If the authentication token file does not
            exist.
    """
    if not TOKEN_FILE.exists():
        msg = "no authentication token found"
        raise AuthTokenNotFoundError(msg)

    return cast(AuthToken, json.loads(TOKEN_FILE.read_text()))


def authenticate_with_device_flow(url: str = DEFAULT_API_URL) -> None:
    """Authenticate the user using the device flow method.

    Opens a web browser for the user to log in and polls the authentication server
    until the user completes the login process or the device code expires.

    Args:
        url (str): The base URL of the API. Defaults to the `DEFAULT_API_URL`.

    Raises:
        AuthenticationError: If authentication fails or the device code expires.
    """
    auth_config = AUTH_CONFIG[urlparse(url).netloc]

    response = requests.post(
        auth_config["device_code_url"],
        json={
            "client_id": auth_config["client_id"],
            "audience": auth_config["audience"],
            "scope": "offline_access",
        },
        timeout=60,
    )
    if response.status_code != 200:
        raise AuthenticationError(
            f"Unexpected status code (status_code={response.status_code}) "
            f"for url: {auth_config['device_code_url']}. "
            f"Response text: {response.text}"
        )

    device_info = response.json()
    device_code_expires_at = dt.datetime.now() + dt.timedelta(
        seconds=device_info["expires_in"]
    )

    sys.stdout.write(
        f"A web browser has been opened at {device_info['verification_uri_complete']}. "
        f"Please complete the login in the browser by verifying the following code:\n"
        f"{device_info['user_code']}\n\n"
        "If the browser fails to open, please enter the respective url manually.\n"
        "Return here once the login process is complete.\n"
    )
    sys.stdout.flush()

    webbrowser.open(device_info["verification_uri_complete"])

    while dt.datetime.now() < device_code_expires_at:
        sys.stdout.write(
            f"Waiting {device_info['interval']} seconds until checking again for "
            "browser authentication...\n"
        )
        sys.stdout.flush()
        sleep(device_info["interval"])

        response = requests.post(
            auth_config["token_url"],
            json={
                "client_id": auth_config["client_id"],
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_info["device_code"],
            },
            timeout=60,
        )

        if response.status_code == 200:
            _save_auth_token(url, response.json())
            return

        if (
            response.status_code == 403
            and response.json()["error"] == "authorization_pending"
        ):
            continue

        raise AuthenticationError(
            "Unable to obtain token: "
            f"status_code='{response.status_code}'; "
            f"reason='{response.reason}'."
        )

    raise AuthenticationError(
        "Device code expired while waiting for web browser authentication."
    )


def authenticate_with_username_password(
    username: str,
    password: str,
    url: str = DEFAULT_API_URL,
) -> None:
    """Authenticate the user using username and password.

    Sends a request to the authentication server with the provided username and password
    to obtain an access token. Saves the token to a local file for future use.

    Args:
        url (str): The base URL of the API. Defaults to the `DEFAULT_API_URL`.
        auth_config (dict[str, str]): Configuration dictionary containing token URL,
            client ID, and audience.
        username (str): The user's username.
        password (str): The user's password.

    Raises:
        AuthenticationError: If authentication fails.
    """
    auth_config = AUTH_CONFIG[urlparse(url).netloc]

    response = requests.post(
        auth_config["token_url"],
        json={
            "client_id": auth_config["client_id"],
            "grant_type": "password",
            "username": username,
            "password": password,
            "audience": auth_config["audience"],
            "scope": "offline_access",
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise AuthenticationError(
            "Username/password authentication failed "
            f"(status_code={response.status_code}). "
            f"Response text: {response.text}"
        )

    _save_auth_token(url, response.json())


def refresh_access_token(auth_token: AuthToken) -> AuthToken:
    """Refresh an expired access token using the refresh token.

    Makes a request to the OAuth token endpoint to refresh an expired access
    token using the stored refresh token. Updates the token file with the new
    access token and expiration time.

    Args:
        auth_token (dict[str, Any]): The current authentication token dictionary
            containing 'refresh_token', 'base_url', and other token information.

    Returns:
        dict[str, Any]: The updated authentication token dictionary with the
            new access token and expiration time.

    Raises:
        ValueError: If the token refresh request fails or returns a non-200
            status code.
    """
    auth_config = AUTH_CONFIG[urlparse(auth_token["base_url"]).netloc]
    response = requests.post(
        auth_config["token_url"],
        json={
            "client_id": auth_config["client_id"],
            "grant_type": "refresh_token",
            "refresh_token": auth_token["refresh_token"],
        },
        timeout=60,
    )

    if response.status_code == 200:
        new_auth_token = response.json()
        auth_token["access_token"] = new_auth_token["access_token"]
        if "refresh_token" in new_auth_token:
            auth_token["refresh_token"] = new_auth_token["refresh_token"]
        auth_token["expires_in"] = new_auth_token["expires_in"]

        _save_auth_token(auth_token["base_url"], auth_token)

        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(json.dumps(auth_token), encoding="utf-8")
        return auth_token

    msg = (
        "Unable to refresh access token. Response "
        f"(status_code='{response.status_code}', "
        f"reason='{response.reason}')."
    )
    raise ValueError(msg)
