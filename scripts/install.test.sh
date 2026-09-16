#!/bin/bash

set -eu
trap 'echo "FAIL at line $LINENO: $BASH_COMMAND" >&2' ERR

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEST_ROOT=$(mktemp -d)
trap 'rm -rf "$TEST_ROOT"' EXIT

mkdir -p "$TEST_ROOT/claude-skills/scripts" \
    "$TEST_ROOT/claude-skills/skills/example" \
    "$TEST_ROOT/claude-skills/skills/example/references" \
    "$TEST_ROOT/claude-skills/commands/example" \
    "$TEST_ROOT/claude-skills/agents/example" \
    "$TEST_ROOT/claude-skills/pi-extensions" \
    "$TEST_ROOT/project" \
    "$TEST_ROOT/symlink-project"
cp "$SCRIPT_DIR/install.sh" "$SCRIPT_DIR/uninstall.sh" "$SCRIPT_DIR/common.sh" "$TEST_ROOT/claude-skills/scripts/"
printf '# Example\n' > "$TEST_ROOT/claude-skills/skills/example/SKILL.md"
printf '# Reference\n' > "$TEST_ROOT/claude-skills/skills/example/references/guide.md"
printf '# Command\n' > "$TEST_ROOT/claude-skills/commands/example/COMMAND.md"
printf '# Example\n' > "$TEST_ROOT/claude-skills/agents/example/AGENT.md"
printf 'export default function () {}\n' > "$TEST_ROOT/claude-skills/pi-extensions/example.ts"

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

echo "Codex home skills use the shared discovery directory"
env HOME="$TEST_ROOT/codex-home" \
    "$TEST_ROOT/claude-skills/scripts/install.sh" \
    --mode symlink --tools codex skills example >/dev/null

