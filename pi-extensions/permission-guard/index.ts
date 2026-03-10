/**
 * Permission Guard extension entrypoint.
 *
 * Spec and integration contract:
 * - ./README.md
 */

import { execFileSync } from "node:child_process";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import {
	extractCommandsFromSkillMarkdown,
	isActionAllowedByRules,
	isInsideProject,
	isSkillReadAllowed,
	normalizeCommand,
	isPermissionGuardBypassed,
} from "./policy.js";
import { mapChoiceToDecision, type Decision, type ToolPermissionOption } from "./decision.js";


interface RuleSettings {
	allowedRules?: string[];
}


interface ActionPromptHandle {
	promise: Promise<Decision | undefined>;
	cancel: () => void;
}

interface ActionPromptResult {
	requestId?: string;
	action?: string;
	activationType?: string;
}

const ALLOW_OPTIONS: ToolPermissionOption[] = [
	"Allow",
	"Allow always (project level)",
	"Allow always (user level)",
	"Deny",
	"Deny with note",
];

export default function (pi: ExtensionAPI) {
	function getProjectSettingsPath(cwd: string): string {
		return path.join(cwd, ".pi", "permission-guard.json");
	}

	function getGlobalSettingsPath(): string {
		return path.join(os.homedir(), ".pi", "agent", "permission-guard.json");
	}

	function readSettingsFile(filePath: string): RuleSettings {
		try {
			if (!fs.existsSync(filePath)) return {};
			const parsed = JSON.parse(fs.readFileSync(filePath, "utf8")) as RuleSettings;
			return parsed && typeof parsed === "object" ? parsed : {};
		} catch {
			return {};
		}
	}

	function loadRules(cwd: string): string[] {
		const projectRules = readSettingsFile(getProjectSettingsPath(cwd)).allowedRules;
		const globalRules = readSettingsFile(getGlobalSettingsPath()).allowedRules;
		const merged = new Set<string>();
		for (const rule of Array.isArray(projectRules) ? projectRules : []) merged.add(rule);
		for (const rule of Array.isArray(globalRules) ? globalRules : []) merged.add(rule);
		return Array.from(merged);
	}

	function saveRule(cwd: string, rule: string, scope: "project" | "global"): void {
		const filePath = scope === "project" ? getProjectSettingsPath(cwd) : getGlobalSettingsPath();
		const data = readSettingsFile(filePath);
		const rules = Array.isArray(data.allowedRules) ? data.allowedRules : [];
		if (rules.includes(rule)) return;
		rules.push(rule);
		data.allowedRules = rules;
		fs.mkdirSync(path.dirname(filePath), { recursive: true });
		fs.writeFileSync(filePath, JSON.stringify(data, null, 2), "utf8");
	}

	function getSkillDirs(cwd: string): { user: string[]; project: string[] } {
		const home = os.homedir();
		return {
			user: [path.join(home, ".pi", "agent", "skills"), path.join(home, ".agents", "skills")],
			project: [path.join(cwd, ".pi", "skills"), path.join(cwd, ".agents", "skills")],
		};
	}

	function getSkillInfo(resolvedPath: string, cwd: string): { type: "$user" | "$project"; name: string } | null {
		const skillDirs = getSkillDirs(cwd);

		for (const dir of skillDirs.user) {
			if (!resolvedPath.startsWith(`${dir}${path.sep}`)) continue;
			const relative = resolvedPath.slice(dir.length + 1);
			const name = relative.split(path.sep)[0];
			if (name) return { type: "$user", name };
		}

		for (const dir of skillDirs.project) {
			if (!resolvedPath.startsWith(`${dir}${path.sep}`)) continue;
			const relative = resolvedPath.slice(dir.length + 1);
			const name = relative.split(path.sep)[0];
			if (name) return { type: "$project", name };
		}

		return null;
	}

	function collectSkillMarkdownFiles(cwd: string): string[] {
		const skillDirs = getSkillDirs(cwd);
		const roots = [...skillDirs.user, ...skillDirs.project];
		const files: string[] = [];

		const visit = (dir: string) => {
			if (!fs.existsSync(dir)) return;
			let entries: fs.Dirent[] = [];
			try {
				entries = fs.readdirSync(dir, { withFileTypes: true });
			} catch {
				return;
			}
			for (const entry of entries) {
				const fullPath = path.join(dir, entry.name);
				if (entry.isDirectory()) {
					visit(fullPath);
					continue;
				}
				if (entry.isFile() && entry.name === "SKILL.md") files.push(fullPath);
			}
		};

		for (const root of roots) visit(root);
		return files;
	}

	function isAllowedBySkillCommandDocs(command: string, cwd: string): boolean {
		const normalized = normalizeCommand(command);
		if (!normalized) return false;
		for (const filePath of collectSkillMarkdownFiles(cwd)) {
			let content = "";
			try {
				content = fs.readFileSync(filePath, "utf8");
			} catch {
				continue;
			}
			const commands = extractCommandsFromSkillMarkdown(content);
			if (commands.includes(normalized)) return true;
		}
		return false;
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
			const clientsRaw = execFileSync("wezterm", ["cli", "list-clients", "--format", "json"], {
				encoding: "utf8",
			});
			const clients = parseJson<Array<{ focused_pane_id?: number }>>(clientsRaw) ?? [];
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

	function createSystemActionPrompt(title: string, body: string): ActionPromptHandle {
		const requestId = `permission-guard-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
		let off: () => void = () => {
			// no-op
		};

		const promise = new Promise<Decision | undefined>((resolve) => {
			off = pi.events.on("system-notify:action-prompt-result", (payload) => {
				const result = payload as ActionPromptResult;
				if (result.requestId !== requestId) return;
				off();
				if (!result.action) {
					resolve(undefined);
					return;
				}
				resolve(mapChoiceToDecision(result.action));
			});

			pi.events.emit("system-notify:action-prompt-request", {
				requestId,
				title: `pi: ${title}`,
				message: body,
				actions: ALLOW_OPTIONS,
				closeLabel: "Deny",
			});
		});

		const cancel = () => {
			off();
			pi.events.emit("system-notify:action-prompt-cancel", { requestId });
		};

		return { promise, cancel };
	}

	async function promptDecision(
		ctx: Parameters<Parameters<ExtensionAPI["on"]>[1]>[1],
		title: string,
		body: string,
	): Promise<Decision> {
		if (!ctx.hasUI) {
			return { allow: false, denyReason: `${title} blocked (no UI for confirmation)` };
		}

		const useNotificationRace = !isPiPaneVisible();
		const notificationHandle = useNotificationRace ? createSystemActionPrompt(title, body) : null;
		const uiAbort = new AbortController();
		const uiPromise = ctx.ui.select(`${title}\n\n${body}`, ALLOW_OPTIONS, { signal: uiAbort.signal });

		if (!notificationHandle) {
			const choice = (await uiPromise) as ToolPermissionOption | undefined;
			if (choice === "Deny with note") {
				const note = await ctx.ui.input("Deny reason (optional):", "explain what is not allowed");
				return mapChoiceToDecision(choice, note?.trim());
			}
			return mapChoiceToDecision(choice);
		}

		const decision = await new Promise<Decision>((resolve) => {
			let settled = false;
			const settle = (value: Decision, source: "ui" | "notification") => {
				if (settled) return;
				settled = true;
				if (source === "ui") {
					notificationHandle.cancel();
				} else {
					uiAbort.abort();
				}
				resolve(value);
			};

			uiPromise.then((choice) => {
				const uiChoice = choice as ToolPermissionOption | undefined;
				if (uiChoice === "Deny with note") {
					ctx.ui.input("Deny reason (optional):", "explain what is not allowed").then((note) => {
						settle(mapChoiceToDecision(uiChoice, note?.trim()), "ui");
					});
					return;
				}
				settle(mapChoiceToDecision(uiChoice), "ui");
			});

			notificationHandle.promise.then((value) => {
				if (!value) return;
				settle(value, "notification");
			});
		});

		return decision;
	}

	pi.on("tool_call", async (event, ctx) => {
		if (isPermissionGuardBypassed()) return undefined;
		const rules = loadRules(ctx.cwd);

		if (event.toolName === "bash") {
			const command = (event.input.command as string | undefined)?.trim();
			if (!command) return undefined;
			if (isActionAllowedByRules("bash", command, rules)) return undefined;
			if (isAllowedBySkillCommandDocs(command, ctx.cwd)) return undefined;

			const decision = await promptDecision(ctx, "Bash permission", `Command:\n  ${command}`);
			if (decision.allow) {
				if (decision.saveScope) saveRule(ctx.cwd, `Bash(${command})`, decision.saveScope);
				return undefined;
			}
			return { block: true, reason: `${decision.denyReason ?? "Denied by user"}: ${command}` };
		}

		if (event.toolName !== "read" && event.toolName !== "write" && event.toolName !== "edit") {
			return undefined;
		}

		const filePath = (event.input.path || event.input.file_path || event.input.file) as string | undefined;
		if (!filePath) return undefined;
		const resolvedPath = path.resolve(ctx.cwd, filePath);

		const skill = getSkillInfo(resolvedPath, ctx.cwd);
		if (skill) {
			const skillRule = `Skill(${skill.type}/${skill.name})`;
			const hasSkillReadAccess = isSkillReadAllowed(event.toolName, skill.type, skill.name, rules);
			if (hasSkillReadAccess) return undefined;

			const modeLabel = event.toolName === "read" ? "Skill permission" : "Skill write/edit permission";
			const decision = await promptDecision(
				ctx,
				modeLabel,
				`Allow plugin to use skill ${skill.name}?\nTool: ${event.toolName}\nPath:\n  ${resolvedPath}`,
			);
			if (decision.allow) {
				// Skill(...) grants read access to the skill directory only. Writes/edits remain separately gated.
				if (decision.saveScope && event.toolName === "read") saveRule(ctx.cwd, skillRule, decision.saveScope);
				return undefined;
			}
			return { block: true, reason: `${decision.denyReason ?? "Denied by user"}: ${skillRule}` };
		}

		if (isInsideProject(resolvedPath, ctx.cwd)) return undefined;

		const tool = event.toolName;
		if (isActionAllowedByRules(tool, resolvedPath, rules)) return undefined;

		const prefixMap: Record<"read" | "write" | "edit", string> = {
			read: "FileRead",
			write: "FileWrite",
			edit: "FileEdit",
		};
		const rulePrefix = prefixMap[tool];

		const decision = await promptDecision(
			ctx,
			`${tool} outside project directory`,
			`Tool wants to access:\n  ${resolvedPath}`,
		);
		if (decision.allow) {
			if (decision.saveScope) saveRule(ctx.cwd, `${rulePrefix}(${resolvedPath})`, decision.saveScope);
			return undefined;
		}

		return { block: true, reason: `${decision.denyReason ?? "Denied by user"}: ${tool} ${resolvedPath}` };
	});
}
