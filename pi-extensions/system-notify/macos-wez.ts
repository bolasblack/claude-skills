import { execFile, execFileSync, spawn } from "node:child_process";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";

export interface PermissionPromptEvent {
	title?: string;
	body?: string;
	cwd?: string;
	timestamp?: number;
}

export interface ActionPromptRequest {
	requestId: string;
	title: string;
	message: string;
	actions: string[];
	closeLabel?: string;
	timeoutSeconds?: number;
}

export interface ActionPromptResult {
	requestId: string;
	action?: string;
	activationType?: string;
}

interface SystemNotifier {
	notifyTaskCompleted(): void;
	notifyPermissionPrompt(event: PermissionPromptEvent): void;
	requestActionPrompt(request: ActionPromptRequest): void;
	cancelActionPrompt(requestId: string): void;
}

interface ActiveActionPrompt {
	child: ReturnType<typeof spawn>;
	groupId: string;
}

const WEZTERM_BUNDLE_ID = "com.github.wez.wezterm";
const FOCUS_ACTION_LABEL = "Focus terminal";
const DEBUG_LOG_PATH = path.join(os.homedir(), ".pi", "agent", "system-notify.log");

function runDetached(command: string, args: string[]): void {
	execFile(command, args, () => {
		// best effort only
	});
}

function appendDebugLog(message: string): void {
	if (process.env.PI_SYSTEM_NOTIFY_DEBUG !== "1") return;
	const line = `[${new Date().toISOString()}] ${message}\n`;
	try {
		fs.mkdirSync(path.dirname(DEBUG_LOG_PATH), { recursive: true });
		fs.appendFileSync(DEBUG_LOG_PATH, line, "utf8");
	} catch {
		// ignore logging errors
	}
}

function resolveAlerterPath(): string | null {
	const configured = process.env.PI_ALERTER_PATH?.trim();
	const bundled = path.join(__dirname, "vendor", "alerter");
	const candidates = [configured, bundled, "alerter"].filter((value): value is string => Boolean(value));

	for (const candidate of candidates) {
		if (candidate.includes(path.sep) && !fs.existsSync(candidate)) {
			appendDebugLog(`alerter candidate missing: ${candidate}`);
			continue;
		}
		try {
			execFileSync(candidate, ["--version"], { stdio: "ignore" });
			appendDebugLog(`alerter resolved: ${candidate}`);
			return candidate;
		} catch {
			appendDebugLog(`alerter candidate unusable: ${candidate}`);
		}
	}
	appendDebugLog("alerter not found, fallback to osascript");
	return null;
}

function resolveBinaryPath(command: string): string | null {
	if (command.includes(path.sep)) return fs.existsSync(command) ? command : null;
	try {
		const out = execFileSync("/usr/bin/which", [command], { encoding: "utf8" }).trim();
		return out || null;
	} catch {
		return null;
	}
}

function focusTerminal(): void {
	const wezPane = process.env.WEZTERM_PANE ?? "";
	const tmuxPane = process.env.TMUX_PANE ?? "";
	const weztermBin = resolveBinaryPath("wezterm");
	const tmuxBin = resolveBinaryPath("tmux");

	appendDebugLog(
		`focus begin wezPane=${JSON.stringify(wezPane)} tmuxPane=${JSON.stringify(tmuxPane)} weztermBin=${weztermBin ?? "none"} tmuxBin=${tmuxBin ?? "none"}`,
	);

	execFile("open", ["-a", "WezTerm"], (openErr) => {
		if (openErr) {
			appendDebugLog(`focus open error: ${openErr.message}`);
			return;
		}

		setTimeout(() => {
			if (weztermBin && wezPane) {
				execFile(weztermBin, ["cli", "activate-pane", "--pane-id", wezPane], (wezErr, _stdout, stderr) => {
					if (wezErr) {
						appendDebugLog(`focus wezterm error: ${wezErr.message}; stderr=${JSON.stringify(String(stderr || "").trim())}`);
					} else {
						appendDebugLog("focus wezterm success");
					}
				});
			}

			if (tmuxBin && tmuxPane) {
				execFile(tmuxBin, ["select-pane", "-t", tmuxPane], (tmuxErr, _stdout, stderr) => {
					if (tmuxErr) {
						appendDebugLog(`focus tmux error: ${tmuxErr.message}; stderr=${JSON.stringify(String(stderr || "").trim())}`);
					} else {
						appendDebugLog("focus tmux success");
					}
				});
			}
		}, 150);
	});
}

