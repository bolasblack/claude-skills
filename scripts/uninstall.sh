#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

# Global counters
TOTAL_REMOVED=0
TOTAL_SKIPPED=0

uninstall_from_tool() {
    local tool_root="$1"
    local tool_name="$2"
    local type="$3"
    local name="$4"

    if [[ ! -d "$tool_root" ]]; then
        return 0
    fi

    local target_subdir
    target_subdir=$(get_target_subdir "$tool_name" "$type")
    local target_dir="$tool_root/$target_subdir"

    # Get target paths (sets target_path and managed_by_file)
    local target_path managed_by_file
    get_target_paths "$target_dir" "$type" "$name"

    if [[ ! -e "$target_path" && ! -L "$target_path" ]]; then
        return 0
    fi

    if is_managed_by_us "$target_path" "$managed_by_file"; then
        rm -rf "$target_path"
        [[ "$type" != "skills" ]] && rm -f "$managed_by_file"
        echo "  - $tool_name: Removed"
        TOTAL_REMOVED=$((TOTAL_REMOVED + 1))
    else
        echo "  - $tool_name: Skipped (not managed by us)"
        TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
    fi
}

uninstall_extension() {
    local type="$1"
    local name="$2"

    echo "[$type/$name]"

    # Claude Code
    uninstall_from_tool "$HOME/.claude" "claude" "$type" "$name"

    # Codex (only skills)
    if [[ "$type" == "skills" ]]; then
        uninstall_from_tool "$HOME/.codex" "codex" "$type" "$name"
    fi

    # OpenCode (skills and commands)
    if [[ "$type" == "skills" || "$type" == "commands" ]]; then
        uninstall_from_tool "$HOME/.config/opencode" "opencode" "$type" "$name"
    fi
}

uninstall_all_of_type() {
    local type="$1"
    local main_file
    main_file=$(get_main_file "$type")

    for dir in "$PROJECT_DIR/$type"/*/; do
        if [[ -d "$dir" && -f "$dir/$main_file" ]]; then
            local name
            name=$(basename "$dir")
            uninstall_extension "$type" "$name"
        fi
    done
}

usage() {
    echo "Usage: $0 <TYPE> <NAME...>"
    echo ""
    echo "Uninstall extensions managed by this repository"
    echo ""
    echo "Arguments:"
    echo "  TYPE    Extension type: ALL, skills, commands, or agents"
    echo "  NAME    One or more extension names, or ALL for all of that type"
    echo ""
    echo "Examples:"
    echo "  $0 ALL                          # Uninstall all extensions of all types"
    echo "  $0 skills ALL                   # Uninstall all skills"
    echo "  $0 skills color-master          # Uninstall specific skill"
    echo "  $0 skills skill-1 skill-2       # Uninstall multiple skills"
    exit 1
}

# Main logic
if [[ $# -eq 0 ]]; then
    usage
elif [[ $# -eq 1 ]]; then
    if [[ "$1" == "ALL" ]]; then
        for type in skills commands agents; do
            if [[ -d "$PROJECT_DIR/$type" ]]; then
                uninstall_all_of_type "$type"
            fi
        done
    else
        usage
    fi
elif [[ $# -ge 2 ]]; then
    type="$1"
    shift
    if [[ "$type" != "skills" && "$type" != "commands" && "$type" != "agents" ]]; then
        usage
    fi
    for name in "$@"; do
        if [[ "$name" == "ALL" ]]; then
            uninstall_all_of_type "$type"
        else
            uninstall_extension "$type" "$name"
        fi
    done
else
    usage
fi

echo ""
echo "Done: $TOTAL_REMOVED removed, $TOTAL_SKIPPED skipped"
