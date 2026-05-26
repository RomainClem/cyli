import { describe, it, expect } from "bun:test";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  configFromDict,
  defaultConfig,
  getTestCommand,
  loadConfig,
  findConfigFile,
} from "../src/config.ts";

describe("config", () => {
  it("returns defaults when no data given", () => {
    const cfg = configFromDict({});
    expect(cfg.scriptRunner.command).toBe("npm");
    expect(cfg.scriptRunner.runPrefix).toBe("run");
    expect(cfg.scriptRunner.scripts.test).toEqual({
      component: "coverage:component",
      e2e: "coverage:e2e",
    });
  });

  it("expands yarn package_manager preset (no run prefix)", () => {
    const cfg = configFromDict({ script_runner: { package_manager: "yarn" } });
    expect(cfg.scriptRunner.command).toBe("yarn");
    expect(cfg.scriptRunner.runPrefix).toBe("");
    const cmd = getTestCommand(cfg, "component");
    expect(cmd).toEqual(["yarn", "coverage:component"]);
  });

  it.each(["npm", "pnpm", "bun"])("uses run prefix for %s", (pm) => {
    const cfg = configFromDict({ script_runner: { package_manager: pm } });
    expect(getTestCommand(cfg, "e2e")).toEqual([pm, "run", "coverage:e2e"]);
  });

  it("throws on unknown package_manager", () => {
    expect(() => configFromDict({ script_runner: { package_manager: "deno" } })).toThrow();
  });

  it("respects explicit command and run_prefix", () => {
    const cfg = configFromDict({
      script_runner: {
        command: "ni",
        run_prefix: "",
        scripts: { test: { component: "cy:c", e2e: "cy:e" } },
      },
    });
    expect(getTestCommand(cfg, "component")).toEqual(["ni", "cy:c"]);
  });

  it("loadConfig returns defaults when no file found", () => {
    const tmp = mkdtempSync(join(tmpdir(), "cyli-no-cfg-"));
    const cfg = loadConfig(join(tmp, "missing.json"));
    expect(cfg).toEqual(defaultConfig());
  });

  it("loadConfig parses a cyli.json file", () => {
    const tmp = mkdtempSync(join(tmpdir(), "cyli-cfg-"));
    const path = join(tmp, "cyli.json");
    writeFileSync(
      path,
      JSON.stringify({
        script_runner: {
          package_manager: "yarn",
          scripts: { test: { component: "test:c", e2e: "test:e" } },
        },
      }),
    );
    const cfg = loadConfig(path);
    expect(cfg.scriptRunner.command).toBe("yarn");
    expect(getTestCommand(cfg, "component")).toEqual(["yarn", "test:c"]);
  });

  it("findConfigFile walks upward", () => {
    const tmp = mkdtempSync(join(tmpdir(), "cyli-find-"));
    const cfgPath = join(tmp, "cyli.json");
    writeFileSync(cfgPath, "{}");
    const deep = join(tmp, "a", "b", "c");
    require("node:fs").mkdirSync(deep, { recursive: true });
    expect(findConfigFile(deep)).toBe(cfgPath);
  });

  it("getTestCommand throws on unknown category or key", () => {
    const cfg = defaultConfig();
    expect(() => getTestCommand(cfg, "smoke")).toThrow();
  });
});
