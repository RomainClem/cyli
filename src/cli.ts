import { parseArgs } from "./args.ts";
import { runTestCommand } from "./commands/test.tsx";

const HELP = `cyli - Interactive Cypress test runner

Usage:
  cyli <command> [options]

Commands:
  test               Run Cypress tests (component or e2e)

Options for 'test':
  -t, --type <type>  Test type (component or e2e). Prompts if omitted.
  --dry-run          Print the command without executing it
  -l, --list-only    Only list the test files without running them
  -h, --help         Show this help
`;

async function main() {
  let parsed;
  try {
    parsed = parseArgs(process.argv.slice(2));
  } catch (err) {
    process.stderr.write(`${(err as Error).message}\n\n${HELP}`);
    process.exit(2);
  }

  if (parsed.help || parsed.command === null) {
    process.stdout.write(HELP);
    process.exit(parsed.help ? 0 : 1);
  }

  switch (parsed.command) {
    case "test": {
      const code = await runTestCommand({
        testType: parsed.testType,
        dryRun: parsed.dryRun,
        listOnly: parsed.listOnly,
      });
      process.exit(code);
      break;
    }
    default:
      process.stderr.write(`Unknown command: ${parsed.command}\n\n${HELP}`);
      process.exit(2);
  }
}

main().catch((err) => {
  process.stderr.write(`Fatal: ${(err as Error).stack ?? err}\n`);
  process.exit(1);
});
