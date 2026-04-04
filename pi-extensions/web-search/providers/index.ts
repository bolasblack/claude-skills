export type { SearchProvider, SearchResult, SearchOptions } from "./types.js";
export { braveProvider } from "./brave.js";
export { tavilyProvider } from "./tavily.js";
export { exaProvider } from "./exa.js";
export { langsearchProvider } from "./langsearch.js";
export { linkupProvider } from "./linkup.js";

import type { SearchProvider } from "./types.js";
import { braveProvider } from "./brave.js";
import { tavilyProvider } from "./tavily.js";
import { exaProvider } from "./exa.js";
import { langsearchProvider } from "./langsearch.js";
import { linkupProvider } from "./linkup.js";

export const ALL_PROVIDERS: SearchProvider[] = [
  braveProvider,
  tavilyProvider,
  exaProvider,
  langsearchProvider,
  linkupProvider,
];

/**
 * Resolve the active search provider.
 *
 * 1. If PI_WEB_SEARCH_PROVIDER is set, use that provider (must have API key).
 * 2. Otherwise, use the first provider with a configured API key.
 */
export function resolveProvider(): SearchProvider | undefined {
  const explicit = process.env.PI_WEB_SEARCH_PROVIDER?.toLowerCase();
  if (explicit) {
    const provider = ALL_PROVIDERS.find((p) => p.name === explicit);
    if (provider?.available()) return provider;
  }
  return ALL_PROVIDERS.find((p) => p.available());
}
