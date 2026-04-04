/**
 * WebSearch Extension — Multi-provider web search tool.
 *
 * Supports: Brave, Tavily, Exa, LangSearch, Linkup.
 * The first provider with a configured API key is used.
 * Override with PI_WEB_SEARCH_PROVIDER env var.
 *
 * All providers use fetchWithRetry which respects retry-after headers
 * and does exponential backoff on 429/5xx errors.
 */

import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { truncateTail, DEFAULT_MAX_BYTES, DEFAULT_MAX_LINES } from "@mariozechner/pi-coding-agent";
import { Type } from "@sinclair/typebox";
import { resolveProvider, ALL_PROVIDERS } from "./providers/index.js";

const WEB_SEARCH_PARAMS = Type.Object({
	query: Type.String({ description: "The search query to use" }),
	allowed_domains: Type.Optional(
		Type.Array(Type.String(), { description: "Only include search results from these domains" }),
	),
	blocked_domains: Type.Optional(
		Type.Array(Type.String(), { description: "Never include search results from these domains" }),
	),
});

function getCurrentDate(): string {
	const now = new Date();
	const months = [
		"January", "February", "March", "April", "May", "June",
		"July", "August", "September", "October", "November", "December",
	];
	return `${months[now.getMonth()]} ${now.getFullYear()}`;
}

export default function webSearchExtension(pi: ExtensionAPI) {
	const provider = resolveProvider();
	if (!provider) {
		return;
	}

	pi.registerTool({
		name: "web_search",
		label: "Web Search",
		description: `
- Allows you to search the web and use the results to inform responses
- Provides up-to-date information for current events and recent data
- Returns search result information formatted as search result blocks, including links as markdown hyperlinks
- Use this tool for accessing information beyond your knowledge cutoff
- Searches are performed via external search provider (${provider.name})

CRITICAL REQUIREMENT - You MUST follow this:
  - After answering the user's question, you MUST include a "Sources:" section at the end of your response
  - In the Sources section, list all relevant URLs from the search results as markdown hyperlinks: [Title](URL)
  - This is MANDATORY - never skip including sources in your response
  - Example format:

    [Your answer here]

    Sources:
    - [Source Title 1](https://example.com/1)
    - [Source Title 2](https://example.com/2)

Usage notes:
  - Domain filtering is supported to include or block specific websites

IMPORTANT - Use the correct year in search queries:
  - You MUST use the current year when searching for recent information, documentation, or current events
  - The current date will be shown in the search results header
  - Example: If the user asks for "latest React docs", search for "React documentation" with the current year, NOT last year
`,
		promptSnippet: "Search the web for current information, recent events, documentation updates, or any real-time data.",
		parameters: WEB_SEARCH_PARAMS,
		async execute(_toolCallId, params, signal, onUpdate) {
			if (params.query.length < 2) {
				throw new Error("Search query must be at least 2 characters.");
			}
			if (params.allowed_domains?.length && params.blocked_domains?.length) {
				throw new Error("Cannot specify both allowed_domains and blocked_domains. Use one or the other.");
			}

			// Re-resolve each call (env vars may change at runtime)
			const currentProvider = resolveProvider();
			if (!currentProvider) {
				const names = ALL_PROVIDERS.map((p) => p.name).join(", ");
				throw new Error(`No web search provider configured. Set PI_WEB_SEARCH_<PROVIDER>_API_KEY or webSearchApiKey.<provider> in settings. Providers: ${names}`);
			}

			onUpdate?.({
				content: [{ type: "text", text: `Searching (${currentProvider.name}): ${params.query}` }],
				details: { query: params.query, provider: currentProvider.name, status: "searching" },
			});

			const start = performance.now();
			const results = await currentProvider.search(params.query, {
				signal: signal ?? undefined,
				allowedDomains: params.allowed_domains,
				blockedDomains: params.blocked_domains,
			});
			const durationSeconds = (performance.now() - start) / 1000;

			onUpdate?.({
				content: [{ type: "text", text: `Found ${results.length} results (${durationSeconds.toFixed(1)}s)` }],
				details: { resultCount: results.length, provider: currentProvider.name, status: "done" },
			});

			const lines: string[] = [];
			lines.push(`Web search results for query: "${params.query}" (searched on ${getCurrentDate()})`, "");

			if (results.length === 0) {
				lines.push("No results found.");
			} else {
				for (let i = 0; i < results.length; i++) {
					const r = results[i];
					lines.push(`${i + 1}. [${r.title}](${r.url})`);
					if (r.age) lines.push(`   Age: ${r.age}`);
					if (r.snippet) lines.push(`   ${r.snippet}`);
					lines.push("");
				}
			}

			lines.push("");
			lines.push("REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks [Title](URL).");

			const text = truncateTail(lines.join("\n"), {
				maxBytes: DEFAULT_MAX_BYTES,
				maxLines: DEFAULT_MAX_LINES,
			}).content;

			return {
				content: [{ type: "text", text }],
				details: {
					query: params.query,
					resultCount: results.length,
					provider: currentProvider.name,
					durationSeconds,
				},
			};
		},
	});
}
