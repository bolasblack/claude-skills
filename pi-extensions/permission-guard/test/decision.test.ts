import { describe, expect, test } from "bun:test";
import { mapChoiceToDecision } from "../decision.ts";

describe("permission-guard decision mapping", () => {
	test("Allow returns allow=true", () => {
		expect(mapChoiceToDecision("Allow")).toEqual({ allow: true });
	});

	test("Allow always maps to project/global persistence", () => {
		expect(mapChoiceToDecision("Allow always (project level)")).toEqual({ allow: true, saveScope: "project" });
		expect(mapChoiceToDecision("Allow always (user level)")).toEqual({ allow: true, saveScope: "global" });
	});

	test("Deny with note includes note text", () => {
		expect(mapChoiceToDecision("Deny with note", "too broad")).toEqual({
			allow: false,
			denyReason: "Denied by user: too broad",
		});
	});

	test("Deny note is trimmed", () => {
		expect(mapChoiceToDecision("Deny with note", "   too broad   ")).toEqual({
			allow: false,
			denyReason: "Denied by user: too broad",
		});
	});

	test("Deny with note without note and unknown choice fallback to deny", () => {
		expect(mapChoiceToDecision("Deny with note")).toEqual({ allow: false, denyReason: "Denied by user" });
		expect(mapChoiceToDecision(undefined)).toEqual({ allow: false, denyReason: "Denied by user" });
	});
});
