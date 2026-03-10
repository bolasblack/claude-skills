import { describe, expect, test } from "bun:test";
import { parseActionPromptOutcome, shorten } from "../macos-wez.ts";

describe("system-notify macos-wez pure helpers", () => {
	test("shorten normalizes whitespace and truncates with ellipsis", () => {
		expect(shorten("  hello   world  ", 20)).toBe("hello world");
		expect(shorten("a ".repeat(30), 20).endsWith("...")).toBe(true);
		expect(shorten("a ".repeat(30), 20).length).toBe(20);
	});

	test("parseActionPromptOutcome focuses when notification body is clicked", () => {
		const clicked = JSON.stringify({ activationType: "contentsClicked", activationValue: "Allow" });
		expect(parseActionPromptOutcome(clicked)).toEqual({
			action: "Allow",
			activationType: "contentsclicked",
			shouldFocus: true,
		});
	});

	test("parseActionPromptOutcome focuses only for first button (显示/Focus terminal)", () => {
		const focusAction = JSON.stringify({ activationType: "actionClicked", activationValue: "显示" });
		expect(parseActionPromptOutcome(focusAction)).toEqual({
			action: "显示",
			activationType: "actionclicked",
			shouldFocus: true,
		});

		const nonFocusAction = JSON.stringify({ activationType: "actionClicked", activationValue: "Allow" });
		expect(parseActionPromptOutcome(nonFocusAction)).toEqual({
			action: "Allow",
			activationType: "actionclicked",
			shouldFocus: false,
		});
	});

	test("parseActionPromptOutcome supports fallback fields and no-focus outcomes", () => {
		const fallback = JSON.stringify({ event: "closed", value: "Deny" });
		expect(parseActionPromptOutcome(fallback)).toEqual({
			action: "Deny",
			activationType: "closed",
			shouldFocus: false,
		});
	});

	test("parseActionPromptOutcome tolerates invalid JSON", () => {
		expect(parseActionPromptOutcome("not-json")).toEqual({
			action: undefined,
			activationType: "",
			shouldFocus: false,
		});
	});
});
