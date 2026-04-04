# Pi Packages Reference (Local)

This reference summarizes `packages/coding-agent/docs/packages.md` for portability.

## What a pi package is

Pi packages bundle extensions, skills, prompts, and themes for reuse via npm/git/local paths.

## Install and manage

```bash
pi install npm:@scope/pkg@1.2.3
pi install git:github.com/user/repo@v1
pi install https://github.com/user/repo
pi install /absolute/path/to/package
pi install ./relative/path/to/package

pi remove npm:@scope/pkg    # or: pi uninstall npm:@scope/pkg
pi list    # show installed packages from settings
pi update  # update all non-pinned packages
```

- Default writes to global settings (`~/.pi/agent/settings.json`).
- Use `-l` to write to project settings (`.pi/settings.json`).
- `pi -e <source>` installs to a temporary directory for the current run only.

Startup no longer auto-updates unpinned packages. Use `pi update` explicitly.
Interactive mode checks for updates in the background and notifies.

## Package sources

- **npm:** `npm:@scope/pkg@1.2.3` or `npm:pkg`
  - Pinned versions are skipped by `pi update`.
  - Global installs go to global npm, project installs go under `.pi/npm/`.
  - Use `npmCommand` in settings to pin npm to a specific wrapper (e.g., `["mise", "exec", "node@20", "--", "npm"]`).
- **git:** `git:github.com/user/repo@ref`, `git:git@github.com:user/repo@ref`, or protocol URLs (`https://`, `ssh://`)
  - SSH/HTTPS both supported; refs pin and skip updates.
  - Cloned to `~/.pi/agent/git/...` or `.pi/git/...`.
  - Runs `npm install` after clone/pull if `package.json` exists.
- **local paths:** file or directory on disk; relative paths resolve against settings file.

## Creating a package

Add a `pi` manifest in `package.json` and the `pi-package` keyword:

```json
{
  "name": "my-package",
  "keywords": ["pi-package"],
  "pi": {
    "extensions": ["./extensions"],
    "skills": ["./skills"],
    "prompts": ["./prompts"],
    "themes": ["./themes"]
  }
}
```

If no `pi` manifest exists, pi auto-discovers:
- `extensions/` (`.ts`/`.js`)
- `skills/` (folders with `SKILL.md`)
- `prompts/` (`.md`)
- `themes/` (`.json`)

### Gallery metadata

The package gallery displays packages tagged with `pi-package`. Add preview media:

```json
{
  "pi": {
    "extensions": ["./extensions"],
    "video": "https://example.com/demo.mp4",
    "image": "https://example.com/screenshot.png"
  }
}
```

- `video`: MP4 only. Autoplays on hover.
- `image`: PNG, JPEG, GIF, or WebP.
- If both set, video takes precedence.

## Dependencies

- Runtime dependencies go in `dependencies`.
- If you import these core packages, list them in `peerDependencies` with `"*"` and do not bundle:
  - `@mariozechner/pi-ai`, `@mariozechner/pi-agent-core`, `@mariozechner/pi-coding-agent`, `@mariozechner/pi-tui`, `@sinclair/typebox`
- To bundle other pi packages, include them in `dependencies` and `bundledDependencies`, then reference resources under `node_modules/` paths in the `pi` manifest.

## Filtering resources (settings)

You can filter package resources in settings using object form:

```json
{
  "packages": [
    {
      "source": "npm:my-package",
      "extensions": ["extensions/*.ts", "!extensions/legacy.ts"],
      "skills": [],
      "prompts": ["prompts/review.md"],
      "themes": ["+themes/legacy.json"]
    }
  ]
}
```

- Omit a key to load all of that type.
- Use `[]` to load none.
- `!pattern` excludes, `+path` forces include, `-path` forces exclude.

## Enable/disable resources

Use `pi config` to enable or disable extensions, skills, prompts, and themes from installed packages and local directories.

## Deduplication

If the same package appears in global and project settings, the project entry wins. Identity is based on source (npm name, git URL without ref, or resolved path).
