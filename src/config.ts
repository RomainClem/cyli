import { readFileSync, existsSync } from "node:fs";
import { findFileUpwards } from "./utils/files.ts";

export const CONFIG_FILE_NAME = "cyli.json";

export const PACKAGE_MANAGERS: Record<string, { command: string; runPrefix: string }> = {
  npm: { command: "npm", runPrefix: "run" },
  yarn: { command: "yarn", runPrefix: "" },
  pnpm: { command: "pnpm", runPrefix: "run" },
  bun: { command: "bun", runPrefix: "run" },
};

export type ScriptMap = Record<string, Record<string, string>>;

export interface ScriptRunnerConfig {
  command: string;
  runPrefix: string;
  scripts: ScriptMap;
}

export interface Config {
  scriptRunner: ScriptRunnerConfig;
}

function defaultScripts(): ScriptMap {
  return {
    test: {
      component: "coverage:component",
      e2e: "coverage:e2e",
    },
  };
}

export function defaultConfig(): Config {
  return {
    scriptRunner: {
      command: "npm",
      runPrefix: "run",
      scripts: defaultScripts(),
    },
  };
}

export function configFromDict(data: any): Config {
  const runnerData = (data?.script_runner ?? {}) as Record<string, any>;

  if (typeof runnerData.package_manager === "string") {
    const pmName = runnerData.package_manager;
    const pm = PACKAGE_MANAGERS[pmName];
    if (!pm) {
      throw new Error(
        `Unknown package manager: ${pmName}. Available: ${Object.keys(PACKAGE_MANAGERS).join(", ")}`,
      );
    }
    return {
      scriptRunner: {
        command: pm.command,
        runPrefix: pm.runPrefix,
        scripts: runnerData.scripts ?? defaultScripts(),
      },
    };
  }

  return {
    scriptRunner: {
      command: runnerData.command ?? "npm",
      runPrefix: runnerData.run_prefix ?? "run",
      scripts: runnerData.scripts ?? defaultScripts(),
    },
  };
}

export function findConfigFile(startPath?: string): string | null {
  return findFileUpwards(CONFIG_FILE_NAME, startPath);
}

export function loadConfig(configPath?: string | null): Config {
  const path = configPath ?? findConfigFile();
  if (!path || !existsSync(path)) return defaultConfig();
  const data = JSON.parse(readFileSync(path, "utf-8"));
  return configFromDict(data);
}

export function getCommand(config: Config, category: string, scriptKey: string): string[] {
  const { command, runPrefix, scripts } = config.scriptRunner;
  const categoryScripts = scripts[category];
  if (!categoryScripts) {
    throw new Error(`Unknown category: ${category}. Available: ${Object.keys(scripts).join(", ")}`);
  }
  const script = categoryScripts[scriptKey];
  if (!script) {
    throw new Error(
      `Unknown script '${scriptKey}' in category '${category}'. Available: ${Object.keys(categoryScripts).join(", ")}`,
    );
  }
  return runPrefix ? [command, runPrefix, script] : [command, script];
}

export function getTestCommand(config: Config, testType: string): string[] {
  return getCommand(config, "test", testType);
}
