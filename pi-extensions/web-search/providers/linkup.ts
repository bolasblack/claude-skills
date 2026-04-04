import type { SearchProvider, SearchResult, SearchOptions } from "./types.js";
import { fetchWithRetry, getApiKey } from "./types.js";

const NAME = "linkup";

/**
 * Extract search results from Linkup Search API response.
 *
 * Response docs: https://docs.linkup.so/pages/documentation/api-reference/endpoint/post-search
 * OpenAPI spec: https://api.linkup.so/v1/openapi.json
 *
 * With outputType "searchResults", response is:
 * ```json
 * {
 *   "results": [
 *     { "type": "text", "name": "...", "url": "...", "content": "..." },
 *     { "type": "image", "name": "...", "url": "..." }
 *   ]
 * }
 * ```
 * We only extract "text" results.
 */
function extractResults(json: unknown): SearchResult[] {
  const data = json as {
    results?: Array<{
      type: string;
      name: string;
      url: string;
      content?: string;
    }>;
  };
  return (data.results ?? [])
    .filter((r) => r.type === "text")
    .map((r) => ({
      title: r.name,
      url: r.url,
      snippet: r.content,
    }));
}

export const linkupProvider: SearchProvider = {
  name: NAME,
  available() {
    return !!getApiKey(NAME);
  },
  async search(
    query: string,
    options?: SearchOptions,
  ): Promise<SearchResult[]> {
    const apiKey = getApiKey(NAME)!;

    const resp = await fetchWithRetry(
      "https://api.linkup.so/v1/search",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
        // Linkup natively supports includeDomains / excludeDomains
        body: JSON.stringify({
          q: query,
          depth: "standard",
          outputType: "searchResults",
          maxResults: 10,
          ...(options?.allowedDomains?.length ? { includeDomains: options.allowedDomains } : {}),
          ...(options?.blockedDomains?.length ? { excludeDomains: options.blockedDomains } : {}),
        }),
      },
      options?.signal,
    );

    if (!resp.ok) {
      const text = await resp.text().catch(() => "");
      throw new Error(`Linkup API error ${resp.status}: ${text}`);
    }

    return extractResults(await resp.json());
  },
};
