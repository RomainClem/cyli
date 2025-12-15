"""Test command implementation."""

import asyncio
from pathlib import Path
import click
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, OptionList, Static, RichLog
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
                Option(Path(f).stem, id=str(f))
                for f in self.test_files
            ]
        )
        yield Footer()
    
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.exit(str(event.option.id))
    
    def action_quit(self) -> None:
        self.exit(None)


class TestRunnerApp(App[None]):
    """App for selecting and running tests with live output."""
    
    CSS = """
    #main-container {
        layout: horizontal;
    }
    
    #test-list-panel {
        width: 1fr;
        border: solid $primary;
        height: 100%;
    }
    
    #output-panel {
        width: 3fr;
        border: solid $secondary;
        height: 100%;
    }
    
    #test-list-title {
        text-align: center;
        padding: 1;
        text-style: bold;
        background: $primary-background;
    }
    
    #output-title {
        text-align: center;
        padding: 1;
        text-style: bold;
        background: $secondary-background;
    }
    
    OptionList {
        height: 1fr;
    }
    
    RichLog {
        height: 1fr;
        scrollbar-gutter: stable;
    }
    
    #status-bar {
        height: 1;
        background: $surface;
        color: $text-muted;
        padding: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "quit", "Quit"),
        Binding("q", "quit", "Quit"),
    ]
    
    def __init__(self, test_files: list, test_type: str, base_cmd: list[str]):
        super().__init__()
        self.test_files = test_files
        self.test_type = test_type
        self.base_cmd = base_cmd
        self.current_process: asyncio.subprocess.Process | None = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            with Vertical(id="test-list-panel"):
                yield Static(f"📁 {self.test_type} tests", id="test-list-title")
                yield OptionList(
                    *[
                        Option(Path(f).stem, id=str(f))
                        for f in self.test_files
                    ],
                    id="test-list"
                )
            with Vertical(id="output-panel"):
                yield Static("📋 Output", id="output-title")
                yield RichLog(id="output-log", highlight=True, markup=True)
        yield Static("Ready. Select a test to run.", id="status-bar")
        yield Footer()
    
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle test selection and run the test."""
        test_file = str(event.option.id)
        self.run_test(test_file)
    
    def run_test(self, test_file: str) -> None:
        """Run the selected test and stream output."""
        output_log = self.query_one("#output-log", RichLog)
        status_bar = self.query_one("#status-bar", Static)
        
        # Clear previous output
        output_log.clear()
        
        # Build command
        cmd = self.base_cmd + ["--", "--", "--spec", test_file]
        cmd_str = " ".join(cmd[:-1]) + f' "{cmd[-1]}"'
        
        output_log.write(f"[bold blue]Running:[/bold blue] {cmd_str}\n")
        output_log.write("-" * 60 + "\n")
        status_bar.update(f"Running: {Path(test_file).stem}...")
        
        # Run command asynchronously
        self.run_worker(self._run_command(cmd, test_file), exclusive=True)
    
    async def _run_command(self, cmd: list[str], test_file: str) -> None:
        """Run command and stream output to the log."""
        output_log = self.query_one("#output-log", RichLog)
        status_bar = self.query_one("#status-bar", Static)
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            self.current_process = process
            
            # Stream output
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                decoded_line = line.decode("utf-8", errors="replace").rstrip()
                output_log.write(decoded_line)
            
            await process.wait()
            
            output_log.write("\n" + "-" * 60)
            if process.returncode == 0:
                output_log.write("\n[bold green]✓ Test passed[/bold green]")
                status_bar.update(f"✓ {Path(test_file).stem} passed. Select another test to run.")
            else:
                output_log.write(f"\n[bold red]✗ Test failed (exit code: {process.returncode})[/bold red]")
                status_bar.update(f"✗ {Path(test_file).stem} failed. Select another test to run.")
                
        except FileNotFoundError:
            output_log.write(f"\n[bold red]Error: Command not found: {cmd[0]}[/bold red]")
            output_log.write("\nMake sure the package manager is installed.")
            status_bar.update("Error: Command not found")
        except Exception as e:
            output_log.write(f"\n[bold red]Error: {e}[/bold red]")
            status_bar.update(f"Error: {e}")
        finally:
            self.current_process = None
    
    def action_quit(self) -> None:
        """Quit the app, cancelling any running process."""
        if self.current_process:
            self.current_process.terminate()
        self.exit(None)


def select_test_type(available_types: list[str], test_scripts: dict[str, str]) -> str | None:
    """Prompt user to select test type using arrow keys."""
    app = TestTypeSelector(available_types, test_scripts)
    return app.run()


def run_test_runner(test_files: list, test_type: str, base_cmd: list[str]) -> None:
    """Run the interactive test runner app."""
    app = TestRunnerApp(test_files, test_type, base_cmd)
    app.run()


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
    
    # Get the base command for running tests
    base_cmd = config.script_runner.get_test_command(test_type)
    
    if dry_run:
        click.echo("Dry run mode - showing command format:")
        cmd_str = " ".join(base_cmd) + ' -- -- --spec "<test_file>"'
        click.echo(f"  {cmd_str}")
        return
    
    # Launch the interactive test runner
    run_test_runner(test_files, test_type, base_cmd)
