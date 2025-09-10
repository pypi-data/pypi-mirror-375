"""group command for engineai CLI."""

import click
from rich.console import Console
from rich.table import Table

from engineai.sdk.api.client import api_client
from engineai.sdk.cli.commands.group_member import member


@click.group(name="group", invoke_without_command=False)
def group() -> None:
    """Group commands."""


@group.command("ls")
@click.argument(
    "workspace_slug",
    required=True,
    type=str,
)
def list_workspace_groups(workspace_slug: str) -> None:
    """List groups within WORKSPACE_SLUG.

    \f
    Args:
        workspace_slug: The workspace's identifier.
    """
    workspace_groups = api_client.group.list_workspace_groups(workspace_slug)

    if not workspace_groups:
        click.echo(f"No groups found in workspace `{workspace_slug}`.")
        return

    console = Console()
    table = Table(
        title=f"Groups of workspace '{workspace_slug}'",
        show_header=False,
        show_edge=True,
    )
    for g in workspace_groups:
        table.add_row(g.name)
    console.print(table)


@group.command("create")
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
def create_group(workspace_slug: str, group_name: str) -> None:
    """Create a group with GROUP_NAME within WORKSPACE_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        group_name: The group's name.
    """
    api_client.group.create_group(workspace_slug, group_name)

    click.echo(
        f"Successfully created group `{group_name}` within the workspace `{workspace_slug}`.",
    )


@group.command("rm")
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
def delete_group(workspace_slug: str, group_name: str) -> None:
    """Delete group with GROUP_NAME from WORKSPACE_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        group_name: The group's name.
    """
    api_client.group.delete_group(workspace_slug, group_name)

    click.echo(
        f"Successfully deleted group `{group_name}` from the workspace `{workspace_slug}`.",
    )


@group.command("rename")
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
    "new_group_name",
    required=True,
    type=str,
)
def rename_group(workspace_slug: str, group_name: str, new_group_name: str) -> None:
    """Rename a group identified by GROUP_NAME within WORKSPACE_SLUG to NEW_GROUP_NAME.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        group_name: The group's name.
        new_group_name: The group's new name.
    """
    api_client.group.update_group(workspace_slug, group_name, new_group_name)

    click.echo(
        f"Successfully renamed group `{group_name}` within the workspace `{workspace_slug}` to "
        f"`{new_group_name}`.",
    )


group.add_command(member)
