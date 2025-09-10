"""Cli main file."""

import sys

import click

from engineai.sdk import __version__
from engineai.sdk.api.auth import AuthenticationError
from engineai.sdk.api.graphql_client import APIServerError
from engineai.sdk.cli.commands import app as app_cmd
from engineai.sdk.cli.commands import dashboard as dashboard_cmd
from engineai.sdk.cli.commands import group as group_cmd
from engineai.sdk.cli.commands import workspace as workspace_cmd
from engineai.sdk.cli.commands.auth import login


@click.group()
@click.version_option(
    __version__,
    package_name="engineai.sdk",
    message="EngineAI's Platform SDK v%(version)s",
)
def cli() -> None:
    """Platform SDK Command Line Interface."""


def main() -> None:
    """Platform SDK Command Line entrypoint."""
    try:
        cli()
    except (AuthenticationError, APIServerError) as err:
        click.echo("Error: " + str(err).capitalize(), err=True)
        sys.exit(1)


cli.add_command(login)
cli.add_command(dashboard_cmd.dashboard)
cli.add_command(app_cmd.app)
cli.add_command(workspace_cmd.workspace)
cli.add_command(group_cmd.group)
