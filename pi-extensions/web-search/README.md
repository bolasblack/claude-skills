# web-search Extension Maintenance Guide

## Overview

Multi-provider web search tool for pi. Zero external dependencies — uses only `fetch()` with automatic retry on 429/5xx (respects `retry-after` headers).

## Providers

| Provider | Env var | Free tier | Docs |
|----------|---------|-----------|------|
| Brave | `PI_WEB_SEARCH_BRAVE_API_KEY` | 2000 queries/mo | https://brave.com/search/api/ |
| Tavily | `PI_WEB_SEARCH_TAVILY_API_KEY` | 1000 queries/mo | https://docs.tavily.com/ |
| Exa | `PI_WEB_SEARCH_EXA_API_KEY` | 1000 queries/mo | https://exa.ai/docs/reference/search-api-guide |
| LangSearch | `PI_WEB_SEARCH_LANGSEARCH_API_KEY` | Free | https://docs.langsearch.com/api/web-search-api |
| Linkup | `PI_WEB_SEARCH_LINKUP_API_KEY` | — | https://docs.linkup.so/ |

## Configuration

API keys can be set via **environment variables** or **pi settings.json**.

### Environment variables

```bash
export PI_WEB_SEARCH_BRAVE_API_KEY=your-key
```

### Settings (global or project)

```json
// ~/.pi/agent/settings.json or .pi/settings.json
{
  "webSearchApiKey": {
    "brave": "your-key"
  }
}
```

| Provider | Env var | Settings key |
|----------|---------|-------------|
| Brave | `PI_WEB_SEARCH_BRAVE_API_KEY` | `webSearchApiKey.brave` |
| Tavily | `PI_WEB_SEARCH_TAVILY_API_KEY` | `webSearchApiKey.tavily` |
| Exa | `PI_WEB_SEARCH_EXA_API_KEY` | `webSearchApiKey.exa` |
| LangSearch | `PI_WEB_SEARCH_LANGSEARCH_API_KEY` | `webSearchApiKey.langsearch` |
| Linkup | `PI_WEB_SEARCH_LINKUP_API_KEY` | `webSearchApiKey.linkup` |

Env vars take priority over settings. Project settings override global settings.

The first available provider is used, in order: Brave > Tavily > Exa > LangSearch > Linkup.

Override priority with `PI_WEB_SEARCH_PROVIDER=brave|tavily|exa|langsearch|linkup`.

## Retry Behavior

All providers use `fetchWithRetry()` from `providers/types.ts`:

- Retries on 429, 503, and 5xx errors (up to 5 times)
- Respects `retry-after` and `retry-after-ms` headers
- Falls back to exponential backoff (500ms base, max 32s) with jitter
- Supports abort signal during wait

## Architecture

```
index.ts
  → resolveProvider()  (from providers/index.ts)
  → provider.search()  (from providers/<name>.ts)
    → fetchWithRetry() (from providers/types.ts)
    → normalize to SearchResult[]
  → format as markdown
```

## Files

```
.pi/extensions/web-search/
├── index.ts                    # Tool registration + result formatting
├── providers/
│   ├── types.ts                # SearchProvider interface + fetchWithRetry
│   ├── index.ts                # Provider registry + resolveProvider()
│   ├── brave.ts                # Brave Search API adapter
│   ├── tavily.ts               # Tavily API adapter
│   ├── exa.ts                  # Exa API adapter
│   ├── langsearch.ts           # LangSearch API adapter
│   └── linkup.ts               # Linkup API adapter
├── package.json                # Minimal (no dependencies)
├── .gitignore
└── MAINTENANCE.md              # This file
```

## Adding a New Provider

1. Create `providers/<name>.ts`:

```ts
import type { SearchProvider, SearchResult, SearchOptions } from "./types.js";
import { fetchWithRetry } from "./types.js";

const ENV_KEY = "PI_WEB_SEARCH_<NAME>_API_KEY";

export const <name>Provider: SearchProvider = {
    name: "<name>",
    envKey: ENV_KEY,
    available() { return !!process.env[ENV_KEY]; },
    async search(query: string, options?: SearchOptions): Promise<SearchResult[]> {
        const resp = await fetchWithRetry("<endpoint>", {
            method: "POST",
            headers: { "Authorization": `Bearer ${process.env[ENV_KEY]}`, "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
        }, options?.signal);
        if (!resp.ok) throw new Error(`<Name> API error ${resp.status}`);
        const json = await resp.json();
        return json.results.map(r => ({ title: r.title, url: r.url, snippet: r.text }));
    },
};
```

2. Export from `providers/index.ts` and add to `ALL_PROVIDERS`.
3. Update this doc's provider table.
