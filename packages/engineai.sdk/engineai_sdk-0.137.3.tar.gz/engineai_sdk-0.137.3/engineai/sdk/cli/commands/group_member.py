"""group member command for engineai CLI."""

import click
from rich.console import Console
from rich.table import Table

from engineai.sdk.api.client import api_client


@click.group()
def member() -> None:
    """Group member commands."""


@member.command("add")
@click.argument(
    "workspace_slug",
    required=True,
    type=str,
)
@click.argument(
    "group_name",
    required=True,
    type=str,
)
@click.argument(
    "email",
    required=True,
    type=str,
)
def add_group_member(
    workspace_slug: str,
    group_name: str,
    email: str,
) -> None:
    """Add member with EMAIL to group identified by GROUP_NAME within WORKSPACE_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        group_name: The group's name.
        email: Email of the user to be added.
    """
    api_client.group_member.add_group_member(
        workspace_slug,
        group_name,
        email,
    )

    click.echo(
        f"Successfully added user `{email}` to the group `{group_name}` within "
        f"the workspace `{workspace_slug}`.",
    )


@member.command("rm")
@click.argument(
    "workspace_slug",
    required=True,
    type=str,
)
@click.argument(
    "group_name",
    required=True,
    type=str,
)
@click.argument(
    "email",
    required=True,
    type=str,
)
def remove_group_member(
    workspace_slug: str,
    group_name: str,
    email: str,
) -> None:
    """Remove member with EMAIL from group identified by GROUP_NAME within WORKSPACE_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        group_name: The group's name.
        email: Email of the user to be removed.
    """
    api_client.group_member.remove_group_member(workspace_slug, group_name, email)

    click.echo(
        f"Successfully removed user `{email}` from the group `{group_name}` within the "
        f"workspace `{workspace_slug}`.",
    )


@member.command("ls")
@click.argument(
    "workspace_slug",
    required=True,
    type=str,
)
@click.argument(
    "group_name",
    required=True,
    type=str,
)
def list_group_member(
    workspace_slug: str,
    group_name: str,
) -> None:
    """List members of a group identified by GROUP_NAME within WORKSPACE_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        group_name: The group's name.
    """
    group_members = api_client.group_member.list_group_members(
        workspace_slug, group_name
    )

    if not group_members:
        click.echo(f"No members found in group `{group_name}`.")
        return

    console = Console()
    table = Table(
        title=f"Members of group '{group_name}'",
        show_header=False,
        show_edge=True,
    )

    for m in group_members:
        table.add_row(m.email)
    console.print(table)
