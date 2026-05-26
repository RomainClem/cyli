import React, { useState } from "react";
import { Box, Text, useApp, useInput } from "ink";

export interface TypeChoice {
  type: string;
  script: string;
}

interface Props {
  choices: TypeChoice[];
  onSelect: (type: string | null) => void;
}

export function TestTypeSelector({ choices, onSelect }: Props) {
  const [index, setIndex] = useState(0);
  const { exit } = useApp();

  useInput((input, key) => {
    if (key.escape || input === "q") {
      onSelect(null);
      exit();
      return;
    }
    if (key.upArrow || input === "k") {
      setIndex((i) => (i - 1 + choices.length) % choices.length);
    } else if (key.downArrow || input === "j") {
      setIndex((i) => (i + 1) % choices.length);
    } else if (key.return) {
      onSelect(choices[index]!.type);
      exit();
    }
  });

  return (
    <Box flexDirection="column" paddingX={1}>
      <Box marginBottom={1}>
        <Text bold>🧪 Select test type:</Text>
      </Box>
      {choices.map((c, i) => {
        const active = i === index;
        return (
          <Text key={c.type} color={active ? "cyan" : undefined}>
            {active ? "❯ " : "  "}
            {c.type} ({c.script})
          </Text>
        );
      })}
      <Box marginTop={1}>
        <Text dimColor>↑/↓ navigate · enter select · esc cancel</Text>
      </Box>
    </Box>
  );
}
