"""Test command implementation."""

import subprocess
import click

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


def display_test_files(test_files: list, test_type: str) -> None:
    """Display the list of test files."""
    click.echo()
    click.echo(f"Test files for '{test_type}':")
    click.echo("-" * 40)
    
    if not test_files:
        click.echo("  No test files found.")
    else:
        for i, test_file in enumerate(test_files, 1):
            click.echo(f"  {i}. {test_file}")
        click.echo()
        click.echo(f"Total: {len(test_files)} test file(s)")
    
    click.echo()


def prompt_test_selection(test_files: list) -> list:
    """Prompt user to select which test files to run.
    
    Returns:
        List of selected test file paths
    """
    if not test_files:
        return []
    
    click.echo("Enter test number(s) to run (comma-separated), 'all' to run all, or 'q' to quit:")
    selection = click.prompt("Selection", default="all")
    
    if selection.lower() == "q":
        raise SystemExit(0)
    
    if selection.lower() == "all":
        return test_files
    
    # Parse comma-separated numbers
    selected = []
    try:
        indices = [int(x.strip()) for x in selection.split(",")]
        for idx in indices:
            if 1 <= idx <= len(test_files):
                selected.append(test_files[idx - 1])
            else:
                click.echo(f"Warning: {idx} is out of range, skipping.", err=True)
    except ValueError:
        click.echo("Invalid selection. Please enter numbers separated by commas.", err=True)
        raise SystemExit(1)
    
    return selected


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
@click.option(
    "--all", "-a",
    "run_all",
    is_flag=True,
    help="Run all tests without prompting for selection.",
)
def test(test_type: str | None, dry_run: bool, list_only: bool, run_all: bool):
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
    
    # If no type specified, prompt user to choose
    if test_type is None:
        click.echo("Available test types:")
        for i, t in enumerate(available_types, 1):
            script_name = test_scripts[t]
            click.echo(f"  {i}. {t} ({script_name})")
        
        choice = click.prompt(
            "Select test type",
            type=click.Choice(available_types, case_sensitive=False),
        )
        test_type = choice
    
    # Validate test type exists in config
    if test_type not in test_scripts:
        click.echo(f"Unknown test type: {test_type}", err=True)
        click.echo(f"Available types: {', '.join(available_types)}", err=True)
        raise SystemExit(1)
    
    # Get and display test files
    test_files = get_test_files(test_type)
    display_test_files(test_files, test_type)
    
    # If list-only, stop here
    if list_only:
        return
    
    if not test_files:
        click.echo("No tests to run.", err=True)
        raise SystemExit(1)
    
    # Select which tests to run
    if run_all:
        selected_tests = test_files
    else:
        selected_tests = prompt_test_selection(test_files)
    
    if not selected_tests:
        click.echo("No tests selected.")
        return
    
    # Run each selected test
    base_cmd = config.script_runner.get_test_command(test_type)
    
    for test_file in selected_tests:
        # Build command: base_cmd -- -- --spec "file_path"
        cmd = base_cmd + ["--", "--", "--spec", str(test_file)]
        cmd_str = " ".join(cmd[:-1]) + f' "{cmd[-1]}"'
        
        if dry_run:
            click.echo(f"Would run: {cmd_str}")
            continue
        
        click.echo(f"Running: {cmd_str}")
        click.echo()
        
        # Execute the command
        try:
            result = subprocess.run(cmd, check=False)
            if result.returncode != 0:
                click.echo(f"Test failed with exit code: {result.returncode}", err=True)
                if len(selected_tests) > 1:
                    if not click.confirm("Continue with remaining tests?", default=True):
                        raise SystemExit(result.returncode)
        except FileNotFoundError:
            click.echo(f"Command not found: {cmd[0]}", err=True)
            click.echo("Make sure the package manager is installed.", err=True)
            raise SystemExit(1)