function parseJson<T>(text: string): T | null {
	try {
		return JSON.parse(text) as T;
	} catch {
		return null;
	}
}

function isPaneVisibleInWezTerm(): boolean {
	const paneEnv = process.env.WEZTERM_PANE;
	if (!paneEnv) return false;
	const paneId = Number.parseInt(paneEnv, 10);
	if (Number.isNaN(paneId)) return false;
	try {
		const raw = execFileSync("wezterm", ["cli", "list-clients", "--format", "json"], { encoding: "utf8" });
		const clients = parseJson<Array<{ focused_pane_id?: number }>>(raw) ?? [];
		return clients.some((client) => client.focused_pane_id === paneId);
	} catch {
		return false;
	}
}

function isPaneVisibleInTmux(): boolean {
	const tmuxPane = process.env.TMUX_PANE;
	if (!tmuxPane) return true;
	try {
		const raw = execFileSync(
			"tmux",
			["display-message", "-p", "-t", tmuxPane, "#{?pane_active,1,0} #{?window_active,1,0}"],
			{ encoding: "utf8" },
		).trim();
		const [paneActive, windowActive] = raw.split(/\s+/);
		return paneActive === "1" && windowActive === "1";
	} catch {
		return false;
	}
}

function isPiPaneVisible(): boolean {
	if (!isPaneVisibleInWezTerm()) return false;
	return isPaneVisibleInTmux();
}

export function shorten(text: string, max = 140): string {
	const singleLine = text.replace(/\s+/g, " ").trim();
	if (singleLine.length <= max) return singleLine;
	return `${singleLine.slice(0, max - 3)}...`;
}

export function parseActionPromptOutcome(stdout: string): { action?: string; activationType?: string; shouldFocus: boolean } {
	const parsed = parseJson<Record<string, unknown>>(stdout.trim());
	const activationType = String(parsed?.activationType ?? parsed?.event ?? parsed?.action ?? "").toLowerCase();
	const activationValue = String(parsed?.activationValue ?? parsed?.value ?? parsed?.button ?? "").trim();
	const normalizedValue = activationValue.toLowerCase();

	const contentClicked = activationType.includes("contentsclicked") || activationType.includes("activate");
	const clicked = activationType.includes("clicked");
	const focusButtonClicked = clicked && ["focus terminal", "显示"].includes(normalizedValue);

	return {
		action: activationValue || undefined,
		activationType,
		shouldFocus: contentClicked || focusButtonClicked,
	};
}

function notifyWithOsascript(title: string, body: string): void {
	appendDebugLog(`notify via osascript title=${JSON.stringify(title)} body=${JSON.stringify(body)}`);
	const script = `display notification ${JSON.stringify(body)} with title ${JSON.stringify(title)}`;
	runDetached("osascript", ["-e", script]);
}

