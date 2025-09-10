"""Auth command for engineai CLI."""

from urllib.parse import urlparse

import click

from engineai.sdk.api.auth import AUTH_CONFIG
from engineai.sdk.api.auth import DEFAULT_API_URL
from engineai.sdk.api.auth import authenticate_with_device_flow
from engineai.sdk.api.auth import authenticate_with_username_password


@click.command()
@click.argument("url", type=str, default=DEFAULT_API_URL)
@click.option(
    "--username",
    "-u",
    type=str,
    default="",
    help="Username to authenticate with the system",
)
@click.option(
    "--password",
    "-p",
    type=str,
    default="",
    help="Password associated with the provided username",
)
def login(url: str, username: str, password: str) -> None:
    """Log in the EngineAI API Authentication System.

    \f
    Args:
        url (str): The URL of the EngineAI API to log in to.
        username (str): Username to authenticate with the system.
        password (str): Password associated with the provided username.
    """
    if urlparse(url).netloc not in AUTH_CONFIG.keys():
        msg = f"Invalid URL: '{url}'. Please use a valid EngineAI API url."
        raise click.BadArgumentUsage(msg)

    if any((username, password)):
        if not username:
            raise click.BadOptionUsage(
                "username",
                "Username required when password is provided.",
            )
        if not password:
            raise click.BadOptionUsage(
                "password",
                "Password required when username is provided.",
            )

        authenticate_with_username_password(
            username,
            password,
            url,
        )
    else:
        authenticate_with_device_flow(url)

    click.echo("Successfully logged in to EngineAI API.")
