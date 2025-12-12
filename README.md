# Cyli

A CLI tool for managing and running Cypress tests with ease. Cyli helps you discover, select, and run Cypress component and e2e tests from any project directory.

## Features

- 🔍 **Auto-discovery** - Automatically finds Cypress test files in your project
- 🎯 **Selective testing** - Choose specific test files to run
- ⚙️ **Configurable** - Support for npm, yarn, pnpm, and bun
- 📁 **Smart search** - Finds tests in both `cypress/` and `src/` folders

## Installation

### Using UV (Recommended)

#### Install globally as a tool

```bash
# Install from the repository
uv tool install git+https://github.com/yourusername/cyli.git

# Or install locally in editable mode (for development)
cd /path/to/cyli
uv tool install -e .
```

#### Install in a project

```bash
uv add cyli
```

### Verify Installation

```bash
cyli --help
```

## Quick Start

1. Navigate to your Cypress project:
   ```bash
   cd /path/to/your/cypress-project
   ```

2. Run tests interactively:
   ```bash
   cyli test
   ```

3. The CLI will:
   - Prompt you to select test type (component or e2e)
   - Display available test files
   - Let you select which tests to run

## Usage

### Running Tests

```bash
# Interactive mode - prompts for test type and file selection
cyli test

# Specify test type directly
cyli test --type component
cyli test -t e2e

# Run all tests without prompting
cyli test --type component --all
cyli test -t e2e -a

# List test files without running
cyli test --list-only
cyli test -l

# Preview command without executing (dry run)
cyli test --dry-run
```

### Example Session

```
$ cyli test

Available test types:
  1. component (coverage:component)
  2. e2e (coverage:e2e)
Select test type: component

Test files for 'component':
----------------------------------------
  1. /home/user/project/cypress/component/Button.cy.ts
  2. /home/user/project/src/components/Form.cy.tsx
  3. /home/user/project/src/hooks/useAuth.cy.ts

Total: 3 test file(s)

Enter test number(s) to run (comma-separated), 'all' to run all, or 'q' to quit:
Selection: 1,3

Running: npm run coverage:component -- -- --spec "/home/user/project/cypress/component/Button.cy.ts"
```

## Configuration

Cyli looks for a `cyli.json` configuration file in your project root (or any parent directory).

### Create a Config File

Create `cyli.json` in your project root:

```json
{
  "script_runner": {
    "command": "npm",
    "run_prefix": "run",
    "scripts": {
      "test": {
        "component": "coverage:component",
        "e2e": "coverage:e2e"
      }
    }
  }
}
```

### Using Different Package Managers

**Yarn:**
```json
{
  "script_runner": {
    "package_manager": "yarn",
    "scripts": {
      "test": {
        "component": "test:component",
        "e2e": "test:e2e"
      }
    }
  }
}
```

**pnpm:**
```json
{
  "script_runner": {
    "command": "pnpm",
    "run_prefix": "run",
    "scripts": {
      "test": {
        "component": "cypress:component",
        "e2e": "cypress:e2e"
      }
    }
  }
}
```

### Supported Package Managers

| Package Manager | Command | Run Prefix |
|-----------------|---------|------------|
| npm             | `npm`   | `run`      |
| yarn            | `yarn`  | (none)     |
| pnpm            | `pnpm`  | `run`      |
| bun             | `bun`   | `run`      |

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/cyli.git
cd cyli

# Install dependencies with UV
uv sync

# Run locally
uv run cyli --help
```

### Install in Editable Mode

```bash
# Install as a global tool (changes reflect immediately)
uv tool install -e .

# Now use it anywhere
cyli test
```

### Project Structure

```
cyli/
├── src/cyli/
│   ├── cli.py           # Main CLI entry point
│   ├── config.py        # Configuration management
│   ├── commands/        # CLI commands
│   │   ├── hello.py
│   │   └── test.py      # Test command
│   ├── core/            # Core functionality
│   │   └── cypress.py   # Cypress test discovery
│   └── utils/           # Utilities
│       └── files.py     # File system helpers
├── cyli.json            # Example config
├── pyproject.toml
└── README.md
```

### UV Tool Commands

```bash
# List installed tools
uv tool list

# Upgrade cyli
uv tool upgrade cyli

# Uninstall
uv tool uninstall cyli

# Reinstall (useful after major changes)
uv tool uninstall cyli && uv tool install -e .
```

## License

MIT
