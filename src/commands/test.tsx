import React from "react";
import { render } from "ink";
import { loadConfig, getTestCommand } from "../config.ts";
import { getTestFiles } from "../core/cypress.ts";
import { TestTypeSelector, type TypeChoice } from "../ui/TestTypeSelector.tsx";
import { TestRunner } from "../ui/TestRunner.tsx";

interface TestOptions {
  testType: string | null;
  dryRun: boolean;
  listOnly: boolean;
}

async function promptTestType(choices: TypeChoice[]): Promise<string | null> {
  return new Promise((resolve) => {
    let chosen: string | null = null;
    const { unmount, waitUntilExit } = render(
      <TestTypeSelector
        choices={choices}
        onSelect={(t) => {
          chosen = t;
        }}
      />,
    );
    waitUntilExit().then(() => {
      unmount();
      resolve(chosen);
    });
  });
}

export async function runTestCommand(opts: TestOptions): Promise<number> {
  const config = loadConfig();
  const testScripts = config.scriptRunner.scripts["test"] ?? {};

  if (Object.keys(testScripts).length === 0) {
    process.stderr.write("No test scripts configured.\n");
    return 1;
  }

  const availableTypes = Object.keys(testScripts);
  let testType = opts.testType;

  if (testType === null) {
    const choices: TypeChoice[] = availableTypes.map((t) => ({ type: t, script: testScripts[t]! }));
    testType = await promptTestType(choices);
    if (testType === null) return 0;
  }

  if (!(testType in testScripts)) {
    process.stderr.write(`Unknown test type: ${testType}\n`);
    process.stderr.write(`Available types: ${availableTypes.join(", ")}\n`);
    return 1;
  }

  const testFiles = getTestFiles(testType);

  if (opts.listOnly) {
    process.stdout.write(`\nTest files for '${testType}':\n`);
    process.stdout.write("-".repeat(40) + "\n");
    if (testFiles.length === 0) {
      process.stdout.write("  No test files found.\n");
    } else {
      for (const f of testFiles) process.stdout.write(`  • ${f}\n`);
      process.stdout.write(`\nTotal: ${testFiles.length} test file(s)\n`);
    }
    return 0;
  }

  if (testFiles.length === 0) {
    process.stderr.write("No test files found.\n");
    return 1;
  }

  const baseCmd = getTestCommand(config, testType);

  if (opts.dryRun) {
    process.stdout.write("Dry run mode - showing command format:\n");
    const cmdStr = baseCmd.join(" ") + ' -- -- --spec "<test_file>"';
    process.stdout.write(`  ${cmdStr}\n`);
    return 0;
  }

  const { waitUntilExit } = render(
    <TestRunner testFiles={testFiles} testType={testType} baseCmd={baseCmd} />,
  );
  await waitUntilExit();
  return 0;
}
