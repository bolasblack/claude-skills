import { readFileSync, existsSync } from "fs";
import { join } from "path";
import { homedir } from "os";

export interface SearchResult {
	title: string;
	url: string;
	snippet?: string;
	age?: string;
}

export interface SearchOptions {
	signal?: AbortSignal;
	allowedDomains?: string[];
	blockedDomains?: string[];
}

export interface SearchProvider {
	name: string;
	available(): boolean;
	search(query: string, options?: SearchOptions): Promise<SearchResult[]>;
}

// ---------------------------------------------------------------------------
// Settings helper — reads API keys from pi settings.json
// ---------------------------------------------------------------------------

interface PiSettings {
	webSearchApiKey?: Record<string, string>;
}

let _settingsCache: { value: PiSettings; ts: number } | undefined;
const SETTINGS_TTL_MS = 30_000; // Re-read settings at most every 30s

function readPiSettings(): PiSettings {
	const now = Date.now();
	if (_settingsCache && now - _settingsCache.ts < SETTINGS_TTL_MS) {
		return _settingsCache.value;
	}

	const paths = [
		join(process.env.PI_AGENT_DIR ?? join(homedir(), ".pi", "agent"), "settings.json"),
		join(process.cwd(), ".pi", "settings.json"),
	];
	const merged: PiSettings = {};
	// Read global first, then project (project overrides)
	for (const p of paths) {
		if (!existsSync(p)) continue;
		try {
			const data = JSON.parse(readFileSync(p, "utf-8"));
			if (data.webSearchApiKey && typeof data.webSearchApiKey === "object") {
				merged.webSearchApiKey = { ...merged.webSearchApiKey, ...data.webSearchApiKey };
			}
		} catch {
			// Ignore corrupt settings
		}
	}

	_settingsCache = { value: merged, ts: now };
	return merged;
}

function toUpperSnakeCase(s: string): string {
	return s.replace(/([a-z])([A-Z])/g, "$1_$2").replace(/[\s-]+/g, "_").toUpperCase();
}

/**
 * Get an API key from environment variable or pi settings.
 *
 * Env var: PI_WEB_SEARCH_<UPPER_SNAKE_CASE(providerName)>_API_KEY
 * Settings: webSearchApiKey.<providerName> in settings.json
 */
export function getApiKey(providerName: string): string | undefined {
	const envKey = `PI_WEB_SEARCH_${toUpperSnakeCase(providerName)}_API_KEY`;
	const envVal = process.env[envKey];
	if (envVal) return envVal;
	const settings = readPiSettings();
	return settings.webSearchApiKey?.[providerName];
}

// ---------------------------------------------------------------------------
// Retry-after aware fetch helper
// ---------------------------------------------------------------------------

const MAX_RETRIES = 5;
const BASE_DELAY_MS = 500;
const MAX_BACKOFF_MS = 32_000;

function getRetryDelay(attempt: number, resp: Response): number {
	const retryAfterMs = resp.headers.get("retry-after-ms");
	if (retryAfterMs) {
		const ms = parseFloat(retryAfterMs);
		if (!isNaN(ms)) return ms;
	}

	const retryAfter = resp.headers.get("retry-after");
	if (retryAfter) {
		const seconds = parseFloat(retryAfter);
		if (!isNaN(seconds)) return seconds * 1000;
		// Try parsing as date
		const date = Date.parse(retryAfter);
		if (!isNaN(date)) return Math.max(0, date - Date.now());
	}

	// Exponential backoff with jitter
	const delay = Math.min(BASE_DELAY_MS * Math.pow(2, attempt), MAX_BACKOFF_MS);
	return delay + Math.random() * 0.25 * delay;
}

function isRetryable(status: number): boolean {
	return status === 429 || status === 503 || status >= 500;
}

function sleep(ms: number, signal?: AbortSignal): Promise<void> {
	return new Promise((resolve, reject) => {
		if (signal?.aborted) {
			reject(new Error("aborted"));
			return;
		}
		const timer = setTimeout(resolve, ms);
		signal?.addEventListener(
			"abort",
			() => {
				clearTimeout(timer);
				reject(new Error("aborted"));
			},
			{ once: true },
		);
	});
}

/**
 * Fetch with automatic retry on 429/5xx, respecting retry-after headers.
 */
export async function fetchWithRetry(
	url: string,
	init: RequestInit,
	signal?: AbortSignal,
): Promise<Response> {
	let lastResp: Response | undefined;

	for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
		if (signal?.aborted) throw new Error("aborted");

		const resp = await fetch(url, { ...init, signal });

		if (resp.ok || !isRetryable(resp.status) || attempt === MAX_RETRIES) {
			return resp;
		}

		lastResp = resp;
		const delayMs = getRetryDelay(attempt, resp);
		await sleep(delayMs, signal);
	}

	return lastResp!;
}
