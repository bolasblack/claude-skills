import type { SearchProvider, SearchResult, SearchOptions } from "./types.js";
import { fetchWithRetry, getApiKey } from "./types.js";

const NAME = "langsearch";

/**
 * Extract search results from LangSearch Web Search API response.
 *
 * Response docs: https://docs.langsearch.com/api/web-search-api
 * Response is Bing-compatible, wrapped in a `data` envelope:
 * ```json
 * {
 *   "code": 200,
 *   "data": {
 *     "webPages": {
 *       "value": [
 *         { "name": "...", "url": "...", "snippet": "...", "datePublished": null }
 *       ]
 *     }
 *   }
 * }
 * ```
 */
function extractResults(json: unknown): SearchResult[] {
	const data = json as {
		data?: {
			webPages?: {
				value?: Array<{
					name: string;
					url: string;
					snippet?: string;
					datePublished?: string | null;
				}>;
			};
		};
	};
	return (data.data?.webPages?.value ?? []).map((r) => ({
		title: r.name,
		url: r.url,
		snippet: r.snippet,
		age: r.datePublished ?? undefined,
	}));
}

export const langsearchProvider: SearchProvider = {
	name: NAME,
	available() {
		return !!getApiKey(NAME);
	},
	async search(query: string, options?: SearchOptions): Promise<SearchResult[]> {
		const apiKey = getApiKey(NAME)!;
		// LangSearch has no native domain filtering; use site: operator in query
		let q = query;
		if (options?.allowedDomains?.length) {
			q += " " + options.allowedDomains.map((d) => `site:${d}`).join(" OR ");
		}
		if (options?.blockedDomains?.length) {
			q += " " + options.blockedDomains.map((d) => `-site:${d}`).join(" ");
		}

		const resp = await fetchWithRetry(
			"https://api.langsearch.com/v1/web-search",
			{
				method: "POST",
				headers: {
					"Authorization": `Bearer ${apiKey}`,
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					query: q,
					freshness: "noLimit",
					summary: false,
					count: 10,
				}),
			},
			options?.signal,
		);

		if (!resp.ok) {
			const text = await resp.text().catch(() => "");
			throw new Error(`LangSearch API error ${resp.status}: ${text}`);
		}

		return extractResults(await resp.json());
	},
};
