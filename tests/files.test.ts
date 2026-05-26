import { describe, it, expect } from "bun:test";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { findFileUpwards, findProjectRoot, isDirectory } from "../src/utils/files.ts";

function makeTree() {
  const root = mkdtempSync(join(tmpdir(), "cyli-files-"));
  writeFileSync(join(root, "package.json"), "{}");
  const nested = join(root, "a", "b", "c");
  mkdirSync(nested, { recursive: true });
  return { root, nested };
}

describe("files", () => {
  it("findFileUpwards finds at root from deep dir", () => {
    const { root, nested } = makeTree();
    writeFileSync(join(root, "cyli.json"), "{}");
    expect(findFileUpwards("cyli.json", nested)).toBe(join(root, "cyli.json"));
  });

  it("findFileUpwards returns null when missing", () => {
    const { nested } = makeTree();
    expect(findFileUpwards("does-not-exist.json", nested)).toBeNull();
  });

  it("findProjectRoot detects package.json", () => {
    const { root, nested } = makeTree();
    expect(findProjectRoot(undefined, nested)).toBe(root);
  });

  it("isDirectory works", () => {
    const { root } = makeTree();
    expect(isDirectory(root)).toBe(true);
    expect(isDirectory(join(root, "package.json"))).toBe(false);
    expect(isDirectory(join(root, "missing"))).toBe(false);
  });
});
