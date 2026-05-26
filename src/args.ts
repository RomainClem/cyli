export interface ParsedArgs {
  command: string | null;
  testType: string | null;
  dryRun: boolean;
  listOnly: boolean;
  help: boolean;
}

export function parseArgs(argv: string[]): ParsedArgs {
  const out: ParsedArgs = {
    command: null,
    testType: null,
    dryRun: false,
    listOnly: false,
    help: false,
  };

  let i = 0;
  if (argv[i] && !argv[i]!.startsWith("-")) {
    out.command = argv[i]!;
    i++;
  }

  while (i < argv.length) {
    const arg = argv[i]!;
    switch (arg) {
      case "--help":
      case "-h":
        out.help = true;
        break;
      case "--dry-run":
        out.dryRun = true;
        break;
      case "--list-only":
      case "-l":
        out.listOnly = true;
        break;
      case "--type":
      case "-t":
        i++;
        out.testType = argv[i] ?? null;
        break;
      default:
        if (arg.startsWith("--type=")) {
          out.testType = arg.slice("--type=".length);
        } else {
          throw new Error(`Unknown argument: ${arg}`);
        }
    }
    i++;
  }

  return out;
}
