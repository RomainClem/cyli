"""Main CLI entry point."""
import click
from cyli.commands import  test

@click.group()
def cli():
    """Cyli - Your CLI application."""
    pass


# Register commands
cli.add_command(test)
