import type { SearchProvider, SearchResult, SearchOptions } from "./types.js";
import { fetchWithRetry, getApiKey } from "./types.js";

const NAME = "brave";

/**
 * Extract search results from Brave Web Search API response.
 *
 * Response docs: https://api-dashboard.search.brave.com/app/documentation/web-search/responses
 * ```json
 * {
 *   "web": {
 *     "results": [
 *       { "title": "...", "url": "...", "description": "...", "page_age": "2024-01-15" }
 *     ]
 *   }
 * }
 * ```
 */
function extractResults(json: unknown): SearchResult[] {
	const data = json as {
		web?: {
			results?: Array<{
				title: string;
				url: string;
				description?: string;
				page_age?: string;
			}>;
		};
	};
	return (data.web?.results ?? []).map((r) => ({
		title: r.title,
		url: r.url,
		snippet: r.description,
		age: r.page_age,
	}));
}

export const braveProvider: SearchProvider = {
	name: NAME,
	available() {
		return !!getApiKey(NAME);
	},
	async search(query: string, options?: SearchOptions): Promise<SearchResult[]> {
		const apiKey = getApiKey(NAME)!;
		// Brave supports site: operator in query for domain filtering
		let q = query;
		if (options?.allowedDomains?.length) {
			q += " " + options.allowedDomains.map((d) => `site:${d}`).join(" OR ");
		}
		if (options?.blockedDomains?.length) {
			q += " " + options.blockedDomains.map((d) => `-site:${d}`).join(" ");
		}
		const params = new URLSearchParams({ q, count: "10" });

		const resp = await fetchWithRetry(
			`https://api.search.brave.com/res/v1/web/search?${params}`,
			{
				headers: {
					"Accept": "application/json",
					"Accept-Encoding": "gzip",
					"X-Subscription-Token": apiKey,
				},
			},
			options?.signal,
		);

		if (!resp.ok) {
			const text = await resp.text().catch(() => "");
			throw new Error(`Brave API error ${resp.status}: ${text}`);
		}

		return extractResults(await resp.json());
	},
};
