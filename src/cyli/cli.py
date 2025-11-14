"""Main CLI entry point."""
import click
from cyli.commands import hello

@click.group()
def cli():
    """Cyli - Your CLI application."""
    pass


# Register commands
cli.add_command(hello)
