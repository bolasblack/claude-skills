import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import {
  DEFAULT_MAX_BYTES,
  DEFAULT_MAX_LINES,
  formatSize,
  truncateTail,
  withFileMutationQueue,
} from "@mariozechner/pi-coding-agent";
import { writeFile, readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { Type } from "@sinclair/typebox";

export default function (pi: ExtensionAPI) {
  // Example 1: Tool with output truncation
  pi.registerTool({
    name: "sample_tool",
    label: "Sample Tool",
    description: "Example tool that demonstrates truncation.",
    promptSnippet: "Echo text with optional repetition and truncation",
    parameters: Type.Object({
      text: Type.String({ description: "Text to echo" }),
      repeat: Type.Optional(
        Type.Number({ description: "Number of times to repeat", default: 1 })
      ),
    }),
    async execute(_toolCallId, params) {
      const repeat = Math.max(1, params.repeat ?? 1);
      const fullOutput = Array.from({ length: repeat }, () => params.text).join("\n");
      const truncation = truncateTail(fullOutput, {
        maxBytes: DEFAULT_MAX_BYTES,
        maxLines: DEFAULT_MAX_LINES,
      });

      let text = truncation.content;
      let fullOutputPath: string | undefined;
      if (truncation.truncated) {
        fullOutputPath = join(tmpdir(), `sample_tool-${Date.now()}.log`);
        await writeFile(fullOutputPath, fullOutput, "utf8");
        text += `\n\n[Output truncated: ${truncation.outputLines} of ${truncation.totalLines} lines (${formatSize(
          truncation.outputBytes
        )} of ${formatSize(truncation.totalBytes)}) - full output saved to ${fullOutputPath}]`;
      }

      return {
        content: [{ type: "text", text }],
        details: { truncated: truncation.truncated, fullOutputPath },
      };
    },
  });

  // Example 2: File-mutating tool with withFileMutationQueue
  pi.registerTool({
    name: "append_to_file",
    label: "Append to File",
    description: "Append text to a file, safe for parallel tool execution.",
    promptSnippet: "Append text to a file (mutation-safe)",
    parameters: Type.Object({
      path: Type.String({ description: "File path (relative to cwd)" }),
      text: Type.String({ description: "Text to append" }),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      const absolutePath = resolve(ctx.cwd, params.path.replace(/^@/, ""));

      return withFileMutationQueue(absolutePath, async () => {
        let existing = "";
        try {
          existing = await readFile(absolutePath, "utf8");
        } catch {
          // file doesn't exist yet
        }
        await writeFile(absolutePath, existing + params.text, "utf8");

        return {
          content: [{ type: "text", text: `Appended to ${params.path}` }],
          details: {},
        };
      });
    },
  });
}
