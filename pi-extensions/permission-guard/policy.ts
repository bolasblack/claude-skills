import * as path from "node:path";

export type GuardTool = "bash" | "read" | "write" | "edit";

export function normalizeCommand(command: string): string {
	return command.trim().replace(/\s+/g, " ");
}

export function matchRuleGlob(glob: string, target: string, isPath = true): boolean {
	const escapeRegex = (s: string) => s.replace(/[.+^${}()|[\]\\]/g, "\\$&");
	const parts = glob.split("**");
	const regexParts = parts.map((part) => {
		const subParts = part.split("*");
		return subParts.map((sp) => escapeRegex(sp)).join(isPath ? "[^/]*" : ".*");
	});
	return new RegExp(`^${regexParts.join(".*")}$`).test(target);
}

export function isActionAllowedByRules(tool: GuardTool, target: string, rules: string[]): boolean {
	const prefixMap: Record<GuardTool, string> = {
		bash: "Bash",
		read: "FileRead",
		write: "FileWrite",
		edit: "FileEdit",
	};
	const prefix = prefixMap[tool];
	for (const rule of rules) {
		if (!rule.startsWith(`${prefix}(`) || !rule.endsWith(")")) continue;
		const glob = rule.slice(prefix.length + 1, -1);
		if (matchRuleGlob(glob, target, tool !== "bash")) return true;
	}
	return false;
}

export function isInsideProject(filePath: string, cwd: string): boolean {
	const resolved = path.resolve(cwd, filePath);
	const cwdPrefix = cwd.endsWith(path.sep) ? cwd : `${cwd}${path.sep}`;
	return resolved === cwd || resolved.startsWith(cwdPrefix);
}

export function extractCommandsFromSkillMarkdown(markdown: string): string[] {
	const commands = new Set<string>();
	const blockRegex = /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g;
	let match: RegExpExecArray | null;

	while ((match = blockRegex.exec(markdown)) !== null) {
		const lang = (match[1] || "").toLowerCase();
		const body = match[2] || "";
		const isShellBlock = ["bash", "sh", "shell", "zsh", "fish"].includes(lang);
		const isConsoleBlock = lang === "console" || lang === "terminal";
		if (!isShellBlock && !isConsoleBlock) continue;

		for (const rawLine of body.split("\n")) {
			const line = rawLine.trim();
			if (!line) continue;
			if (line.startsWith("#")) continue;
			if (isConsoleBlock && !line.startsWith("$")) continue;
			const normalized = normalizeCommand(line.startsWith("$") ? line.slice(1) : line);
			if (normalized) commands.add(normalized);
		}
	}

	return Array.from(commands);
}

export function isSkillReadAllowed(
	tool: "read" | "write" | "edit",
	skillType: "$user" | "$project",
	skillName: string,
	rules: string[],
): boolean {
	if (tool !== "read") return false;
	return rules.includes(`Skill(${skillType}/${skillName})`);
}

export function isPermissionGuardBypassed(env: NodeJS.ProcessEnv = process.env): boolean {
	const raw = env.PI_PERMISSION_GUARD_BYPASS?.trim().toLowerCase();
	return raw === "1" || raw === "true" || raw === "yes";
}
