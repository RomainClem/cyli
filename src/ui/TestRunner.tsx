import React, { useEffect, useReducer, useRef, useState } from "react";
import { Box, Text, useApp, useInput } from "ink";
import { spawn, type ChildProcess } from "node:child_process";
import { basename } from "node:path";

interface Props {
  testFiles: string[];
  testType: string;
  baseCmd: string[];
}

type Focus = "list" | "output";

interface LogLine {
  id: number;
  text: string;
  color?: string;
  bold?: boolean;
}

type LogAction = { kind: "clear" } | { kind: "append"; lines: Omit<LogLine, "id">[] };

const MAX_LOG_LINES = 2000;
let lineCounter = 0;

function logReducer(state: LogLine[], action: LogAction): LogLine[] {
  if (action.kind === "clear") return [];
  const appended = action.lines.map((l) => ({ ...l, id: ++lineCounter }));
  const next = state.concat(appended);
  return next.length > MAX_LOG_LINES ? next.slice(next.length - MAX_LOG_LINES) : next;
}

export function TestRunner({ testFiles, testType, baseCmd }: Props) {
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [focus, setFocus] = useState<Focus>("list");
  const [status, setStatus] = useState("Ready. Select a test to run.");
  const [log, dispatchLog] = useReducer(logReducer, []);
  const [scrollOffset, setScrollOffset] = useState(0);
  const processRef = useRef<ChildProcess | null>(null);
  const { exit } = useApp();

  const killCurrent = () => {
    const proc = processRef.current;
    if (proc && proc.exitCode === null && !proc.killed) {
      try {
        proc.kill("SIGTERM");
      } catch {}
    }
    processRef.current = null;
  };

  useEffect(() => {
    return () => {
      killCurrent();
    };
  }, []);

  const runTest = (testFile: string) => {
    if (processRef.current) {
      dispatchLog({
        kind: "append",
        lines: [{ text: "⚠ Cancelling previous test...", color: "yellow", bold: true }],
      });
      killCurrent();
    }
    dispatchLog({ kind: "clear" });
    setScrollOffset(0);

    const cmd = [...baseCmd, "--", "--", "--spec", testFile];
    const cmdStr = cmd.slice(0, -1).join(" ") + ` "${cmd[cmd.length - 1]}"`;

    dispatchLog({
      kind: "append",
      lines: [{ text: `Running: ${cmdStr}`, color: "blue", bold: true }, { text: "-".repeat(60) }],
    });
    setStatus(`Running: ${basename(testFile)}...`);

    let proc: ChildProcess;
    try {
      proc = spawn(cmd[0]!, cmd.slice(1), { stdio: ["ignore", "pipe", "pipe"] });
    } catch (err) {
      dispatchLog({
        kind: "append",
        lines: [{ text: `Error: ${(err as Error).message}`, color: "red", bold: true }],
      });
      setStatus(`Error: ${(err as Error).message}`);
      return;
    }
    processRef.current = proc;

    let buffer = "";
    const onChunk = (chunk: Buffer) => {
      buffer += chunk.toString("utf-8");
      const parts = buffer.split("\n");
      buffer = parts.pop() ?? "";
      if (parts.length) {
        dispatchLog({
          kind: "append",
          lines: parts.map((text) => ({ text: text.replace(/\r$/, "") })),
        });
      }
    };
    proc.stdout?.on("data", onChunk);
    proc.stderr?.on("data", onChunk);

    proc.on("error", (err) => {
      if (processRef.current !== proc) return;
      const msg =
        (err as NodeJS.ErrnoException).code === "ENOENT"
          ? `Error: Command not found: ${cmd[0]}\nMake sure the package manager is installed.`
          : `Error: ${err.message}`;
      dispatchLog({
        kind: "append",
        lines: msg.split("\n").map((text) => ({ text, color: "red", bold: true })),
      });
      setStatus("Error: Command not found");
      processRef.current = null;
    });

    proc.on("close", (code) => {
      if (processRef.current !== proc) return;
      if (buffer) {
        dispatchLog({ kind: "append", lines: [{ text: buffer }] });
        buffer = "";
      }
      const lines: Omit<LogLine, "id">[] = [{ text: "-".repeat(60) }];
      if (code === 0) {
        lines.push({ text: "✓ Test passed", color: "green", bold: true });
        setStatus(`✓ ${basename(testFile)} passed. Select another test to run.`);
      } else if (code === null) {
        lines.push({ text: "⚠ Cancelled", color: "yellow", bold: true });
      } else {
        lines.push({ text: `✗ Test failed (exit code: ${code})`, color: "red", bold: true });
        setStatus(`✗ ${basename(testFile)} failed. Select another test to run.`);
      }
      dispatchLog({ kind: "append", lines });
      processRef.current = null;
    });
  };

  useInput((input, key) => {
    if (input === "q" || key.escape) {
      killCurrent();
      exit();
      return;
    }
    if (input === "h") {
      setFocus("list");
      return;
    }
    if (input === "l") {
      setFocus("output");
      return;
    }
    if (key.tab) {
      setFocus((f) => (f === "list" ? "output" : "list"));
      return;
    }

    if (focus === "list") {
      if (key.upArrow || input === "k") {
        setSelectedIdx((i) => (i - 1 + testFiles.length) % testFiles.length);
      } else if (key.downArrow || input === "j") {
        setSelectedIdx((i) => (i + 1) % testFiles.length);
      } else if (key.return) {
        const file = testFiles[selectedIdx];
        if (file) runTest(file);
      }
    } else {
      if (key.upArrow || input === "k") {
        setScrollOffset((o) => Math.max(0, o - 1));
      } else if (key.downArrow || input === "j") {
        setScrollOffset((o) => o + 1);
      } else if (key.pageUp) {
        setScrollOffset((o) => Math.max(0, o - 10));
      } else if (key.pageDown) {
        setScrollOffset((o) => o + 10);
      }
    }
  });

  const outputHeight = Math.max(5, (process.stdout.rows ?? 24) - 8);
  const totalLines = log.length;
  const maxOffset = Math.max(0, totalLines - outputHeight);
  const effectiveOffset = Math.min(scrollOffset, maxOffset);
  const startLine = Math.max(0, totalLines - outputHeight - effectiveOffset);
  const visibleLines = log.slice(startLine, startLine + outputHeight);

  return (
    <Box flexDirection="column" height="100%">
      <Box flexDirection="row" flexGrow={1}>
        <Box
          flexDirection="column"
          borderStyle="round"
          borderColor={focus === "list" ? "cyan" : "gray"}
          width="30%"
          paddingX={1}
        >
          <Text bold>📁 {testType} tests</Text>
          <Box flexDirection="column" marginTop={1}>
            {testFiles.map((f, i) => {
              const active = i === selectedIdx;
              const focused = active && focus === "list";
              return (
                <Text
                  key={f}
                  color={focused ? "cyan" : undefined}
                  inverse={active && focus !== "list"}
                >
                  {focused ? "❯ " : "  "}
                  {basename(f).replace(/\.cy\.(ts|tsx|js|jsx)$/, "")}
                </Text>
              );
            })}
          </Box>
        </Box>
        <Box
          flexDirection="column"
          borderStyle="round"
          borderColor={focus === "output" ? "magenta" : "gray"}
          flexGrow={1}
          paddingX={1}
        >
          <Text bold>📋 Output</Text>
          <Box flexDirection="column" marginTop={1}>
            {visibleLines.map((line) => (
              <Text key={line.id} color={line.color} bold={line.bold}>
                {line.text || " "}
              </Text>
            ))}
          </Box>
        </Box>
      </Box>
      <Box>
        <Text dimColor>{status}</Text>
      </Box>
      <Box>
        <Text dimColor>q/esc quit · h focus list · l focus output · tab switch · enter run</Text>
      </Box>
    </Box>
  );
}
