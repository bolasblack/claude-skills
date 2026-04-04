import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { isToolCallEventType } from "@mariozechner/pi-coding-agent";
import { Type } from "@sinclair/typebox";

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async (event, ctx) => {
    // event.reason: "startup" | "reload" | "new" | "resume" | "fork"
    // event.previousSessionFile: set for "new", "resume", "fork"
    if (ctx.hasUI) ctx.ui.notify("extension loaded", "info");
  });

  pi.on("tool_call", async (event, _ctx) => {
    if (isToolCallEventType("bash", event)) {
      // event.input is typed as { command: string; timeout?: number }
      if (event.input.command.includes("rm -rf")) {
        return { block: true, reason: "Blocked by policy" };
      }
    }
  });

  pi.registerTool({
    name: "hello_tool",
    label: "Hello Tool",
    description: "Return a greeting",
    promptSnippet: "Greet someone by name",
    parameters: Type.Object({
      name: Type.String({ description: "Name to greet" }),
    }),
    async execute(_toolCallId, params) {
      return {
        content: [{ type: "text", text: `Hello, ${params.name}!` }],
        details: { ok: true },
      };
    },
  });

  pi.registerCommand("hello", {
    description: "Say hello",
    handler: async (args, ctx) => {
      if (ctx.hasUI) ctx.ui.notify(`Hello ${args || "world"}`, "info");
    },
  });
}
