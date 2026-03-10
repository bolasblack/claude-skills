import { describe, expect, test } from "bun:test";
import {
	extractCommandsFromSkillMarkdown,
	isActionAllowedByRules,
	isInsideProject,
	isSkillReadAllowed,
	normalizeCommand,
	isPermissionGuardBypassed,
} from "../policy.ts";

describe("permission-guard policy", () => {
	test("normalizeCommand collapses whitespace and trims", () => {
		expect(normalizeCommand("  ls   -la   /tmp  ")).toBe("ls -la /tmp");
	});

	test("extractCommandsFromSkillMarkdown parses shell and console blocks", () => {
		const md = `
# Skill

\`\`\`bash
# comment
lsof -i :3000
\`\`\`

\`\`\`console
$ rg -n "foo" src
not-a-command
\`\`\`
`;
		const commands = extractCommandsFromSkillMarkdown(md);
		expect(commands.sort()).toEqual(["lsof -i :3000", 'rg -n "foo" src'].sort());
	});

	test("command matching is strict; lsof does not allow ls", () => {
		const md = "```bash\nlsof\n```";
		const commands = extractCommandsFromSkillMarkdown(md);
		expect(commands.includes("lsof")).toBe(true);
		expect(commands.includes("ls")).toBe(false);
	});

	test("isActionAllowedByRules supports glob rules per tool", () => {
		const rules = ["Bash(npm run *)", "FileRead(/var/log/**)"];
		expect(isActionAllowedByRules("bash", "npm run check", rules)).toBe(true);
		expect(isActionAllowedByRules("bash", "npm test", rules)).toBe(false);
		expect(isActionAllowedByRules("read", "/var/log/app/error.log", rules)).toBe(true);
	});

	test("Skill rule grants read only, not edit/write", () => {
		const rules = ["Skill($user/my-skill)"];
		expect(isSkillReadAllowed("read", "$user", "my-skill", rules)).toBe(true);
		expect(isSkillReadAllowed("edit", "$user", "my-skill", rules)).toBe(false);
		expect(isSkillReadAllowed("write", "$user", "my-skill", rules)).toBe(false);
	});

	test("isInsideProject returns true only for cwd subtree", () => {
		const cwd = "/repo";
		expect(isInsideProject("/repo/src/a.ts", cwd)).toBe(true);
		expect(isInsideProject("/tmp/a.ts", cwd)).toBe(false);
	});

	test("isPermissionGuardBypassed supports 1/true/yes", () => {
		expect(isPermissionGuardBypassed({ PI_PERMISSION_GUARD_BYPASS: "1" } as NodeJS.ProcessEnv)).toBe(true);
		expect(isPermissionGuardBypassed({ PI_PERMISSION_GUARD_BYPASS: "true" } as NodeJS.ProcessEnv)).toBe(true);
		expect(isPermissionGuardBypassed({ PI_PERMISSION_GUARD_BYPASS: "YES" } as NodeJS.ProcessEnv)).toBe(true);
		expect(isPermissionGuardBypassed({ PI_PERMISSION_GUARD_BYPASS: "0" } as NodeJS.ProcessEnv)).toBe(false);
		expect(isPermissionGuardBypassed({} as NodeJS.ProcessEnv)).toBe(false);
	});
});
