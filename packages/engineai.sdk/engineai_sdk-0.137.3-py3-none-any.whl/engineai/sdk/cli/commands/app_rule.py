"""app rule command for engineai CLI."""

from typing import cast

import click
from rich.console import Console
from rich.table import Table

from engineai.sdk.api.app_authorization_rule import User
from engineai.sdk.api.client import api_client
from engineai.sdk.api.group import Group

# User-facing role choices (what users see in CLI)
APP_AUTHORIZATION_ROLE_DISPLAY = ["MANAGER", "WRITER", "READER"]

ROLE_DISPLAY_TO_API = {"MANAGER": "ADMIN", "WRITER": "WRITE", "READER": "READ"}

ROLE_API_TO_DISPLAY = {"ADMIN": "MANAGER", "WRITE": "WRITER", "READ": "READER"}


@click.group()
def rule() -> None:
    """App rule commands."""


@rule.command("add")
@click.argument(
    "workspace_slug",
    required=True,
    type=str,
)
@click.argument(
    "app_slug",
    required=True,
    type=str,
)
@click.argument(
    "subject",
    required=True,
    type=str,
    metavar="USER_EMAIL|GROUP_NAME",
)
@click.argument(
    "role",
    required=True,
    type=click.Choice(APP_AUTHORIZATION_ROLE_DISPLAY, case_sensitive=False),
)
def add_app_authorization_rule(
    workspace_slug: str,
    app_slug: str,
    subject: str,
    role: str,
) -> None:
    """Add an authorization rule for a USER_EMAIL or GROUP_NAME with ROLE in the app identified by APP_SLUG within WORKSPACE_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The app identifier.
        subject: Email of the user (if contains @) or name of the group.
        role: The role for the user or group in the app (MANAGER, WRITER, or READER).
    """
    # Determine if subject is a user (contains @) or group
    is_user = "@" in subject
    user_email = subject if is_user else None
    group_name = subject if not is_user else None

    display_role = role.upper()
    authorization_role = ROLE_DISPLAY_TO_API[display_role]

    api_client.app_authorization_rule.add_app_authorization_rule(
        workspace_slug,
        app_slug,
        role=authorization_role,
        user=user_email,
        user_group=group_name,
    )

    subject_type = "user" if is_user else "group"

    click.echo(
        f"Successfully added new authorization rule for {subject_type} `{subject}` with role `{display_role}` in app "
        f"`{app_slug}` within workspace `{workspace_slug}`."
    )


@rule.command("update")
@click.argument(
    "workspace_slug",
    required=True,
    type=str,
)
@click.argument(
    "app_slug",
    required=True,
    type=str,
)
@click.argument(
    "subject",
    required=True,
    type=str,
    metavar="USER_EMAIL|GROUP_NAME",
)
@click.argument(
    "role",
    required=True,
    type=click.Choice(APP_AUTHORIZATION_ROLE_DISPLAY, case_sensitive=False),
)
def update_app_authorization_rule(
    workspace_slug: str,
    app_slug: str,
    subject: str,
    role: str,
) -> None:
    """Update authorization rule for USER_EMAIL or GROUP_NAME to ROLE in the app identified by APP_SLUG within WORKSPACE_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The app identifier.
        subject: Email of the user (if contains @) or name of the group.
        role: The new role for the user or group in the app (MANAGER, WRITER, or READER).
    """
    # Determine if subject is a user (contains @) or group
    is_user = "@" in subject
    user_email = subject if is_user else None
    group_name = subject if not is_user else None

    display_role = role.upper()
    authorization_role = ROLE_DISPLAY_TO_API[display_role]

    api_client.app_authorization_rule.update_app_authorization_rule(
        workspace_slug,
        app_slug,
        role=authorization_role,
        user=user_email,
        user_group=group_name,
    )

    subject_type = "user" if is_user else "group"

    click.echo(
        (
            f"Successfully updated {subject_type} `{subject}`'s role to"
            f" `{display_role}` in app `{app_slug}` within workspace"
            f" `{workspace_slug}`."
        )
    )


@rule.command("rm")
@click.argument(
    "workspace_slug",
    required=True,
    type=str,
)
@click.argument(
    "app_slug",
    required=True,
    type=str,
)
@click.argument(
    "subject",
    required=True,
    type=str,
    metavar="USER_EMAIL|GROUP_NAME",
)
def remove_app_authorization_rule(
    workspace_slug: str,
    app_slug: str,
    subject: str,
) -> None:
    """Remove authorization rule for USER_EMAIL or GROUP_NAME in the app identified by APP_SLUG within WORKSPACE_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The app identifier.
        subject: Email of the user (if contains @) or name of the group.
    """
    # Determine if subject is a user (contains @) or group
    is_user = "@" in subject
    user_email = subject if is_user else None
    group_name = subject if not is_user else None

    api_client.app_authorization_rule.remove_app_authorization_rule(
        workspace_slug, app_slug, user=user_email, user_group=group_name
    )

    subject_type = "user" if is_user else "group"

    click.echo(
        (
            f"Successfully removed authorization rule for {subject_type} `{subject}` "
            f"in app `{app_slug}` within workspace `{workspace_slug}`."
        )
    )


@rule.command("ls")
@click.argument(
    "workspace_slug",
    required=True,
    type=str,
)
@click.argument(
    "app_slug",
    required=True,
    type=str,
)
def list_app_authorization_rules(
    workspace_slug: str,
    app_slug: str,
) -> None:
    """List authorization rules for an app identified by APP_SLUG within WORKSPACE_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The app identifier.
    """
    app_authorization_rules = (
        api_client.app_authorization_rule.list_app_authorization_rules(
            workspace_slug, app_slug
        )
    )

    if not app_authorization_rules:
        click.echo(f"No rules found in app `{app_slug}`")
        return

    console = Console()
    table = Table(
        title=f"Rules of app '{app_slug}'",
        show_header=True,
        show_edge=True,
    )

    table.add_column("", style="dim", justify="right")
    table.add_column("Subject")
    table.add_column("Role")

    table.add_section()

    user_rules = (r for r in app_authorization_rules if isinstance(r.subject, User))
    group_rules = (r for r in app_authorization_rules if isinstance(r.subject, Group))

    for i, r in enumerate(user_rules):
        table.add_row(
            "Users" if i == 0 else "",
            cast("User", r.subject).email,
            ROLE_API_TO_DISPLAY[r.role],
        )

    table.add_section()

    for i, r in enumerate(group_rules):
        table.add_row(
            "Groups" if i == 0 else "",
            cast("Group", r.subject).name,
            ROLE_API_TO_DISPLAY[r.role],
        )
    console.print(table)
