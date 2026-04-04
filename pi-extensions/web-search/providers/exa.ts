import type { SearchProvider, SearchResult, SearchOptions } from "./types.js";
import { fetchWithRetry, getApiKey } from "./types.js";

const NAME = "exa";

/**
 * Extract search results from Exa Search API response.
 *
 * Response docs: https://docs.exa.ai/reference/search
 * ```json
 * {
 *   "results": [
 *     { "title": "...", "url": "...", "text": "...", "publishedDate": "2024-01-15" }
 *   ]
 * }
 * ```
 */
function extractResults(json: unknown): SearchResult[] {
	const data = json as {
		results?: Array<{
			title: string;
			url: string;
			text?: string;
			publishedDate?: string;
		}>;
	};
	return (data.results ?? []).map((r) => ({
		title: r.title,
		url: r.url,
		snippet: r.text,
		age: r.publishedDate,
	}));
}

export const exaProvider: SearchProvider = {
	name: NAME,
	available() {
		return !!getApiKey(NAME);
	},
	async search(query: string, options?: SearchOptions): Promise<SearchResult[]> {
		const apiKey = getApiKey(NAME)!;

		const resp = await fetchWithRetry(
			"https://api.exa.ai/search",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"x-api-key": apiKey,
				},
				// Exa natively supports includeDomains / excludeDomains
				body: JSON.stringify({
					query,
					type: "auto",
					numResults: 10,
					contents: {
						text: { maxCharacters: 300 },
					},
					...(options?.allowedDomains?.length ? { includeDomains: options.allowedDomains } : {}),
					...(options?.blockedDomains?.length ? { excludeDomains: options.blockedDomains } : {}),
				}),
			},
			options?.signal,
		);

		if (!resp.ok) {
			const text = await resp.text().catch(() => "");
			throw new Error(`Exa API error ${resp.status}: ${text}`);
		}

		return extractResults(await resp.json());
	},
};
