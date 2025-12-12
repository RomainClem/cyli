"""Main CLI entry point."""
import click
from cyli.commands import hello, test

@click.group()
def cli():
    """Cyli - Your CLI application."""
    pass


# Register commands
cli.add_command(hello)
cli.add_command(test)
