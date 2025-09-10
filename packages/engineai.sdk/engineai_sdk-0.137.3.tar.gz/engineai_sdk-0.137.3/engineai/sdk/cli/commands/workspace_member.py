"""workspace member command for engineai CLI."""

import click
from rich.console import Console
from rich.table import Table

from engineai.sdk.api.client import api_client

WORKSPACE_ROLE = ["ADMIN", "MEMBER"]


@click.group()
def member() -> None:
    """Workspace member commands."""


@member.command("invite")
@click.argument(
    "slug",
    required=True,
    type=str,
)
@click.argument(
    "email",
    required=True,
    type=str,
)
@click.argument(
    "role",
    required=True,
    type=click.Choice(WORKSPACE_ROLE, case_sensitive=False),
)
def invite_workspace_member(slug: str, email: str, role: str) -> None:
    """Invite a user with EMAIL and ROLE to the workspace identified by SLUG.

    \f
    Args:
        slug: The workspace's identifier.
        email: Email of the user to be added.
        role: Role for the user in the workspace (ADMIN or MEMBER).
    """
    member_role = role.upper()

    workspace_member = api_client.workspace_member.invite_workspace_member(
        slug, email, member_role
    )

    if not workspace_member:
        click.echo(f"User `{email}` is already a member of the workspace `{slug}`.")
        return

    click.echo(
        f"Successfully invited user `{email}` to the workspace `{slug}` with role "
        f"`{member_role}`.",
    )


@member.command("update")
@click.argument(
    "slug",
    required=True,
    type=str,
)
@click.argument(
    "email",
    required=True,
    type=str,
)
@click.argument(
    "role",
    required=True,
    type=click.Choice(WORKSPACE_ROLE, case_sensitive=False),
)
def update_workspace_member_role(slug: str, email: str, role: str) -> None:
    """Update member with EMAIL to new ROLE in the workspace identified by SLUG.

    \f
    Args:
        slug: The workspace's identifier.
        email: Email of the user to be updated.
        role: New role for the user in the workspace (ADMIN or MEMBER).
    """
    member_role = role.upper()

    api_client.workspace_member.update_workspace_member(slug, email, member_role)

    click.echo(
        f"Successfully updated user `{email}`'s role to `{member_role}` "
        f"in the workspace `{slug}`.",
    )


@member.command("rm")
@click.argument(
    "slug",
    required=True,
    type=str,
)
@click.argument(
    "email",
    required=True,
    type=str,
)
def remove_workspace_member(slug: str, email: str) -> None:
    """Remove member with EMAIL from workspace identified by SLUG.

    \f
    Args:
        slug: The workspace's identifier.
        email: Email of the user to be removed.
    """
    api_client.workspace_member.remove_workspace_member(slug, email)

    click.echo(f"Successfully removed user `{email}` from the workspace `{slug}`.")


@member.command("ls")
@click.argument(
    "slug",
    required=True,
    type=str,
)
def list_workspace_members(slug: str) -> None:
    """List all members in a workspace with SLUG.

    \f
    Args:
        slug: The workspace's identifier
    """
    workspace_members = api_client.workspace_member.list_workspace_members(slug)

    console = Console()
    table = Table(
        title=f"Members of workspace '{slug}'",
        show_header=True,
        show_edge=True,
    )

    table.add_column("Member")
    table.add_column("Role")
    table.add_section()
    for m in workspace_members:
        table.add_row(m.email + (" (invited)" if m.is_invitee else ""), m.role)
    console.print(table)


@member.command("transfer")
@click.argument(
    "slug",
    required=True,
    type=str,
)
@click.argument(
    "email",
    required=True,
    type=str,
)
def transfer_workspace(slug: str, email: str) -> None:
    """Transfer workspace identified by SLUG to an admin with EMAIL.

    \f
    Args:
        slug: The workspace's identifier.
        email: Email of the user (admin) to whom the workspace will be transferred.
    """
    api_client.workspace_member.transfer_workspace_ownership(slug, email)

    click.echo(f"Successfully transferred workspace `{slug}` to user `{email}`.")
