"""app command for engineai CLI."""

import click
from rich.console import Console
from rich.table import Table

from engineai.sdk.api.client import api_client
from engineai.sdk.api.graphql_client import APIServerError
from engineai.sdk.cli.commands.app_rule import rule


@click.group(name="app", invoke_without_command=False)
def app() -> None:
    """App commands."""


@app.command("ls")
@click.argument(
    "workspace_slug",
    required=True,
    type=str,
)
def list_workspace_apps(workspace_slug: str) -> None:
    """List apps within WORKSPACE_SLUG.

    \f
    Args:
        workspace_slug: The workspace's identifier.
    """
    workspace_apps = api_client.app.list_workspace_apps(workspace_slug)

    if not workspace_apps:
        click.echo(f"No apps found in workspace `{workspace_slug}`.")
        return

    console = Console()
    table = Table(
        title=f"Apps of workspace '{workspace_slug}'",
        show_header=True,
        show_edge=True,
    )
    table.add_column("Name")
    table.add_column("Slug")
    for a in workspace_apps:
        table.add_row(a.name, a.slug)
    console.print(table)


@app.command("create")
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
    "app_name",
    required=True,
    type=str,
)
def create_app(workspace_slug: str, app_slug: str, app_name: str) -> None:
    """Create an app with APP_SLUG and APP_NAME within WORKSPACE_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: Identifier for the new app (used in URLs).
        app_name: The display name of the app.
    """
    api_client.app.create_app(workspace_slug, app_slug, app_name)

    click.echo(
        f"Successfully created app `{app_slug}` with name `{app_name}` within "
        f"workspace `{workspace_slug}`."
    )


@app.command("update")
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
@click.option("-s", "--slug", type=str, default=None, help="new slug.")
@click.option("-n", "--name", type=str, default=None, help="new name.")
def update_app(
    workspace_slug: str, app_slug: str, slug: str | None, name: str | None
) -> None:
    """Update the slug or name of an app with APP_SLUG within WORKSPACE_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The app's identifier.
        slug: New slug for the app.
        name: New name for the app.
    """
    if slug is None and name is None:
        msg = (
            "You must provide at least one of the following options:\n"
            "-s, --slug: new app slug\n"
            "-n, --name: new app name"
        )
        raise click.UsageError(msg)

    api_client.app.update_app(
        workspace_slug,
        app_slug,
        slug,
        name,
    )

    msg = f"Successfully updated app `{app_slug}` within `{workspace_slug}`:"

    if slug is not None:
        msg += f"\n- new slug: `{slug}`"
    if name is not None:
        msg += f"\n- new name: `{name}`"
    click.echo(msg)


@app.command("trash")
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
def trash_app(workspace_slug: str, app_slug: str) -> None:
    """Move an app with APP_SLUG to trash within WORKSPACE_SLUG.

    NOTE: Once in the trash, you have 30 days to restore it otherwise the app and
    all its resources will be permanently deleted (including dashboards).

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The app's identifier.
    """
    api_client.app.trash_app(workspace_slug, app_slug)

    click.echo(
        f"Successfully moved app `{app_slug}` to trash within "
        f"workspace `{workspace_slug}`."
    )


@app.command("restore")
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
def restore_app(workspace_slug: str, app_slug: str) -> None:
    """Restore an app with APP_SLUG from trash within WORKSPACE_SLUG.

    NOTE: Restoring an app won't restore dashboards that were already in the trash prior to the app.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The app's identifier.
    """
    api_client.app.restore_app(workspace_slug, app_slug)

    click.echo(
        f"Successfully restored app `{app_slug}` from trash within "
        f"workspace `{workspace_slug}`."
    )


@app.command("rm")
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
def delete_app(workspace_slug: str, app_slug: str) -> None:
    """Delete an app with APP_SLUG permanently from trash within WORKSPACE_SLUG.

    \b
    NOTE:
    - The app must be in the trash before it can be deleted permanently.
    - This action cannot be undone.
    - All resources associated with the app will be permanently deleted, regardless of being in the trash or not.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The app's identifier.
    """
    try:
        # First check if the app still exists (if it does, it's not in trash)
        api_client.app.get_app(workspace_slug, app_slug)
    except APIServerError as err:
        if err.error_code != "NOT_FOUND":
            raise err
    else:
        # App still exists, so it's not in trash
        msg = (
            f"App `{app_slug}` must be moved to trash before deletion.\n\n"
            "Please move the app to trash first using: engineai app trash"
        )
        raise click.ClickException(msg) from None

    # App is not found (in trash or doesn't exist at all), proceed with deletion
    api_client.app.delete_app(workspace_slug, app_slug)

    click.echo(
        f"Successfully deleted app `{app_slug}` permanently from "
        f"workspace `{workspace_slug}`."
    )


app.add_command(rule)