target="$TEST_ROOT/codex-home/.agents/skills/example"
[[ -L "$target" ]]
[[ "$target" -ef "$TEST_ROOT/claude-skills/skills/example" ]]
[[ "$(readlink "$target")" != /* ]]
[[ ! -e "$TEST_ROOT/codex-home/.codex/skills/example" ]]
[[ ! -L "$TEST_ROOT/codex-home/.codex/skills/example" ]]

echo "Detected OpenCode home skills use the shared discovery directory"
mkdir -p "$TEST_ROOT/opencode-home/.config/opencode"
output=$(env HOME="$TEST_ROOT/opencode-home" \
    "$TEST_ROOT/claude-skills/scripts/install.sh" skills example)

target="$TEST_ROOT/opencode-home/.agents/skills/example"
[[ -d "$target" && ! -L "$target" ]]
cmp "$target/SKILL.md" "$TEST_ROOT/claude-skills/skills/example/SKILL.md"
[[ ! -e "$TEST_ROOT/opencode-home/.config/opencode/skills/example" ]]
[[ "$output" == *"1 installed, 0 updated, 0 skipped"* ]]

echo "Pi project skills use the shared discovery directory"
mkdir -p "$TEST_ROOT/pi-project"
"$TEST_ROOT/claude-skills/scripts/install.sh" \
    --project "$TEST_ROOT/pi-project" --tools pi skills example >/dev/null

target="$TEST_ROOT/pi-project/.agents/skills/example"
[[ -d "$target" && ! -L "$target" ]]
cmp "$target/SKILL.md" "$TEST_ROOT/claude-skills/skills/example/SKILL.md"
[[ ! -e "$TEST_ROOT/pi-project/.pi/skills/example" ]]

echo "Reinstall consolidates managed Codex skills into the shared directory"
mkdir -p "$TEST_ROOT/consolidate-home/.codex/skills/example"
printf '# Installed copy\n' > "$TEST_ROOT/consolidate-home/.codex/skills/example/SKILL.md"
printf 'bolasblack/claude-skills\n' > "$TEST_ROOT/consolidate-home/.codex/skills/example/.managed-by"
env HOME="$TEST_ROOT/consolidate-home" \
    "$TEST_ROOT/claude-skills/scripts/install.sh" --tools codex skills example >/dev/null

target="$TEST_ROOT/consolidate-home/.agents/skills/example"
cmp "$target/SKILL.md" "$TEST_ROOT/claude-skills/skills/example/SKILL.md"
[[ ! -e "$TEST_ROOT/consolidate-home/.codex/skills/example" ]]
[[ ! -L "$TEST_ROOT/consolidate-home/.codex/skills/example" ]]

echo "Aliased skill directories preserve the shared installation"
mkdir -p "$TEST_ROOT/alias-home/.agents/skills" "$TEST_ROOT/alias-home/.codex"
ln -s ../.agents/skills "$TEST_ROOT/alias-home/.codex/skills"
env HOME="$TEST_ROOT/alias-home" \
    "$TEST_ROOT/claude-skills/scripts/install.sh" --tools codex skills example >/dev/null

cmp "$TEST_ROOT/alias-home/.agents/skills/example/SKILL.md" \
    "$TEST_ROOT/claude-skills/skills/example/SKILL.md"
[[ -L "$TEST_ROOT/alias-home/.codex/skills" ]]

echo "Shared skill symlinks resolve through aliased parent directories"
mkdir -p "$TEST_ROOT/linked-parent-home/.pi/agent/skills" "$TEST_ROOT/linked-parent-home/.agents"
ln -s ../.pi/agent/skills "$TEST_ROOT/linked-parent-home/.agents/skills"
env HOME="$TEST_ROOT/linked-parent-home" \
    "$TEST_ROOT/claude-skills/scripts/install.sh" --mode symlink --tools pi skills example >/dev/null

target="$TEST_ROOT/linked-parent-home/.agents/skills/example"
[[ -L "$target" && "$target" -ef "$TEST_ROOT/claude-skills/skills/example" ]]
[[ "$(readlink "$target")" != /* ]]
[[ -L "$TEST_ROOT/linked-parent-home/.agents/skills" ]]
output=$(env HOME="$TEST_ROOT/linked-parent-home" \
    "$TEST_ROOT/claude-skills/scripts/install.sh" --mode symlink --tools pi skills example)
[[ "$output" == *"0 installed, 1 updated, 0 skipped"* ]]
[[ "$target" -ef "$TEST_ROOT/claude-skills/skills/example" ]]
output=$(env HOME="$TEST_ROOT/linked-parent-home" \
    "$TEST_ROOT/claude-skills/scripts/uninstall.sh" --tools pi skills example)
[[ "$output" == *"1 removed, 0 skipped"* ]]
[[ ! -e "$target" && ! -L "$target" ]]
[[ -L "$TEST_ROOT/linked-parent-home/.agents/skills" ]]

echo "Uninstall removes shared and tool-specific managed skills"
env HOME="$TEST_ROOT/uninstall-home" \
    "$TEST_ROOT/claude-skills/scripts/install.sh" --tools agents skills example >/dev/null
for skill_dir in .codex/skills .config/opencode/skills .pi/agent/skills; do
    target="$TEST_ROOT/uninstall-home/$skill_dir/example"
    mkdir -p "$target"
    printf '# Installed copy\n' > "$target/SKILL.md"
    printf 'c4605/claude-skills\n' > "$target/.managed-by"
done
output=$(env HOME="$TEST_ROOT/uninstall-home" \
    "$TEST_ROOT/claude-skills/scripts/uninstall.sh" \
    --tools agents,codex,opencode,pi skills example)

for skill_dir in .agents/skills .codex/skills .config/opencode/skills .pi/agent/skills; do
    [[ ! -e "$TEST_ROOT/uninstall-home/$skill_dir/example" ]]
    [[ ! -L "$TEST_ROOT/uninstall-home/$skill_dir/example" ]]
done
[[ "$output" == *"4 removed, 0 skipped"* ]]

echo "Reinstall preserves and reports tool-specific skills owned elsewhere"
mkdir -p "$TEST_ROOT/foreign-home/.codex/skills/example" \
    "$TEST_ROOT/foreign-home/.config/opencode/skills" \
    "$TEST_ROOT/foreign-home/.pi/agent/skills/example" \
    "$TEST_ROOT/foreign-skill"
printf '# User skill\n' > "$TEST_ROOT/foreign-home/.codex/skills/example/SKILL.md"
printf 'another/repository\n' > "$TEST_ROOT/foreign-home/.codex/skills/example/.managed-by"
printf '# User skill\n' > "$TEST_ROOT/foreign-home/.pi/agent/skills/example/SKILL.md"
printf '# User skill\n' > "$TEST_ROOT/foreign-skill/SKILL.md"
ln -s "$TEST_ROOT/foreign-skill" "$TEST_ROOT/foreign-home/.config/opencode/skills/example"
output=$(env HOME="$TEST_ROOT/foreign-home" \
    "$TEST_ROOT/claude-skills/scripts/install.sh" --tools codex,opencode,pi skills example)

for skill_dir in .codex/skills .config/opencode/skills .pi/agent/skills; do
    [[ "$(cat "$TEST_ROOT/foreign-home/$skill_dir/example/SKILL.md")" == '# User skill' ]]
done
[[ -L "$TEST_ROOT/foreign-home/.config/opencode/skills/example" ]]
cmp "$TEST_ROOT/foreign-home/.agents/skills/example/SKILL.md" \
    "$TEST_ROOT/claude-skills/skills/example/SKILL.md"
[[ "$output" == *"WARNING"* && "$output" == *"3 conflicts"* ]]
output=$(env HOME="$TEST_ROOT/foreign-home" \
    "$TEST_ROOT/claude-skills/scripts/uninstall.sh" --tools codex,opencode,pi skills example)
[[ "$output" == *"1 removed, 3 skipped"* ]]
for skill_dir in .codex/skills .config/opencode/skills .pi/agent/skills; do
    [[ "$(cat "$TEST_ROOT/foreign-home/$skill_dir/example/SKILL.md")" == '# User skill' ]]
done
[[ -L "$TEST_ROOT/foreign-home/.config/opencode/skills/example" ]]

echo "A conflict at the shared destination preserves existing managed installations"
mkdir -p "$TEST_ROOT/conflict-home/.agents/skills/example" "$TEST_ROOT/conflict-home/.codex/skills/example"
printf '# User skill\n' > "$TEST_ROOT/conflict-home/.agents/skills/example/SKILL.md"
printf '# Installed copy\n' > "$TEST_ROOT/conflict-home/.codex/skills/example/SKILL.md"
printf 'bolasblack/claude-skills\n' > "$TEST_ROOT/conflict-home/.codex/skills/example/.managed-by"
output=$(env HOME="$TEST_ROOT/conflict-home" \
    "$TEST_ROOT/claude-skills/scripts/install.sh" --tools codex skills example)
[[ "$output" == *"0 installed, 0 updated, 1 skipped"* ]]
[[ "$(cat "$TEST_ROOT/conflict-home/.agents/skills/example/SKILL.md")" == '# User skill' ]]
[[ "$(cat "$TEST_ROOT/conflict-home/.codex/skills/example/SKILL.md")" == '# Installed copy' ]]
output=$(env HOME="$TEST_ROOT/conflict-home" \
    "$TEST_ROOT/claude-skills/scripts/uninstall.sh" --tools codex skills example)
[[ "$output" == *"1 removed, 1 skipped"* ]]
[[ "$(cat "$TEST_ROOT/conflict-home/.agents/skills/example/SKILL.md")" == '# User skill' ]]
[[ ! -e "$TEST_ROOT/conflict-home/.codex/skills/example" ]]

echo "Failed shared installation preserves the existing managed skill"
mkdir -p "$TEST_ROOT/failed-home/.codex/skills/example"
printf 'User file blocking the destination\n' > "$TEST_ROOT/failed-home/.agents"
printf '# Installed copy\n' > "$TEST_ROOT/failed-home/.codex/skills/example/SKILL.md"
printf 'bolasblack/claude-skills\n' > "$TEST_ROOT/failed-home/.codex/skills/example/.managed-by"
if env HOME="$TEST_ROOT/failed-home" "$TEST_ROOT/claude-skills/scripts/install.sh" \
    --tools codex skills example >"$TEST_ROOT/failed-install.log" 2>&1; then
    echo "Expected the blocked installation to fail" >&2
    exit 1
fi
[[ "$(cat "$TEST_ROOT/failed-home/.codex/skills/example/SKILL.md")" == '# Installed copy' ]]
[[ "$(cat "$TEST_ROOT/failed-home/.agents")" == 'User file blocking the destination' ]]

echo "Explicit tool selection limits cleanup to the selected tools"
for skill_dir in .codex/skills .config/opencode/skills; do
    target="$TEST_ROOT/selected-home/$skill_dir/example"
    mkdir -p "$target"
    printf '# Installed copy\n' > "$target/SKILL.md"
    printf 'bolasblack/claude-skills\n' > "$target/.managed-by"
done
env HOME="$TEST_ROOT/selected-home" \
    "$TEST_ROOT/claude-skills/scripts/install.sh" --tools codex skills example >/dev/null
[[ ! -e "$TEST_ROOT/selected-home/.codex/skills/example" ]]
[[ "$(cat "$TEST_ROOT/selected-home/.config/opencode/skills/example/SKILL.md")" == '# Installed copy' ]]
env HOME="$TEST_ROOT/selected-home" \
    "$TEST_ROOT/claude-skills/scripts/uninstall.sh" --tools codex skills example >/dev/null
[[ ! -e "$TEST_ROOT/selected-home/.agents/skills/example" ]]
[[ "$(cat "$TEST_ROOT/selected-home/.config/opencode/skills/example/SKILL.md")" == '# Installed copy' ]]

echo "Shared skills install once, update, and uninstall in both scopes and modes"
for scope in home project; do
    for mode in copy symlink; do
        for tools in agents,codex,opencode,pi,claude pi,opencode,codex,agents,claude; do
            case_root="$TEST_ROOT/shared-$scope-$mode-$tools"
            install_home="$case_root/home"
            base="$install_home"
            args=(--tools "$tools")
            if [[ "$scope" == project ]]; then
                base="$case_root/project"
                args+=(--project "$base")
            fi
            mkdir -p "$base"
            output=$(env HOME="$install_home" \
                "$TEST_ROOT/claude-skills/scripts/install.sh" --mode "$mode" "${args[@]}" skills example)
            [[ "$output" == *"2 installed, 0 updated, 0 skipped"* ]]

            for skill_dir in .agents/skills .claude/skills; do
                target="$base/$skill_dir/example"
                cmp "$target/SKILL.md" "$TEST_ROOT/claude-skills/skills/example/SKILL.md"
                cmp "$target/references/guide.md" "$TEST_ROOT/claude-skills/skills/example/references/guide.md"
                if [[ "$mode" == symlink ]]; then
                    [[ -L "$target" && "$(readlink "$target")" != /* ]]
                else
                    [[ ! -L "$target" && -f "$target/.managed-by" ]]
                fi
            done
            for skill_dir in .codex/skills .config/opencode/skills .opencode/skills .pi/agent/skills .pi/skills; do
                [[ ! -e "$base/$skill_dir/example" && ! -L "$base/$skill_dir/example" ]]
            done

            compat_dirs=(.codex/skills .config/opencode/skills .pi/agent/skills)
            if [[ "$scope" == project ]]; then
                compat_dirs=(.codex/skills .opencode/skills .pi/skills)
            fi
            for skill_dir in "${compat_dirs[@]}"; do
                mkdir -p "$base/$skill_dir/.system"
                printf '# Keep\n' > "$base/$skill_dir/.system/keep.md"
                ln -s "$TEST_ROOT/claude-skills/skills/example" "$base/$skill_dir/example"
            done
            output=$(env HOME="$install_home" \
                "$TEST_ROOT/claude-skills/scripts/install.sh" --mode "$mode" "${args[@]}" skills example)
            [[ "$output" == *"0 installed, 2 updated, 0 skipped"* ]]
            for skill_dir in "${compat_dirs[@]}"; do
                [[ ! -e "$base/$skill_dir/example" && ! -L "$base/$skill_dir/example" ]]
                [[ "$(cat "$base/$skill_dir/.system/keep.md")" == '# Keep' ]]
            done
            output=$(env HOME="$install_home" \
                "$TEST_ROOT/claude-skills/scripts/uninstall.sh" "${args[@]}" skills example)
            [[ "$output" == *"2 removed, 0 skipped"* ]]
            for skill_dir in .agents/skills .claude/skills; do
                [[ ! -e "$base/$skill_dir/example" && ! -L "$base/$skill_dir/example" ]]
            done
            [[ -f "$TEST_ROOT/claude-skills/skills/example/SKILL.md" ]]
        done
    done
done

echo "Auto-detection recognizes each tool without requiring a shared directory"
for scope in home project; do
    for tool_dir in .agents .claude .codex .opencode .pi; do
        case_root="$TEST_ROOT/detected-$scope-$tool_dir"
        install_home="$case_root/home"
        base="$install_home"
        detect_dir="$tool_dir"
        args=(skills example)
        if [[ "$scope" == project ]]; then
            base="$case_root/project"
            args=(--project "$base" "${args[@]}")
        else
            case "$tool_dir" in
                .opencode) detect_dir=.config/opencode ;;
                .pi) detect_dir=.pi/agent ;;
            esac
        fi
        mkdir -p "$base/$detect_dir"
        output=$(env HOME="$install_home" "$TEST_ROOT/claude-skills/scripts/install.sh" "${args[@]}")
        [[ "$output" == *"1 installed, 0 updated, 0 skipped"* ]]
        skill_dir=.agents/skills
        [[ "$tool_dir" == .claude ]] && skill_dir=.claude/skills
        cmp "$base/$skill_dir/example/SKILL.md" "$TEST_ROOT/claude-skills/skills/example/SKILL.md"
        output=$(env HOME="$install_home" "$TEST_ROOT/claude-skills/scripts/uninstall.sh" "${args[@]}")
        [[ "$output" == *"1 removed, 0 skipped"* ]]
        [[ ! -e "$base/$skill_dir/example" ]]
    done
done

echo "Commands, agents, and pi extensions keep their tool-specific directories"
for scope in home project; do
    case_root="$TEST_ROOT/other-types-$scope"
    install_home="$case_root/home"
    base="$install_home"
    opencode_dir=.config/opencode
    pi_dir=.pi/agent
    args=(--tools agents,claude,codex,opencode,pi)
    if [[ "$scope" == project ]]; then
        base="$case_root/project"
        opencode_dir=.opencode
        pi_dir=.pi
        args+=(--project "$base")
    fi
    mkdir -p "$base"
    env HOME="$install_home" "$TEST_ROOT/claude-skills/scripts/install.sh" "${args[@]}" commands example >/dev/null
    env HOME="$install_home" "$TEST_ROOT/claude-skills/scripts/install.sh" "${args[@]}" agents example >/dev/null
    env HOME="$install_home" "$TEST_ROOT/claude-skills/scripts/install.sh" "${args[@]}" pi-extensions example.ts >/dev/null
    for path in .claude/commands/example.md "$opencode_dir/command/example.md"; do
        cmp "$base/$path" "$TEST_ROOT/claude-skills/commands/example/COMMAND.md"
    done
    for path in .claude/agents/example.md "$opencode_dir/agent/example.md" "$pi_dir/agents/example.md"; do
        cmp "$base/$path" "$TEST_ROOT/claude-skills/agents/example/AGENT.md"
    done
    cmp "$base/$pi_dir/extensions/example.ts" "$TEST_ROOT/claude-skills/pi-extensions/example.ts"
    [[ ! -e "$base/.agents" && ! -e "$base/.codex" ]]
done

echo "install tests passed"
