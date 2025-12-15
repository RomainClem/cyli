"""Test command implementation."""

import subprocess
import click
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, OptionList, Static
from textual.widgets.option_list import Option
from textual.binding import Binding

from cyli.config import load_config
from cyli.core import list_test_files, list_src_test_files


def get_test_files(test_type: str) -> list:
    """Get all test files for the given test type."""
    # Get tests from cypress folder
    cypress_tests = list_test_files(test_type)
    
    # For component tests, also check src folder
    src_tests: list = []
    if test_type == "component":
        src_tests = list_src_test_files()
    
    return cypress_tests + src_tests


class TestTypeSelector(App[str | None]):
    """App for selecting test type."""
    
    CSS = """
    OptionList {
        height: auto;
        max-height: 20;
        margin: 1;
    }
    #title {
        text-align: center;
        padding: 1;
        text-style: bold;
    }
    """
    
    BINDINGS = [
        Binding("escape", "quit", "Cancel"),
        Binding("enter", "select", "Select"),
    ]
    
    def __init__(self, available_types: list[str], test_scripts: dict[str, str]):
        super().__init__()
        self.available_types = available_types
        self.test_scripts = test_scripts
        self.selected_type: str | None = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("🧪 Select test type:", id="title")
        yield OptionList(
            *[
                Option(f"{t} ({self.test_scripts[t]})", id=t)
                for t in self.available_types
            ]
        )
        yield Footer()
    
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.selected_type = str(event.option.id)
        self.exit(self.selected_type)
    
    def action_quit(self) -> None:
        self.exit(None)


class TestFileSelector(App[str | None]):
    """App for selecting a single test file."""
    
    CSS = """
    OptionList {
        height: auto;
        max-height: 30;
        margin: 1;
    }
    #title {
        text-align: center;
        padding: 1;
        text-style: bold;
    }
    """
    
    BINDINGS = [
        Binding("escape", "quit", "Cancel"),
        Binding("enter", "select", "Select"),
    ]
    
    def __init__(self, test_files: list, test_type: str):
        super().__init__()
        self.test_files = test_files
        self.test_type = test_type
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"📁 Select test file for '{self.test_type}':", id="title")
        yield OptionList(
            *[
                Option(str(f), id=str(f))
                for f in self.test_files
            ]
        )
        yield Footer()
    
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.exit(str(event.option.id))
    
    def action_quit(self) -> None:
        self.exit(None)


def select_test_type(available_types: list[str], test_scripts: dict[str, str]) -> str | None:
    """Prompt user to select test type using arrow keys."""
    app = TestTypeSelector(available_types, test_scripts)
    return app.run()


def select_test_file(test_files: list, test_type: str) -> str | None:
    """Prompt user to select a single test file to run."""
    if not test_files:
        return None
    
    app = TestFileSelector(test_files, test_type)
    return app.run()


@click.command()
@click.option(
    "--type", "-t",
    "test_type",
    type=click.Choice(["component", "e2e"], case_sensitive=False),
    help="Type of test to run (component or e2e).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Print the command without executing it.",
)
@click.option(
    "--list-only", "-l",
    is_flag=True,
    help="Only list the test files without running them.",
)
def test(test_type: str | None, dry_run: bool, list_only: bool):
    """Run Cypress tests (component or e2e).
    
    If no test type is specified, you will be prompted to choose.
    """
    config = load_config()
    
    # Get available test types from config
    test_scripts = config.script_runner.scripts.get("test", {})
    
    if not test_scripts:
        click.echo("No test scripts configured.", err=True)
        raise SystemExit(1)
    
    available_types = list(test_scripts.keys())
    
    # If no type specified, prompt user to choose with arrow keys
    if test_type is None:
        test_type = select_test_type(available_types, test_scripts)
        if test_type is None:
            raise SystemExit(0)
    
    # Validate test type exists in config
    if test_type not in test_scripts:
        click.echo(f"Unknown test type: {test_type}", err=True)
        click.echo(f"Available types: {', '.join(available_types)}", err=True)
        raise SystemExit(1)
    
    # Get test files
    test_files = get_test_files(test_type)
    
    # If list-only, display and stop
    if list_only:
        click.echo()
        click.echo(f"Test files for '{test_type}':")
        click.echo("-" * 40)
        if not test_files:
            click.echo("  No test files found.")
        else:
            for f in test_files:
                click.echo(f"  • {f}")
            click.echo()
            click.echo(f"Total: {len(test_files)} test file(s)")
        return
    
    if not test_files:
        click.echo("No test files found.", err=True)
        raise SystemExit(1)
    
    # Select which test to run
    selected_test = select_test_file(test_files, test_type)
    
    if not selected_test:
        click.echo("No test selected.")
        return
    
    click.echo()
    click.echo(f"Selected: {selected_test}")
    click.echo()
    
    # Run the selected test
    base_cmd = config.script_runner.get_test_command(test_type)
    
    # Build command: base_cmd -- -- --spec "file_path"
    cmd = base_cmd + ["--", "--", "--spec", str(selected_test)]
    cmd_str = " ".join(cmd[:-1]) + f' "{cmd[-1]}"'
    
    if dry_run:
        click.echo(f"Would run: {cmd_str}")
        return
    
    click.echo(f"Running: {cmd_str}")
    click.echo()
    
    # Execute the command
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            click.echo(f"Test failed with exit code: {result.returncode}", err=True)
            raise SystemExit(result.returncode)
    except FileNotFoundError:
        click.echo(f"Command not found: {cmd[0]}", err=True)
        click.echo("Make sure the package manager is installed.", err=True)
        raise SystemExit(1)
