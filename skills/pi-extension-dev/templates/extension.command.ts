import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.registerCommand("summarize", {
    description: "Queue a follow-up summary request",
    handler: async (args, ctx) => {
      const prompt = args
        ? `Summarize the following topic: ${args}`
        : "Summarize the most recent changes.";

      pi.sendUserMessage(prompt, { deliverAs: "followUp" });

      if (ctx.hasUI) {
        ctx.ui.notify("Queued summary request.", "info");
      }
    },
  });
}
