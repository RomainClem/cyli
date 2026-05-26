import { existsSync, statSync } from "node:fs";
import { dirname, resolve, join, parse } from "node:path";

export function findFileUpwards(filename: string, startPath: string = process.cwd()): string | null {
  let current = resolve(startPath);
  const { root } = parse(current);

  while (true) {
    const candidate = join(current, filename);
    if (existsSync(candidate)) return candidate;
    if (current === root) return null;
    current = dirname(current);
  }
}

const DEFAULT_MARKERS = ["package.json", "pyproject.toml", "setup.py", "Cargo.toml", "go.mod", ".git"];

export function findProjectRoot(
  markerFiles: string[] = DEFAULT_MARKERS,
  startPath: string = process.cwd(),
): string | null {
  let current = resolve(startPath);
  const { root } = parse(current);

  while (true) {
    for (const marker of markerFiles) {
      if (existsSync(join(current, marker))) return current;
    }
    if (current === root) return null;
    current = dirname(current);
  }
}

export function isDirectory(path: string): boolean {
  try {
    return statSync(path).isDirectory();
  } catch {
    return false;
  }
}
