# Web Search Extension — Agent Instructions

## Adding or Updating a Provider

### 1. Get API documentation

Spawn a subagent to find the **exact documentation URL** for the provider's search endpoint response format:

```
Find the official API documentation URL for <ProviderName> Search API that documents
the response JSON schema/structure. I need the URL that shows the response fields
(title, url, snippet equivalent, date equivalent), not a marketing page.
Start from: <provider docs landing page>
```

### 2. Verify the documentation URL

Spawn a subagent to verify the URL is real and accessible:

```
Verify this URL is a real, accessible documentation page (not a 404 or redirect
to a generic page):

<URL from step 1>

Fetch it and check:
1. HTTP status code
2. Does the page content mention the expected response fields?
3. If invalid, find the correct URL.
```

If invalid, repeat steps 1-2 until a working URL is confirmed.

### 3. Verify the response format

Test the actual API response with a real or dummy API key:

```bash
curl -s -X POST "<endpoint>" \
  -H "Authorization: Bearer <key>" \
  -H "Content-Type: application/json" \
  -d '{"query":"hello world"}' | head -500
```

Compare the actual JSON structure against the documentation. Pay attention to:
- Envelope wrappers (e.g., LangSearch wraps everything in `data`)
- Field names (e.g., `name` vs `title`, `content` vs `snippet` vs `description`)
- Null vs missing fields for dates

### 4. Implement the provider

Create `providers/<name>.ts` following the existing pattern:

```ts
import type { SearchProvider, SearchResult, SearchOptions } from "./types.js";
import { fetchWithRetry, getApiKey } from "./types.js";

const NAME = "<name>";

/**
 * Extract search results from <ProviderName> API response.
 *
 * Response docs: <verified URL from step 2>
 * ```json
 * <example response structure>
 * ```
 */
function extractResults(json: unknown): SearchResult[] {
    // Type assertion and field mapping
}

export const <name>Provider: SearchProvider = {
    name: NAME,
    available() { return !!getApiKey(NAME); },
    async search(query, options) {
        // fetchWithRetry call + extractResults
    },
};
```

### 5. Register the provider

In `providers/index.ts`:
- Add import
- Add to `ALL_PROVIDERS` array (order = priority)

### 6. Update README.md

Add the provider to the tables (Providers, Configuration).

## Env var naming convention

Env var is derived automatically from the provider name:

```
PI_WEB_SEARCH_${toUpperSnakeCase(providerName)}_API_KEY
```

Settings key is the provider name directly:

```json
{ "webSearchApiKey": { "<providerName>": "..." } }
```

## Verifying all providers

To re-verify all documentation links and response formats:

```
Spawn a subagent with this task:

Verify that each of these URLs is a real, accessible documentation page.
For each URL, fetch it and confirm it contains documentation about the
search API response format.

1. Brave: https://api-dashboard.search.brave.com/app/documentation/web-search/responses
2. Tavily: https://docs.tavily.com/documentation/api-reference/endpoint/search
3. Exa: https://docs.exa.ai/reference/search
4. LangSearch: https://docs.langsearch.com/api/web-search-api
5. Linkup: https://docs.linkup.so/pages/documentation/api-reference/endpoint/post-search

For each: fetch, check HTTP status, check content mentions expected fields.
Report VALID or INVALID with correct URL if invalid.
```

Then fix any broken links in the corresponding `providers/<name>.ts` file's `extractResults` docstring.
