import type { SearchProvider, SearchResult, SearchOptions } from "./types.js";
import { fetchWithRetry, getApiKey } from "./types.js";

const NAME = "tavily";

/**
 * Extract search results from Tavily Search API response.
 *
 * Response docs: https://docs.tavily.com/documentation/api-reference/endpoint/search
 * ```json
 * {
 *   "results": [
 *     { "title": "...", "url": "...", "content": "...", "published_date": "2024-01-15" }
 *   ]
 * }
 * ```
 */
function extractResults(json: unknown): SearchResult[] {
	const data = json as {
		results?: Array<{
			title: string;
			url: string;
			content?: string;
			published_date?: string;
		}>;
	};
	return (data.results ?? []).map((r) => ({
		title: r.title,
		url: r.url,
		snippet: r.content,
		age: r.published_date,
	}));
}

export const tavilyProvider: SearchProvider = {
	name: NAME,
	available() {
		return !!getApiKey(NAME);
	},
	async search(query: string, options?: SearchOptions): Promise<SearchResult[]> {
		const apiKey = getApiKey(NAME)!;

		const resp = await fetchWithRetry(
			"https://api.tavily.com/search",
			{
				method: "POST",
				headers: { "Content-Type": "application/json" },
				// Tavily natively supports include_domains / exclude_domains
				body: JSON.stringify({
					api_key: apiKey,
					query,
					max_results: 10,
					include_answer: false,
					...(options?.allowedDomains?.length ? { include_domains: options.allowedDomains } : {}),
					...(options?.blockedDomains?.length ? { exclude_domains: options.blockedDomains } : {}),
				}),
			},
			options?.signal,
		);

		if (!resp.ok) {
			const text = await resp.text().catch(() => "");
			throw new Error(`Tavily API error ${resp.status}: ${text}`);
		}

		return extractResults(await resp.json());
	},
};
