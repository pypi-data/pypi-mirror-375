"""dashboard command for engineai CLI."""

import click
from rich.console import Console
from rich.table import Table

from engineai.sdk.api.auth import get_auth_token
from engineai.sdk.api.client import api_client
from engineai.sdk.api.graphql_client import APIServerError


@click.group(name="dashboard", invoke_without_command=False)
def dashboard() -> None:
    """Dashboard commands."""


@dashboard.command("ls")
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
def list_app_dashboards(workspace_slug: str, app_slug: str) -> None:
    """List dashboards within WORKSPACE_SLUG and APP_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The app's identifier.
    """
    app_dashboards = api_client.dashboard.list_app_dashboards(workspace_slug, app_slug)

    if not app_dashboards:
        click.echo(f"No dashboards found in app `{app_slug}`.")
        return

    console = Console()
    table = Table(
        title=f"Dashboards of app `{app_slug}`",
        show_header=True,
        show_edge=True,
    )
    table.add_column("Name")
    table.add_column("Slug")
    table.add_column("Active Version", justify="left")
    for d in app_dashboards:
        table.add_row(d.name, d.slug, d.active_version or "-")
    with console.pager():
        console.print(table)


@dashboard.command("create")
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
@click.argument("dashboard_slug", required=True, type=str)
@click.argument("dashboard_name", required=True, type=str)
def create_dashboard(
    workspace_slug: str, app_slug: str, dashboard_slug: str, dashboard_name: str
) -> None:
    """Create a dashboard with DASHBOARD_SLUG and DASHBOARD_NAME within WORKSPACE_SLUG and APP_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The parent app's identifier.
        dashboard_slug: Identifier for the new dashboard (used in URLs).
        dashboard_name: The display name of the dashboard.
    """
    api_client.dashboard.create_dashboard(
        workspace_slug,
        app_slug,
        dashboard_slug,
        dashboard_name,
    )

    click.echo(
        f"Successfully created dashboard `{dashboard_slug}` with name `{dashboard_name}` within "
        f"app `{app_slug}` and workspace `{workspace_slug}`."
    )


@dashboard.command("update")
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
@click.argument("dashboard_slug", required=True, type=str)
@click.option("-s", "--slug", type=str, default=None, help="new slug.")
@click.option("-n", "--name", type=str, default=None, help="new name.")
def update_dashboard(
    workspace_slug: str,
    app_slug: str,
    dashboard_slug: str,
    slug: str | None,
    name: str | None,
) -> None:
    """Update the slug or name of a dashboard identified by DASHBOARD_SLUG within WORKSPACE_SLUG and APP_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The parent app's identifier.
        dashboard_slug: The dashboard's identifier.
        slug: New slug for the dashboard.
        name: New name for the dashboard.
    """
    if slug is None and name is None:
        msg = (
            "You must provide at least one of the following options:\n"
            "-s, --slug: new dashboard slug\n"
            "-n, --name: new dashboard name"
        )
        raise click.UsageError(msg)

    api_client.dashboard.update_dashboard(
        workspace_slug=workspace_slug,
        app_slug=app_slug,
        dashboard_slug=dashboard_slug,
        new_dashboard_slug=slug,
        new_dashboard_name=name,
    )

    msg = f"Successfully updated dashboard `{dashboard_slug}` within app `{app_slug}` and workspace `{workspace_slug}`:"

    if slug is not None:
        msg += f"\n- new slug: `{slug}`"
    if name is not None:
        msg += f"\n- new name: `{name}`"
    click.echo(msg)


@dashboard.command("trash")
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
@click.argument("dashboard_slug", required=True, type=str)
def trash_dashboard(workspace_slug: str, app_slug: str, dashboard_slug: str) -> None:
    """Move a dashboard with DASHBOARD_SLUG to trash within WORKSPACE_SLUG and APP_SLUG.

    NOTE: Once in the trash, you have 30 days to restore it otherwise it will be permanently deleted.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The parent app's identifier.
        dashboard_slug: The dashboard's identifier.
    """
    api_client.dashboard.trash_dashboard(workspace_slug, app_slug, dashboard_slug)

    click.echo(
        f"Successfully moved dashboard `{dashboard_slug}` to trash within "
        f"app `{app_slug}` and workspace `{workspace_slug}`."
    )


@dashboard.command("restore")
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
@click.argument("dashboard_slug", required=True, type=str)
def restore_dashboard(workspace_slug: str, app_slug: str, dashboard_slug: str) -> None:
    """Restore a dashboard with DASHBOARD_SLUG from trash within WORKSPACE_SLUG and APP_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The parent app's identifier.
        dashboard_slug: The dashboard's identifier.
    """
    api_client.dashboard.restore_dashboard(workspace_slug, app_slug, dashboard_slug)

    click.echo(
        f"Successfully restored dashboard `{dashboard_slug}` from trash within "
        f"app `{app_slug}` and workspace `{workspace_slug}`."
    )


