export type ToolPermissionOption =
	| "Allow"
	| "Allow always (project level)"
	| "Allow always (user level)"
	| "Deny"
	| "Deny with note";

export interface Decision {
	allow: boolean;
	saveScope?: "project" | "global";
	denyReason?: string;
}

export function mapChoiceToDecision(choice: string | undefined, noteText?: string): Decision {
	if (choice === "Allow") return { allow: true };
	if (choice === "Allow always (project level)") return { allow: true, saveScope: "project" };
	if (choice === "Allow always (user level)") return { allow: true, saveScope: "global" };
	if (choice === "Deny with note") {
		const note = noteText?.trim();
		return { allow: false, denyReason: note ? `Denied by user: ${note}` : "Denied by user" };
	}
	return { allow: false, denyReason: "Denied by user" };
}