export function createMacOSWezNotifier(onActionPromptResult: (result: ActionPromptResult) => void): SystemNotifier {
	const alerterPath = resolveAlerterPath();
	appendDebugLog(`system-notify init: alerterPath=${alerterPath ?? "none"}`);
	const activePrompts = new Map<string, ActiveActionPrompt>();

	function notifySimple(title: string, body: string): void {
		if (isPiPaneVisible()) {
			appendDebugLog(`skip notification because pane is visible: title=${JSON.stringify(title)}`);
			return;
		}
		if (!alerterPath) {
			notifyWithOsascript(title, body);
			return;
		}

		const args = [
			"--title",
			title,
			"--message",
			body,
			"--sender",
			WEZTERM_BUNDLE_ID,
			"--actions",
			FOCUS_ACTION_LABEL,
			"--close-label",
			"Dismiss",
			"--timeout",
			"20",
			"--json",
		];

		appendDebugLog(`notify via alerter(simple): title=${JSON.stringify(title)} body=${JSON.stringify(body)}`);
		const child = spawn(alerterPath, args, { stdio: ["ignore", "pipe", "pipe"] });
		let stdout = "";
		let stderr = "";
		child.stdout.on("data", (chunk) => {
			stdout += chunk.toString();
		});
		child.stderr.on("data", (chunk) => {
			stderr += chunk.toString();
		});
		child.on("close", (code) => {
			appendDebugLog(
				`alerter(simple) exit=${code} stdout=${JSON.stringify(stdout.trim())} stderr=${JSON.stringify(stderr.trim())}`,
			);
			const outcome = parseActionPromptOutcome(stdout);
			if (outcome.shouldFocus) focusTerminal();
		});
	}

	function requestActionPrompt(request: ActionPromptRequest): void {
		if (!alerterPath) {
			onActionPromptResult({ requestId: request.requestId });
			return;
		}

		const groupId = `system-notify-${request.requestId}`;
		const args = [
			"--title",
			request.title,
			"--message",
			request.message.length > 220 ? `${request.message.slice(0, 217)}...` : request.message,
			"--sender",
			WEZTERM_BUNDLE_ID,
			"--actions",
			request.actions.join(","),
			"--close-label",
			request.closeLabel ?? "Deny",
			"--group",
			groupId,
			"--json",
		];
		if (typeof request.timeoutSeconds === "number") {
			args.push("--timeout", String(request.timeoutSeconds));
		}

		appendDebugLog(`action prompt request=${request.requestId} title=${JSON.stringify(request.title)}`);
		const child = spawn(alerterPath, args, { stdio: ["ignore", "pipe", "pipe"] });
		activePrompts.set(request.requestId, { child, groupId });

		let stdout = "";
		let stderr = "";
		child.stdout.on("data", (chunk) => {
			stdout += chunk.toString();
		});
		child.stderr.on("data", (chunk) => {
			stderr += chunk.toString();
		});
		child.on("close", (code) => {
			activePrompts.delete(request.requestId);
			appendDebugLog(
				`action prompt exit id=${request.requestId} code=${code} stdout=${JSON.stringify(stdout.trim())} stderr=${JSON.stringify(stderr.trim())}`,
			);
			const outcome = parseActionPromptOutcome(stdout);
			if (outcome.shouldFocus) focusTerminal();
			onActionPromptResult({
				requestId: request.requestId,
				action: outcome.action,
				activationType: outcome.activationType,
			});
		});
		child.on("error", () => {
			activePrompts.delete(request.requestId);
			onActionPromptResult({ requestId: request.requestId });
		});
	}

	function cancelActionPrompt(requestId: string): void {
		const active = activePrompts.get(requestId);
		if (!active) return;
		activePrompts.delete(requestId);
		if (!active.child.killed) active.child.kill("SIGTERM");
		if (alerterPath) {
			execFile(alerterPath, ["--remove", active.groupId], () => {
				// ignore
			});
		}
		appendDebugLog(`action prompt canceled id=${requestId}`);
	}

	return {
		notifyTaskCompleted() {
			notifySimple("pi", "Task completed");
		},
		notifyPermissionPrompt(event: PermissionPromptEvent) {
			const title = event.title ? `pi: ${event.title}` : "pi: Permission required";
			const body = event.body ? shorten(event.body) : "A tool action needs approval";
			notifySimple(title, body);
		},
		requestActionPrompt,
		cancelActionPrompt,
	};
}
