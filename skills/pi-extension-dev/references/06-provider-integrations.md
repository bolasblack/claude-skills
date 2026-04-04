# 06. Provider Integrations

Use this reference when adding proxy endpoints, OAuth providers, or custom streaming behavior.

## Registering providers

Use `pi.registerProvider()` to add or override providers, and `pi.unregisterProvider()` to remove them.

Calls during extension factory are queued and applied on runner init.
Calls after that (e.g., from command handlers) take effect immediately without `/reload`.

```ts
pi.registerProvider("my-proxy", {
  baseUrl: "https://proxy.example.com",
  apiKey: "PROXY_API_KEY", // env var name or literal
  api: "openai-responses",
  models: [
    {
      id: "proxy-model",
      name: "Proxy Model",
      reasoning: false,
      input: ["text", "image"],
      cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
      contextWindow: 128000,
      maxTokens: 8192
    }
  ]
});

pi.unregisterProvider("my-proxy");
```

Config options:
- `baseUrl` — API endpoint URL. Required when defining models.
- `apiKey` — API key or env var name. Required when defining models (unless `oauth` provided).
- `api` — API type: `"anthropic-messages"`, `"openai-completions"`, `"openai-responses"`, etc.
- `headers` — Custom headers.
- `authHeader` — If true, adds `Authorization: Bearer` automatically.
- `models` — Array of model definitions. Replaces existing models for this provider.
- `oauth` — OAuth config for `/login` support.
- `streamSimple` — Custom streaming for non-standard APIs.

Notes:
- If you pass `models`, they replace existing models for that provider name.
- Providing only `baseUrl` or `headers` overrides the endpoint without replacing models.

## OAuth support

Register providers with an `oauth` field to integrate with `/login`:

```ts
pi.registerProvider("corp-ai", {
  baseUrl: "https://ai.corp.com/v1",
  api: "openai-responses",
  models: [/* ... */],
  oauth: {
    name: "Corp AI (SSO)",
    async login(callbacks) {
      callbacks.onAuth({ url: "https://sso.corp.com/authorize" });
      const code = await callbacks.onPrompt({ message: "Enter SSO code:" });
      return { refresh: code, access: code, expires: Date.now() + 3600000 };
    },
    async refreshToken(credentials) {
      return credentials;
    },
    getApiKey(credentials) {
      return credentials.access;
    }
  }
});
```

Guidance:
- OAuth credentials persist in `~/.pi/agent/auth.json`.
- Avoid blocking prompts in non-interactive modes; require pre-seeded tokens where possible.

## API key resolution (v0.63.0+)

`ModelRegistry.getApiKey(model)` has been removed. Use `getApiKeyAndHeaders(model)` instead:

```ts
// Before (broken):
const apiKey = await ctx.modelRegistry.getApiKey(model);

// After:
const auth = await ctx.modelRegistry.getApiKeyAndHeaders(model);
if (!auth.ok) throw new Error(auth.error);
// auth.apiKey, auth.headers
```

This is needed because `models.json` auth and header values can resolve dynamically on every request.
Use `getApiKeyForProvider(provider)` only for provider-level key lookup without model headers.

## Custom streaming (`streamSimple`)

Use `streamSimple` for non-standard APIs. Implement streaming with `createAssistantMessageEventStream()` and push:

- `start`
- `text_*` / `thinking_*` / `toolcall_*`
- `done` or `error`

Always populate `usage` and compute cost with `calculateCost`.

Reference implementations:
- `packages/ai/src/providers/*.ts`
- `packages/coding-agent/docs/custom-provider.md`

## Model selection behavior

- Use `model_select` events for UI updates when models change.
- `event.source` is `"set"`, `"cycle"`, or `"restore"`.
- Use `pi.setModel()` to switch; it returns `false` when no API key is available.
- Provider registration applies in all modes (interactive/print/json/rpc).
