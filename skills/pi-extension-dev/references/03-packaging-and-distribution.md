# 03. Packaging and Distribution

## pi package basics

A pi package can include:
- extensions
- skills
- prompts
- themes

Declare via `package.json`:

```json
{
  "keywords": ["pi-package"],
  "pi": {
    "extensions": ["./extensions"],
    "skills": ["./skills"],
    "prompts": ["./prompts"],
    "themes": ["./themes"]
  }
}
```

### Gallery metadata

Add preview media for the package gallery:

```json
{
  "pi": {
    "extensions": ["./extensions"],
    "video": "https://example.com/demo.mp4",
    "image": "https://example.com/screenshot.png"
  }
}
```

## Install flows

```bash
pi install npm:@scope/pkg
pi install git:github.com/user/repo
pi install https://github.com/user/repo
pi install /absolute/path/to/package
pi install ./relative/path/to/package

pi install -l npm:@scope/pkg   # project-local
pi -e npm:@scope/pkg           # temporary for current run

pi list
pi update
pi remove npm:@scope/pkg       # or: pi uninstall npm:@scope/pkg
```

Startup no longer auto-updates packages. Use `pi update` explicitly.

## Package source types

- **npm:** `npm:pkg` or `npm:@scope/pkg@1.2.3` (version pins skip `pi update`).
- **git:** `git:github.com/user/repo@ref`, `git:git@github.com:user/repo@ref`, or protocol URLs like `https://github.com/user/repo@ref`.
- **local:** absolute or relative paths (files load as single extensions; directories load as packages).

## Dependency guidance

- Core pi runtime libraries should be `peerDependencies` with `"*"`:
  `@mariozechner/pi-ai`, `@mariozechner/pi-agent-core`, `@mariozechner/pi-coding-agent`, `@mariozechner/pi-tui`, `@sinclair/typebox`
- External runtime libs go in `dependencies`.
- To bundle other pi packages, use `dependencies` + `bundledDependencies` and reference via `node_modules/` paths.

## Filtering resources in settings

Use package object form:

```json
{
  "packages": [
    {
      "source": "npm:my-pkg",
      "extensions": ["extensions/*.ts", "!extensions/legacy.ts"],
      "skills": [],
      "prompts": ["prompts/review.md"]
    }
  ]
}
```

## Enable/disable resources

Use `pi config` to enable or disable extensions, skills, prompts, and themes from installed packages and local directories.

## Security note

Extensions execute arbitrary code; skills can instruct arbitrary actions. Only install trusted packages.
