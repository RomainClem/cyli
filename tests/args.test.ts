import { describe, it, expect } from "bun:test";
import { parseArgs } from "../src/args.ts";

describe("parseArgs", () => {
  it("parses bare command", () => {
    expect(parseArgs(["test"])).toMatchObject({
      command: "test",
      testType: null,
      dryRun: false,
      listOnly: false,
    });
  });

  it("parses --type with value", () => {
    expect(parseArgs(["test", "--type", "e2e"])).toMatchObject({
      command: "test",
      testType: "e2e",
    });
  });

  it("parses -t short flag", () => {
    expect(parseArgs(["test", "-t", "component"])).toMatchObject({ testType: "component" });
  });

  it("parses --type=value", () => {
    expect(parseArgs(["test", "--type=e2e"])).toMatchObject({ testType: "e2e" });
  });

  it("parses --dry-run and --list-only", () => {
    expect(parseArgs(["test", "--dry-run", "--list-only"])).toMatchObject({
      dryRun: true,
      listOnly: true,
    });
  });

  it("parses -l short for list-only", () => {
    expect(parseArgs(["test", "-l"])).toMatchObject({ listOnly: true });
  });

  it("parses --help", () => {
    expect(parseArgs(["--help"])).toMatchObject({ help: true, command: null });
  });

  it("throws on unknown arg", () => {
    expect(() => parseArgs(["test", "--what"])).toThrow();
  });
});
