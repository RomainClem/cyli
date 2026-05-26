import { describe, it, expect } from "bun:test";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { getTestFiles, listTestFiles, listSrcTestFiles } from "../src/core/cypress.ts";

function makeCypressProject() {
  const root = mkdtempSync(join(tmpdir(), "cyli-cyp-"));
  writeFileSync(join(root, "package.json"), "{}");
  mkdirSync(join(root, "cypress", "e2e", "feature"), { recursive: true });
  mkdirSync(join(root, "cypress", "component"), { recursive: true });
  mkdirSync(join(root, "src", "components"), { recursive: true });

  writeFileSync(join(root, "cypress", "e2e", "login.cy.ts"), "");
  writeFileSync(join(root, "cypress", "e2e", "feature", "nested.cy.js"), "");
  writeFileSync(join(root, "cypress", "e2e", "ignore.txt"), "");

  writeFileSync(join(root, "cypress", "component", "btn.cy.tsx"), "");

  writeFileSync(join(root, "src", "components", "card.cy.tsx"), "");
  writeFileSync(join(root, "src", "components", "card.tsx"), "");

  return root;
}

describe("cypress discovery", () => {
  it("lists e2e tests from cypress folder only", () => {
    const root = makeCypressProject();
    const files = listTestFiles("e2e", root);
    expect(files.length).toBe(2);
    expect(files.every((f) => f.endsWith(".cy.ts") || f.endsWith(".cy.js"))).toBe(true);
  });

  it("lists component tests from cypress folder only", () => {
    const root = makeCypressProject();
    const files = listTestFiles("component", root);
    expect(files.length).toBe(1);
    expect(files[0]!.endsWith("btn.cy.tsx")).toBe(true);
  });

  it("lists src tests independently", () => {
    const root = makeCypressProject();
    const files = listSrcTestFiles(root);
    expect(files.length).toBe(1);
    expect(files[0]!.endsWith("card.cy.tsx")).toBe(true);
  });

  it("getTestFiles for component combines cypress + src", () => {
    const root = makeCypressProject();
    const files = getTestFiles("component", root);
    expect(files.length).toBe(2);
  });

  it("getTestFiles for e2e does not include src", () => {
    const root = makeCypressProject();
    const files = getTestFiles("e2e", root);
    expect(files.length).toBe(2);
    expect(files.some((f) => f.includes("/src/"))).toBe(false);
  });

  it("throws on unknown test type", () => {
    expect(() => listTestFiles("smoke")).toThrow();
  });

  it("returns empty when no cypress folder", () => {
    const root = mkdtempSync(join(tmpdir(), "cyli-empty-"));
    writeFileSync(join(root, "package.json"), "{}");
    expect(listTestFiles("e2e", root)).toEqual([]);
  });
});
