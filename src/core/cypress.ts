import { readdirSync } from "node:fs";
import { join } from "node:path";
import { findProjectRoot, isDirectory } from "../utils/files.ts";

const CYPRESS_FOLDER = "cypress";
const TEST_FOLDERS: Record<string, string> = {
  e2e: "e2e",
  component: "component",
};
const TEST_SUFFIX_RE = /\.cy\.(ts|tsx|js|jsx)$/;

export function findCypressFolder(startPath?: string): string | null {
  const root = findProjectRoot(undefined, startPath);
  if (!root) return null;
  const cypressPath = join(root, CYPRESS_FOLDER);
  return isDirectory(cypressPath) ? cypressPath : null;
}

export function findTestFolder(testType: string, startPath?: string): string | null {
  if (!(testType in TEST_FOLDERS)) {
    throw new Error(
      `Unknown test type: ${testType}. Available: ${Object.keys(TEST_FOLDERS).join(", ")}`,
    );
  }
  const cypressFolder = findCypressFolder(startPath);
  if (!cypressFolder) return null;
  const testFolder = join(cypressFolder, TEST_FOLDERS[testType]!);
  return isDirectory(testFolder) ? testFolder : null;
}

function globTestFiles(folder: string): string[] {
  const files: string[] = [];
  const walk = (dir: string) => {
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.isFile() && TEST_SUFFIX_RE.test(entry.name)) {
        files.push(full);
      }
    }
  };
  walk(folder);
  return files.toSorted();
}

export function listTestFiles(testType: string, startPath?: string): string[] {
  const testFolder = findTestFolder(testType, startPath);
  if (!testFolder) return [];
  return globTestFiles(testFolder);
}

export function findSrcFolder(startPath?: string): string | null {
  const root = findProjectRoot(undefined, startPath);
  if (!root) return null;
  const srcPath = join(root, "src");
  return isDirectory(srcPath) ? srcPath : null;
}

export function listSrcTestFiles(startPath?: string): string[] {
  const srcFolder = findSrcFolder(startPath);
  if (!srcFolder) return [];
  return globTestFiles(srcFolder);
}

export function getTestFiles(testType: string, startPath?: string): string[] {
  const cypressTests = listTestFiles(testType, startPath);
  const srcTests = testType === "component" ? listSrcTestFiles(startPath) : [];
  return [...cypressTests, ...srcTests];
}