@dashboard.command("rm")
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
@click.argument("dashboard_slug", required=True, type=str)
def delete_dashboard(workspace_slug: str, app_slug: str, dashboard_slug: str) -> None:
    """Delete a dashboard with DASHBOARD_SLUG permanently from trash within WORKSPACE_SLUG and APP_SLUG.

    \b
    NOTE:
    - The dashboard must be in the trash or have its parent app in the trash before it can be deleted permanently.
    - This action cannot be undone.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The parent app's identifier.
        dashboard_slug: The dashboard's identifier.
    """
    try:
        # First check if the dashboard still exists (if it does, it's not in trash)
        api_client.dashboard.get_dashboard(workspace_slug, app_slug, dashboard_slug)
    except APIServerError as err:
        if err.error_code != "NOT_FOUND":
            raise err
    else:
        # Dashboard still exists, so it's not in trash
        msg = (
            f"Dashboard `{dashboard_slug}` must be moved to trash before deletion.\n\n"
            "Please move the dashboard to trash first using: engineai dashboard trash"
        )
        raise click.ClickException(msg) from None

    # Dashboard is not found (either in trash, parent app in trash, or doesn't exist at all), proceed with deletion
    api_client.dashboard.delete_dashboard(workspace_slug, app_slug, dashboard_slug)

    click.echo(
        f"Successfully deleted dashboard `{dashboard_slug}` permanently from trash within "
        f"app `{app_slug}` and workspace `{workspace_slug}`."
    )


@dashboard.group("version", invoke_without_command=True)
def version() -> None:
    """Dashboard version commands."""


@version.command("ls")
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
@click.argument("dashboard_slug", required=True, type=str)
def list_dashboard_versions(
    workspace_slug: str, app_slug: str, dashboard_slug: str
) -> None:
    """List all versions of a dashboard identified by DASHBOARD_SLUG within WORKSPACE_SLUG and APP_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The parent app's identifier.
        dashboard_slug: The dashboard's identifier.
    """
    dashboard_versions = api_client.dashboard_version.list_dashboard_versions(
        workspace_slug, app_slug, dashboard_slug
    )

    if not dashboard_versions:
        click.echo(f"No versions found for dashboard `{dashboard_slug}`.")
        return

    console = Console()
    table = Table(
        title=f"Versions of dashboard '{dashboard_slug}'",
        show_header=True,
        show_edge=True,
    )
    table.add_column("Version")
    table.add_column("Active")
    for dv in dashboard_versions:
        table.add_row(dv.version, str(dv.active))

    console.print(table)


@dashboard.command("activate")
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
@click.argument("dashboard_slug", required=True, type=str)
@click.argument("version", required=True, type=str)
def activate_dashboard_version(
    workspace_slug: str, app_slug: str, dashboard_slug: str, version: str
) -> None:
    """Activate a VERSION of a dashboard identified by DASHBOARD_SLUG within WORKSPACE_SLUG and APP_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The parent app's identifier.
        dashboard_slug: The dashboard's identifier.
        version: The version of the dashboard to activate.
    """
    api_client.dashboard_version.activate_dashboard_version(
        workspace_slug,
        app_slug,
        dashboard_slug,
        version,
    )

    platform_url = (
        get_auth_token()["base_url"]
        .replace("api.", "platform.")
        .replace("http://localhost:4000", "https://localhost:3000")
    )

    click.echo(
        f"Dashboard `{dashboard_slug}` is live in version `{version}`.\n"
        "You can access it at: "
        f"{platform_url}/"
        f"workspaces/{workspace_slug}"
        f"/apps/{app_slug}/dashboards/{dashboard_slug}.",
    )


@dashboard.command("deactivate")
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
@click.argument("dashboard_slug", required=True, type=str)
@click.argument("version", required=True, type=str)
def deactivate_dashboard_version(
    workspace_slug: str, app_slug: str, dashboard_slug: str, version: str
) -> None:
    """Deactivate a VERSION of a dashboard identified by DASHBOARD_SLUG within WORKSPACE_SLUG and APP_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The parent app's identifier.
        dashboard_slug: The dashboard's identifier.
        version: The version of the dashboard to deactivate.
    """
    api_client.dashboard_version.deactivate_dashboard_version(
        workspace_slug,
        app_slug,
        dashboard_slug,
        version,
    )

    click.echo(
        f"Successfully deactivated version `{version}`. The dashboard `{dashboard_slug}` is now a draft.",
    )


@version.command("rm")
@click.argument("workspace_slug", required=True, type=str)
@click.argument("app_slug", required=True, type=str)
@click.argument("dashboard_slug", required=True, type=str)
@click.argument("version", required=True, type=str)
def delete_dashboard_version(
    workspace_slug: str,
    app_slug: str,
    dashboard_slug: str,
    version: str,
) -> None:
    """Delete a VERSION from a dashboard identified by DASHBOARD_SLUG within WORKSPACE_SLUG and APP_SLUG.

    \f
    Args:
        workspace_slug: The parent workspace's identifier.
        app_slug: The parent app's identifier.
        dashboard_slug: The dashboard's identifier.
        version: The version of the dashboard to delete.
    """
    api_client.dashboard_version.delete_dashboard_version(
        workspace_slug,
        app_slug,
        dashboard_slug,
        version,
    )

    click.echo(
        f"Successfully deleted version `{version}` from dashboard `{dashboard_slug}`."
    )
