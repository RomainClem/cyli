"""Main CLI entry point."""
import click
from cyli.commands.hello import hello


@click.group()
def cli():
    """Cyli - Your CLI application."""
    pass


# Register commands
cli.add_command(hello)
