import click

from . import authenticate, collect


@click.group()
def cli():
    # This is the entry point of the CLI. New commands should be added via the
    # `add_command` function in the `cli` group as seen below.
    pass


cli.add_command(collect.collect)
cli.add_command(authenticate.authenticate)
