#!/bin/bash

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEST_ROOT=$(mktemp -d)
trap 'rm -rf "$TEST_ROOT"' EXIT

mkdir -p "$TEST_ROOT/claude-skills/scripts" \
    "$TEST_ROOT/claude-skills/skills/example" \
    "$TEST_ROOT/claude-skills/agents/example" \
    "$TEST_ROOT/project" \
    "$TEST_ROOT/symlink-project"
cp "$SCRIPT_DIR/install.sh" "$SCRIPT_DIR/common.sh" "$TEST_ROOT/claude-skills/scripts/"
printf '# Example\n' > "$TEST_ROOT/claude-skills/skills/example/SKILL.md"
printf '# Example\n' > "$TEST_ROOT/claude-skills/agents/example/AGENT.md"

"$TEST_ROOT/claude-skills/scripts/install.sh" \
    --mode copy \
    --project "$TEST_ROOT/project" \
    --tools claude \
    skills example >/dev/null

target="$TEST_ROOT/project/.claude/skills/example"
[[ -d "$target" ]]
[[ ! -L "$target" ]]
[[ -f "$target/.managed-by" ]]

"$TEST_ROOT/claude-skills/scripts/install.sh" \
    --mode symlink \
    --project "$TEST_ROOT/symlink-project" \
    --tools claude \
    skills example >/dev/null

target="$TEST_ROOT/symlink-project/.claude/skills/example"
[[ -L "$target" ]]
[[ "$(readlink "$target")" == "../../../claude-skills/skills/example" ]]
[[ "$target" -ef "$TEST_ROOT/claude-skills/skills/example" ]]

"$TEST_ROOT/claude-skills/scripts/install.sh" \
    --mode symlink \
    --project "$TEST_ROOT/symlink-project" \
    --tools claude \
    agents example >/dev/null

target="$TEST_ROOT/symlink-project/.claude/agents/example.md"
[[ -L "$target" ]]
[[ "$(readlink "$target")" == "../../../claude-skills/agents/example/AGENT.md" ]]
[[ "$target" -ef "$TEST_ROOT/claude-skills/agents/example/AGENT.md" ]]

output=$("$TEST_ROOT/claude-skills/scripts/install.sh" \
    --mode copy \
    --project "$TEST_ROOT/symlink-project" \
    --tools claude \
    skills example)

target="$TEST_ROOT/symlink-project/.claude/skills/example"
[[ -d "$target" ]]
[[ ! -L "$target" ]]
[[ -f "$target/.managed-by" ]]
[[ "$output" == *"Updated"* ]]

echo "install tests passed"
