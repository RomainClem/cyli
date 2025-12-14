"""Configuration module for cyli CLI tool."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cyli.utils import find_file_upwards


# Common package manager configurations
PACKAGE_MANAGERS = {
    "npm": {"command": "npm", "run_prefix": "run"},
    "yarn": {"command": "yarn", "run_prefix": ""},  # yarn doesn't need "run"
    "pnpm": {"command": "pnpm", "run_prefix": "run"},
    "bun": {"command": "bun", "run_prefix": "run"},
}


@dataclass
class ScriptRunnerConfig:
    """Configuration for script execution (npm, yarn, pnpm, bun, etc.)."""
    
    # The command to use (e.g., "npm", "pnpm", "yarn", "bun")
    command: str = "npm"
    
    # Prefix for running scripts (e.g., "run" for npm/pnpm, empty for yarn)
    run_prefix: str = "run"
    
    # Script categories with their mappings
    scripts: dict[str, dict[str, str]] = field(default_factory=lambda: {
        "test": {
            "component": "coverage:component",
            "e2e": "coverage:e2e",
        }
    })
    
    @classmethod
    def for_package_manager(cls, name: str, scripts: dict[str, dict[str, str]] | None = None) -> "ScriptRunnerConfig":
        """Create a config for a known package manager.
        
        Args:
            name: Package manager name (npm, yarn, pnpm, bun)
            scripts: Optional custom scripts mapping
            
        Returns:
            ScriptRunnerConfig configured for the package manager
        """
        if name not in PACKAGE_MANAGERS:
            raise ValueError(f"Unknown package manager: {name}. Available: {list(PACKAGE_MANAGERS.keys())}")
        
        pm = PACKAGE_MANAGERS[name]
        return cls(
            command=pm["command"],
            run_prefix=pm["run_prefix"],
            scripts=scripts or cls().scripts,
        )
    
    def get_command(self, category: str, script_key: str) -> list[str]:
        """Get the full command to run a script.
        
        Args:
            category: The script category 
            script_key: The key within the category (e.g., "component", "e2e")
            
        Returns:
            List of command parts to execute
        """
        if category not in self.scripts:
            raise ValueError(f"Unknown category: {category}. Available: {list(self.scripts.keys())}")
        
        category_scripts = self.scripts[category]
        script = category_scripts.get(script_key)
        if not script:
            raise ValueError(f"Unknown script '{script_key}' in category '{category}'. Available: {list(category_scripts.keys())}")
        
        if self.run_prefix:
            return [self.command, self.run_prefix, script]
        return [self.command, script]
    
    def get_test_command(self, test_type: str) -> list[str]:
        """Get the full command to run a test script.
        
        Args:
            test_type: The type of test (e.g., "component", "e2e")
            
        Returns:
            List of command parts to execute
        """
        return self.get_command("test", test_type)


@dataclass
class Config:
    """Main configuration for cyli."""
    
    script_runner: ScriptRunnerConfig = field(default_factory=ScriptRunnerConfig)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        """Create a Config instance from a dictionary."""
        runner_data = data.get("script_runner", {})
        
        # Support shorthand: if "package_manager" is specified, use presets
        if "package_manager" in runner_data:
            pm_name = runner_data["package_manager"]
            scripts = runner_data.get("scripts", None)
            runner_config = ScriptRunnerConfig.for_package_manager(pm_name, scripts)
        else:
            runner_config = ScriptRunnerConfig(
                command=runner_data.get("command", "npm"),
                run_prefix=runner_data.get("run_prefix", "run"),
                scripts=runner_data.get("scripts", ScriptRunnerConfig().scripts),
            )
        
        return cls(script_runner=runner_config)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert the config to a dictionary."""
        return {
            "script_runner": {
                "command": self.script_runner.command,
                "run_prefix": self.script_runner.run_prefix,
                "scripts": self.script_runner.scripts,
            }
        }


# Default config file name
CONFIG_FILE_NAME = "cyli.json"


def find_config_file(start_path: Path | None = None) -> Path | None:
    """Find the config file by searching up the directory tree.
    
    Args:
        start_path: Starting directory to search from (defaults to cwd)
        
    Returns:
        Path to the config file if found, None otherwise
    """
    return find_file_upwards(CONFIG_FILE_NAME, start_path)


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from a file.
    
    Args:
        config_path: Path to the config file. If None, searches for it.
        
    Returns:
        Config instance (default if no config file found)
    """
    if config_path is None:
        config_path = find_config_file()
    
    if config_path is None or not config_path.exists():
        return Config()
    
    with open(config_path) as f:
        data = json.load(f)
    
    return Config.from_dict(data)


def save_config(config: Config, config_path: Path | None = None) -> Path:
    """Save configuration to a file.
    
    Args:
        config: Config instance to save
        config_path: Path to save to (defaults to cwd/cyli.json)
        
    Returns:
        Path where the config was saved
    """
    if config_path is None:
        config_path = Path.cwd() / CONFIG_FILE_NAME
    
    with open(config_path, "w") as f:
        json.dump(config.to_dict(), f, indent=2)
    
    return config_path


def create_default_config(path: Path | None = None) -> Path:
    """Create a default config file.
    
    Args:
        path: Directory to create the config in (defaults to cwd)
        
    Returns:
        Path to the created config file
    """
    if path is None:
        path = Path.cwd()
    
    config_path = path / CONFIG_FILE_NAME
    return save_config(Config(), config_path)
