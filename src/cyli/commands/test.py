"""Test command implementation."""

import subprocess
import click
from InquirerPy import inquirer
from InquirerPy.separator import Separator

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


def select_test_type(available_types: list[str], test_scripts: dict[str, str]) -> str | None:
    """Prompt user to select test type using arrow keys."""
    choices = [
        {"name": f"{t} ({test_scripts[t]})", "value": t}
        for t in available_types
    ]
    
    result = inquirer.select(
        message="Select test type:",
        choices=choices,
        pointer="❯",
        qmark="🧪",
    ).execute()
    
    return result


def select_test_files(test_files: list, test_type: str) -> list:
    """Prompt user to select which test files to run using arrow keys."""
    if not test_files:
        return []
    
    choices = [
        {"name": str(f), "value": f}
        for f in test_files
    ]
    
    # Add "Run all" option at the top
    choices.insert(0, Separator("─" * 40))
    choices.insert(0, {"name": "✅ Run all tests", "value": "__all__"})
    
    result = inquirer.checkbox(
        message=f"Select test files for '{test_type}' (Space to select, Enter to confirm):",
        choices=choices,
        pointer="❯",
        qmark="📁",
        instruction="(Use arrow keys, Space to select, Enter to confirm)",
    ).execute()
    
    # If "Run all" was selected, return all test files
    if "__all__" in result:
        return test_files
    
    return result


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
    
    # Select which tests to run
    if run_all:
        selected_tests = test_files
    else:
        selected_tests = select_test_files(test_files, test_type)
    
    if not selected_tests:
        click.echo("No tests selected.")
        return
    
    click.echo()
    click.echo(f"Selected {len(selected_tests)} test(s)")
    click.echo()
    
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
