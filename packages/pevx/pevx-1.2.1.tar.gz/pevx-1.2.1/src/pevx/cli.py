#!/usr/bin/env python3
import click

from pevx.commands import docker_proxy, uv_proxy


@click.group()
@click.version_option()
def cli():
    """Prudentia CLI - Development tools for Prudentia internal developers."""
    pass


cli.add_command(uv_proxy)

cli.add_command(docker_proxy)

if __name__ == "__main__":
    cli()
