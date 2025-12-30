---
name: Playwright Browser Automation
description: Complete browser automation with Playwright. Auto-detects dev servers, writes clean test scripts to /tmp. Test pages, fill forms, take screenshots, check responsive design, validate UX, test login flows, check links, automate any browser task. Use when user wants to test websites, automate browser interactions, validate web functionality, or perform any browser-based testing.
---

# Playwright Browser Automation

Browser automation skill. Write custom Playwright code for any task and execute via `run.js`.

## Setup

```bash
cd <skill directory> && bun install
```

Uses system Chrome by default (`channel: 'chrome'`). If not found, run `bunx playwright install chromium`.

## Workflow

**1. Detect dev servers** (for localhost testing):

```bash
cd <skill directory> && bun -e "require('./lib/helpers').detectDevServers().then(s => console.log(JSON.stringify(s)))"
```

- 1 server found → use it automatically
- Multiple servers → ask user which one
- No servers → ask for URL

**2. Write script to /tmp** with parameterized URL:

```javascript
// /tmp/playwright-test-example.js
const { chromium } = require('playwright');
const TARGET_URL = 'http://localhost:3001'; // detected or user-provided

(async () => {
  const browser = await chromium.launch({ headless: false, channel: 'chrome' });
  const page = await browser.newPage();
  await page.goto(TARGET_URL);
  // ... automation code ...
  await browser.close();
})();
```

**3. Execute**:

```bash
cd <skill directory> && bun run.js /tmp/playwright-test-example.js
```

## Key Rules

- **Always detect servers first** for localhost testing
- **Write to /tmp** - never to skill directory or user's project
- **Use `headless: false`** unless user requests headless
- **Parameterize URLs** with `TARGET_URL` constant

## Helpers

Optional utilities in `lib/helpers.js`:

```javascript
const helpers = require('./lib/helpers');

await helpers.detectDevServers();           // Find running dev servers
await helpers.safeClick(page, selector);    // Click with retry
await helpers.safeType(page, selector, text); // Type with clear
await helpers.takeScreenshot(page, name);   // Timestamped screenshot
await helpers.handleCookieBanner(page);     // Dismiss cookie popups
await helpers.extractTableData(page, selector); // Get table as JSON
```

## Patterns

See [references/patterns.md](references/patterns.md) for common patterns:

- Basic page test
- Responsive design testing
- Login flow
- Form submission
- Broken links check
- Screenshot with error handling
- Inline execution

## Tips

- Use `slowMo: 100` to make actions visible
- Use `waitForURL`, `waitForSelector` instead of fixed timeouts
- Always use try-catch for robust automation
- Use `console.log()` to track progress

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Playwright not installed | `cd <skill dir> && bun install` |
| Browser doesn't open | Check `headless: false`, ensure display available |
| Element not found | Add `await page.waitForSelector('.element', { timeout: 10000 })` |
