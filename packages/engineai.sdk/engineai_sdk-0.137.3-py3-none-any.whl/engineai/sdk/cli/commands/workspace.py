"""workspace command for engineai CLI."""

import click
from rich.console import Console
from rich.table import Table

from engineai.sdk.api.client import api_client
from engineai.sdk.cli.commands.workspace_member import member

WORKSPACE_ROLE = ["ADMIN", "MEMBER"]


@click.group(name="workspace", invoke_without_command=False)
def workspace() -> None:
    """Workspace commands."""


@workspace.command("ls")
def list_user_workspaces() -> None:
    """List all user workspaces."""
    workspace_list = api_client.workspace.list_user_workspaces()

    if not workspace_list:
        click.echo("No workspaces found.")
        return

    console = Console()
    table = Table(
        title="User Workspaces",
        show_header=True,
        show_edge=True,
    )
    table.add_column("Name")
    table.add_column("Slug")
    for w in workspace_list:
        table.add_row(w.name, w.slug)
    console.print(table)


@workspace.command("create")
@click.argument(
    "slug",
    required=True,
    type=str,
)
@click.argument(
    "name",
    required=True,
    type=str,
)
def create_workspace(slug: str, name: str) -> None:
    """Create a workspace with SLUG and NAME.

    \f
    Args:
        slug: Identifier for the new workspace (used in URLs).
        name: The display name of the workspace.
    """
    api_client.workspace.create_workspace(slug, name)

    click.echo(f"Successfully created workspace `{slug}` with name `{name}`.")


@workspace.command("rm")
@click.argument(
    "slug",
    required=True,
    type=str,
)
def delete_workspace(slug: str) -> None:
    """Delete a workspace with SLUG.

    NOTE: This will permanently delete the workspace and all its contents (apps, dashboards, etc.).

    \f
    Args:
        slug: The workspace's identifier.
    """
    api_client.workspace.delete_workspace(slug)

    click.echo(f"Successfully deleted workspace `{slug}`.")


@workspace.command("update")
@click.argument(
    "slug",
    required=True,
    type=str,
)
@click.option("-s", "--slug", "new_slug", type=str, default=None, help="new slug.")
@click.option("-n", "--name", type=str, default=None, help="new name.")
def update_workspace(slug: str, new_slug: str | None, name: str | None) -> None:
    """Update the name or slug of a workspace with SLUG.

    \f
    Args:
        slug: The parent workspace's identifier.
        new_slug: New slug for the workspace.
        name: New name for the workspace.
    """
    if new_slug is None and name is None:
        msg = (
            "You must provide at least one of the following options:\n"
            "-s, --slug: new workspace slug\n"
            "-n, --name: new workspace name"
        )
        raise click.ClickException(msg)

    api_client.workspace.update_workspace(slug=slug, new_slug=new_slug, new_name=name)

    msg = f"Successfully updated workspace `{slug}`:"

    if new_slug is not None:
        msg += f"\n- new slug: `{new_slug}`"
    if name is not None:
        msg += f"\n- new name: `{name}`"
    click.echo(msg)


workspace.add_command(member)
