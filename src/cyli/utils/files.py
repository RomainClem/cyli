"""File system utilities for cyli."""

from pathlib import Path


def find_file_upwards(filename: str, start_path: Path | None = None) -> Path | None:
    """Find a file by searching up the directory tree.
    
    Args:
        filename: Name of the file to find
        start_path: Starting directory to search from (defaults to cwd)
        
    Returns:
        Path to the file if found, None otherwise
    """
    if start_path is None:
        start_path = Path.cwd()
    
    current = start_path.resolve()
    
    while current != current.parent:
        file_path = current / filename
        if file_path.exists():
            return file_path
        current = current.parent
    
    # Check root as well
    file_path = current / filename
    if file_path.exists():
        return file_path
    
    return None


def find_project_root(
    marker_files: list[str] | None = None,
    start_path: Path | None = None,
) -> Path | None:
    """Find the project root by looking for marker files.
    
    Args:
        marker_files: List of filenames that indicate project root
                     (defaults to common project files)
        start_path: Starting directory to search from (defaults to cwd)
        
    Returns:
        Path to the project root if found, None otherwise
    """
    if marker_files is None:
        marker_files = [
            "package.json",
            "pyproject.toml",
            "setup.py",
            "Cargo.toml",
            "go.mod",
            ".git",
        ]
    
    if start_path is None:
        start_path = Path.cwd()
    
    current = start_path.resolve()
    
    while current != current.parent:
        for marker in marker_files:
            if (current / marker).exists():
                return current
        current = current.parent
    
    # Check root as well
    for marker in marker_files:
        if (current / marker).exists():
            return current
    
    return None
