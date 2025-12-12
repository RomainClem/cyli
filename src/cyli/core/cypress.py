"""Cypress test discovery and management."""

from pathlib import Path

from cyli.utils import find_project_root


# Default Cypress folder name
CYPRESS_FOLDER = "cypress"

# Test type folders within Cypress
TEST_FOLDERS = {
    "e2e": "e2e",
    "component": "component",
}


def find_cypress_folder(start_path: Path | None = None) -> Path | None:
    """Find the Cypress folder in the project.
    
    Args:
        start_path: Starting directory to search from (defaults to cwd)
        
    Returns:
        Path to the Cypress folder if found, None otherwise
    """
    project_root = find_project_root(start_path=start_path)
    if project_root is None:
        return None
    
    cypress_path = project_root / CYPRESS_FOLDER
    if cypress_path.exists() and cypress_path.is_dir():
        return cypress_path
    
    return None


def find_test_folder(test_type: str, start_path: Path | None = None) -> Path | None:
    """Find a specific test type folder within Cypress.
    
    Args:
        test_type: Type of tests to find ("e2e", "component")
        start_path: Starting directory to search from (defaults to cwd)
        
    Returns:
        Path to the test folder if found, None otherwise
    """
    if test_type not in TEST_FOLDERS:
        raise ValueError(f"Unknown test type: {test_type}. Available: {list(TEST_FOLDERS.keys())}")
    
    cypress_folder = find_cypress_folder(start_path)
    if cypress_folder is None:
        return None
    
    test_folder = cypress_folder / TEST_FOLDERS[test_type]
    if test_folder.exists() and test_folder.is_dir():
        return test_folder
    
    return None


def find_e2e_folder(start_path: Path | None = None) -> Path | None:
    """Find the e2e test folder within Cypress.
    
    Args:
        start_path: Starting directory to search from (defaults to cwd)
        
    Returns:
        Path to the e2e folder if found, None otherwise
    """
    return find_test_folder("e2e", start_path)


def find_component_folder(start_path: Path | None = None) -> Path | None:
    """Find the component test folder within Cypress.
    
    Args:
        start_path: Starting directory to search from (defaults to cwd)
        
    Returns:
        Path to the component folder if found, None otherwise
    """
    return find_test_folder("component", start_path)


def list_test_files(
    test_type: str,
    pattern: str = "**/*.cy.{ts,js,tsx,jsx}",
    start_path: Path | None = None,
) -> list[Path]:
    """List all test files of a specific type.
    
    Args:
        test_type: Type of tests to find ("e2e", "component")
        pattern: Glob pattern to match test files
        start_path: Starting directory to search from (defaults to cwd)
        
    Returns:
        List of paths to test files
    """
    test_folder = find_test_folder(test_type, start_path)
    if test_folder is None:
        return []
    
    # Handle brace expansion manually since pathlib doesn't support it
    files: list[Path] = []
    for ext in ["ts", "js", "tsx", "jsx"]:
        files.extend(test_folder.glob(f"**/*.cy.{ext}"))
    
    return sorted(files)


def list_e2e_tests(start_path: Path | None = None) -> list[Path]:
    """List all e2e test files.
    
    Args:
        start_path: Starting directory to search from (defaults to cwd)
        
    Returns:
        List of paths to e2e test files
    """
    return list_test_files("e2e", start_path=start_path)


def list_component_tests(start_path: Path | None = None) -> list[Path]:
    """List all component test files.
    
    Args:
        start_path: Starting directory to search from (defaults to cwd)
        
    Returns:
        List of paths to component test files
    """
    return list_test_files("component", start_path=start_path)


def find_src_folder(start_path: Path | None = None) -> Path | None:
    """Find the src folder in the project.
    
    Args:
        start_path: Starting directory to search from (defaults to cwd)
        
    Returns:
        Path to the src folder if found, None otherwise
    """
    project_root = find_project_root(start_path=start_path)
    if project_root is None:
        return None
    
    src_path = project_root / "src"
    if src_path.exists() and src_path.is_dir():
        return src_path
    
    return None


def list_src_test_files(
    pattern: str = "*.cy.ts",
    start_path: Path | None = None,
) -> list[Path]:
    """List all Cypress test files in the src folder.
    
    Searches recursively through the src folder for files matching
    the pattern (default: *.cy.ts).
    
    Args:
        pattern: Glob pattern to match test files (default: "*.cy.ts")
        start_path: Starting directory to search from (defaults to cwd)
        
    Returns:
        List of paths to test files in src
    """
    src_folder = find_src_folder(start_path)
    if src_folder is None:
        return []
    
    files = list(src_folder.glob(f"**/{pattern}"))
    return sorted(files)
