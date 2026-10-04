#!/usr/bin/env bash

set -eu
trap 'echo "FAIL at line $LINENO: $BASH_COMMAND" >&2' ERR

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEST_ROOT=$(mktemp -d)
trap 'rm -rf "$TEST_ROOT"' EXIT
PROJECT_DIR="$TEST_ROOT/project with spaces"
mkdir -p "$PROJECT_DIR"

check_setup() {
    python3 "$SCRIPT_DIR/check-setup.py" "$@"
}

expect_not_ready() {
    local output status=0
    output=$(check_setup "$PROJECT_DIR" 2>&1) || status=$?
    if [ "$status" -ne 1 ] || [[ "$output" != *"$1"* ]]; then
        printf 'Expected not ready (%s), got exit %s: %s\n' "$1" "$status" "$output" >&2
        exit 1
    fi
}

run_hooks() {
    local hook
    while IFS= read -r hook; do
        CLAUDE_PROJECT_DIR="$PROJECT_DIR" PYTHONDONTWRITEBYTECODE=1 bash -c "$hook" </dev/null
    done < <(sed -n "s/^[[:space:]]*command: '\(.*\)'/\1/p" "$SKILL_DIR/SKILL.md")
}

# A project without setup must fail without creating .agents.
expect_not_ready '.agents/config.json'
run_hooks
[ ! -e "$PROJECT_DIR/.agents" ]

# Shared agent directories do not establish AGD setup.
mkdir -p "$PROJECT_DIR/.agents/skills/example"
expect_not_ready '.agents/config.json'
run_hooks
[ ! -e "$PROJECT_DIR/.agents/config.json" ]

# Check the exact target even when an initialized project is available in the environment.
CLAUDE_PROJECT_DIR="$PROJECT_DIR" CLAUDE_SKILL_DIR="$SKILL_DIR" PYTHONDONTWRITEBYTECODE=1 \
    bash "$SCRIPT_DIR/init.sh" >/dev/null
check_setup "$PROJECT_DIR"
mkdir "$PROJECT_DIR/nested"
status=0
CLAUDE_PROJECT_DIR="$PROJECT_DIR" check_setup "$PROJECT_DIR/nested" >/dev/null 2>&1 || status=$?
[ "$status" -eq 1 ]
[ ! -e "$PROJECT_DIR/nested/.agents" ]

# Usage mistakes cannot silently select the current directory.
for argument in missing empty extra; do
    status=0
    case "$argument" in
        missing) check_setup >/dev/null 2>&1 || status=$? ;;
        empty) check_setup '' >/dev/null 2>&1 || status=$? ;;
        extra) check_setup "$PROJECT_DIR" extra >/dev/null 2>&1 || status=$? ;;
    esac
    [ "$status" -eq 2 ]
done

# Partial installs fail for each missing runtime prerequisite.
for item in decisions scripts config.json scripts/validate-agds.py scripts/generate-index.py scripts/utils.py scripts/simple_yaml.py; do
    mv "$PROJECT_DIR/.agents/$item" "$TEST_ROOT/removed"
    expect_not_ready ".agents/$item"
    mv "$TEST_ROOT/removed" "$PROJECT_DIR/.agents/$item"
done

for script in validate-agds.py generate-index.py; do
    chmod -x "$PROJECT_DIR/.agents/scripts/$script"
    expect_not_ready 'not executable'
    chmod +x "$PROJECT_DIR/.agents/scripts/$script"
done

cp "$PROJECT_DIR/.agents/config.json" "$TEST_ROOT/config.json"
for config in '{' 'null' '[]' '{}' '{"tags": "core"}' '{"tags": [1]}'; do
    printf '%s\n' "$config" > "$PROJECT_DIR/.agents/config.json"
    expect_not_ready '.agents/config.json'
done
cp "$TEST_ROOT/config.json" "$PROJECT_DIR/.agents/config.json"

# Generated indexes are not setup markers; custom scripts and update opt-outs are valid.
rm "$PROJECT_DIR/.agents/INDEX-TAGS.md" "$PROJECT_DIR/.agents/INDEX-AGD-RELATIONS.md"
printf '%s\n' '{"tags": [], "disableAutoUpdateScripts": true, "postValidateAgdsScripts": ["hooks/local.sh"], "postGenerateIndexScripts": ["hooks/local.sh"]}' \
    > "$PROJECT_DIR/.agents/config.json"
mkdir "$PROJECT_DIR/.agents/hooks"
printf '#!/usr/bin/env bash\ntouch "$1/check-executed-a-hook"\n' > "$PROJECT_DIR/.agents/hooks/local.sh"
chmod +x "$PROJECT_DIR/.agents/hooks/local.sh"

# Checking ready and invalid projects preserves all files and never runs configured hooks.
cp -R "$PROJECT_DIR" "$TEST_ROOT/before"
check_setup "$PROJECT_DIR"
diff -r "$TEST_ROOT/before" "$PROJECT_DIR"

# Older initialized projects can pass before sync has installed the hook's checker.
mv "$PROJECT_DIR/.agents/scripts/check-setup.py" "$TEST_ROOT/check-setup.py"
check_setup "$PROJECT_DIR"
run_hooks
[ ! -e "$PROJECT_DIR/.agents/INDEX-TAGS.md" ]
[ ! -e "$PROJECT_DIR/check-executed-a-hook" ]
mv "$TEST_ROOT/check-setup.py" "$PROJECT_DIR/.agents/scripts/check-setup.py"

printf 'invalid json\n' > "$PROJECT_DIR/.agents/config.json"
printf 'invalid json\n' > "$TEST_ROOT/before/.agents/config.json"
expect_not_ready '.agents/config.json'
diff -r "$TEST_ROOT/before" "$PROJECT_DIR"

# Automatic hooks must also stay inert when setup is invalid.
run_hooks
diff -r "$TEST_ROOT/before" "$PROJECT_DIR"

# Once setup passes, the same hook commands still validate and generate indexes.
cp "$TEST_ROOT/config.json" "$PROJECT_DIR/.agents/config.json"
run_hooks
[ -f "$PROJECT_DIR/.agents/INDEX-TAGS.md" ]
[ -f "$PROJECT_DIR/.agents/INDEX-AGD-RELATIONS.md" ]
[ ! -e "$PROJECT_DIR/check-executed-a-hook" ]

# Agents without hooks can use the documented validation command.
rm "$PROJECT_DIR/.agents/INDEX-TAGS.md" "$PROJECT_DIR/.agents/INDEX-AGD-RELATIONS.md"
check_setup "$PROJECT_DIR"
PYTHONDONTWRITEBYTECODE=1 python3 "$PROJECT_DIR/.agents/scripts/validate-agds.py" "$PROJECT_DIR" </dev/null
[ -f "$PROJECT_DIR/.agents/INDEX-TAGS.md" ]
[ -f "$PROJECT_DIR/.agents/INDEX-AGD-RELATIONS.md" ]

echo 'Setup check tests passed.'
