/**
 * System Notify extension entrypoint.
 *
 * Spec and integration contract:
 * - ./README.md
 */

import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import {
	createMacOSWezNotifier,
	type ActionPromptRequest,
	type ActionPromptResult,
	type PermissionPromptEvent,
} from "./macos-wez.js";

interface SystemNotifier {
	notifyTaskCompleted(): void;
	notifyPermissionPrompt(event: PermissionPromptEvent): void;
	requestActionPrompt(request: ActionPromptRequest): void;
	cancelActionPrompt(requestId: string): void;
}

function createNoopNotifier(): SystemNotifier {
	return {
		notifyTaskCompleted() {
			// no-op on unsupported platforms
		},
		notifyPermissionPrompt() {
			// no-op on unsupported platforms
		},
		requestActionPrompt(_request: ActionPromptRequest) {
			// no-op
		},
		cancelActionPrompt() {
			// no-op
		},
	};
}

export default function (pi: ExtensionAPI) {
	const onActionPromptResult = (result: ActionPromptResult) => {
		pi.events.emit("system-notify:action-prompt-result", result);
	};
	const notifier: SystemNotifier =
		process.platform === "darwin" ? createMacOSWezNotifier(onActionPromptResult) : createNoopNotifier();

	pi.on("agent_end", async () => {
		notifier.notifyTaskCompleted();
	});

	pi.events.on("permission-guard:permission-prompt", (payload) => {
		notifier.notifyPermissionPrompt(payload as PermissionPromptEvent);
	});

	pi.events.on("system-notify:action-prompt-request", (payload) => {
		notifier.requestActionPrompt(payload as ActionPromptRequest);
	});

	pi.events.on("system-notify:action-prompt-cancel", (payload) => {
		const request = payload as { requestId?: string };
		if (!request.requestId) return;
		notifier.cancelActionPrompt(request.requestId);
	});
}
