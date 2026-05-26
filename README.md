# Cyli

An interactive CLI/TUI for discovering and running Cypress tests, built with [Ink](https://github.com/vadimdemedes/ink) and [Bun](https://bun.sh).

## Features

- 🔍 **Auto-discovery** — finds Cypress test files in `cypress/` and `src/`
- 🎯 **Interactive selection** — pick a test type and file from a TUI
- 📺 **Live output** — streams the runner's stdout/stderr next to the file list
- ⚙️ **Pluggable** — works with npm, yarn, pnpm, and bun

## Installation

```bash
# Global, via npm
npm install -g cyli

# Or run ad-hoc
npx cyli test
```

Requires Node.js ≥ 18.

## Quick Start

From any Cypress project directory:

```bash
cyli test
```

You'll be prompted to choose a test type (`component` or `e2e`), then shown a list of test files. Select one to run it and watch live output.

## Usage

```bash
# Interactive mode (prompt for type, then pick file in TUI)
cyli test

# Skip the type prompt
cyli test --type component
cyli test -t e2e

# List discovered test files and exit
cyli test --list-only
cyli test -l

# Print the command without executing
cyli test --dry-run --type e2e

# Help
cyli --help
```

### Keybindings in the runner TUI

| Key       | Action                |
| --------- | --------------------- |
| `↑` / `↓` | Move selection / scroll |
| `Enter`   | Run the selected test |
| `h`       | Focus the file list   |
| `l`       | Focus the output pane |
| `Tab`     | Toggle focus          |
| `q` / `Esc` | Quit (kills any running process) |

Selecting a different test while one is running cancels the previous process.

## Configuration

Cyli looks for a `cyli.json` file in the current directory or any ancestor. With no config, it defaults to npm + `coverage:component` / `coverage:e2e` scripts.

### Example: shorthand using a package-manager preset

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

### Example: explicit command/prefix

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

### Supported package managers

| Manager | Command | Run prefix |
| ------- | ------- | ---------- |
| npm     | `npm`   | `run`      |
| yarn    | `yarn`  | (none)     |
| pnpm    | `pnpm`  | `run`      |
| bun     | `bun`   | `run`      |

Each invocation is built as:

```
<command> [run] <script> -- -- --spec <test_file>
```

See `cyli.example.json` and `cyli.example.yarn.json`.

## Development

Built with Bun. To work on cyli locally:

```bash
# Install deps
bun install

# Run from source
bun run dev test --list-only

# Type-check
bun run typecheck

# Run tests
bun test

# Build the publishable artifact
bun run build
node dist/cli.js --help
```

### Project layout

```
cyli/
├── src/
│   ├── cli.ts                  # entry point
│   ├── args.ts                 # tiny argv parser
│   ├── config.ts               # cyli.json loading + command building
│   ├── core/cypress.ts         # test discovery
│   ├── utils/files.ts          # upward-search + project root
│   ├── commands/test.tsx       # test command orchestrator
│   └── ui/
│       ├── TestTypeSelector.tsx
│       └── TestRunner.tsx
├── tests/                      # bun:test specs for core logic
├── package.json
└── tsconfig.json
```

## License

MIT
