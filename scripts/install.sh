#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

# Global counters
TOTAL_INSTALLED=0
TOTAL_UPDATED=0
TOTAL_SKIPPED=0
TOTAL_WARNINGS=0

usage() {
    echo "Usage: $0 <TYPE> <NAME...>"
    echo ""
    echo "Install extensions by copying to Claude Code, Codex, and OpenCode"
    echo ""
    echo "Arguments:"
    echo "  TYPE    Extension type: ALL, skills, commands, or agents"
    echo "  NAME    One or more extension names, or ALL for all of that type"
    echo ""
    echo "Examples:"
    echo "  $0 ALL                          # Install all extensions of all types"
    echo "  $0 skills ALL                   # Install all skills"
    echo "  $0 skills color-master          # Install specific skill"
    echo "  $0 skills skill-1 skill-2       # Install multiple skills"
    echo "  $0 commands ALL                 # Install all commands"
    echo "  $0 agents code-reviewer         # Install specific agent"
    echo ""
    echo "Available extensions:"
    echo ""
    echo "Skills:"
    for dir in "$PROJECT_DIR"/skills/*/; do
        if [[ -d "$dir" && -f "$dir/SKILL.md" ]]; then
            echo "  $(basename "$dir")"
        fi
    done
    echo ""
    echo "Commands:"
    for dir in "$PROJECT_DIR"/commands/*/; do
        if [[ -d "$dir" && -f "$dir/COMMAND.md" ]]; then
            echo "  $(basename "$dir")"
        fi
    done
    echo ""
    echo "Agents:"
    for dir in "$PROJECT_DIR"/agents/*/; do
        if [[ -d "$dir" && -f "$dir/AGENT.md" ]]; then
            echo "  $(basename "$dir")"
        fi
    done
    exit 1
}

install_to_tool() {
    local tool_root="$1"
    local tool_name="$2"
    local type="$3"
    local name="$4"
    local source_path="$5"

    # Check if tool directory exists
    if [[ ! -d "$tool_root" ]]; then
        return 0
    fi

    local target_subdir
    target_subdir=$(get_target_subdir "$tool_name" "$type")
    local target_dir="$tool_root/$target_subdir"
    mkdir -p "$target_dir"

    # Get target paths (sets target_path and managed_by_file)
    local target_path managed_by_file
    get_target_paths "$target_dir" "$type" "$name"

    # Check if target already exists
    local is_update=false
    if [[ -e "$target_path" || -L "$target_path" ]]; then
        if is_managed_by_us "$target_path" "$managed_by_file"; then
            # Remove existing installation for update
            rm -rf "$target_path"
            [[ "$type" != "skills" ]] && rm -f "$managed_by_file"
            is_update=true
        else
            echo "  - $tool_name: WARNING - Skipped (already exists, not managed by us)"
            TOTAL_WARNINGS=$((TOTAL_WARNINGS + 1))
            TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
            return 0
        fi
    fi

    # Install
    if [[ "$type" == "skills" ]]; then
        # Copy entire directory
        cp -r "$source_path" "$target_path"
        # Add .managed-by file inside the skill directory
        echo "$REPO_NAME" > "$target_path/.managed-by"
    else
        # Copy main file only
        local main_file
        main_file=$(get_main_file "$type")
        cp "$source_path/$main_file" "$target_path"
        # Add .managed-by file as hidden file alongside the target
        echo "$REPO_NAME" > "$managed_by_file"
    fi

    if [[ "$is_update" == true ]]; then
        echo "  - $tool_name: Updated"
        TOTAL_UPDATED=$((TOTAL_UPDATED + 1))
    else
        echo "  - $tool_name: Installed"
        TOTAL_INSTALLED=$((TOTAL_INSTALLED + 1))
    fi
}

install_extension() {
    local type="$1"
    local name="$2"
    local source_path="$PROJECT_DIR/$type/$name"
    local main_file
    main_file=$(get_main_file "$type")

    if [[ ! -d "$source_path" ]]; then
        echo "Error: Extension directory not found: $source_path"
        return 1
    fi

    if [[ ! -f "$source_path/$main_file" ]]; then
        echo "Error: Not a valid $type (missing $main_file): $source_path"
        return 1
    fi

    echo "[$type/$name]"

    # Claude Code: supports skills, commands, agents
    install_to_tool "$HOME/.claude" "claude" "$type" "$name" "$source_path"

    # Codex: only supports skills
    if [[ "$type" == "skills" ]]; then
        install_to_tool "$HOME/.codex" "codex" "$type" "$name" "$source_path"
    fi

    # OpenCode: supports skills, commands (as command)
    if [[ "$type" == "skills" || "$type" == "commands" ]]; then
        install_to_tool "$HOME/.config/opencode" "opencode" "$type" "$name" "$source_path"
    fi

    return 0
}

install_all_of_type() {
    local type="$1"
    local main_file
    main_file=$(get_main_file "$type")

    for dir in "$PROJECT_DIR/$type"/*/; do
        if [[ -d "$dir" && -f "$dir/$main_file" ]]; then
            local name
            name=$(basename "$dir")
            install_extension "$type" "$name"
        fi
    done
}

# Main logic
if [[ $# -eq 0 ]]; then
    usage
elif [[ $# -eq 1 ]]; then
    if [[ "$1" == "ALL" ]]; then
        # Install everything
        for type in skills commands agents; do
            if [[ -d "$PROJECT_DIR/$type" ]]; then
                install_all_of_type "$type"
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
            install_all_of_type "$type"
        else
            install_extension "$type" "$name"
        fi
    done
else
    usage
fi

echo ""
summary="Done: $TOTAL_INSTALLED installed, $TOTAL_UPDATED updated, $TOTAL_SKIPPED skipped"
if [[ $TOTAL_WARNINGS -gt 0 ]]; then
    summary="$summary ($TOTAL_WARNINGS conflicts)"
fi
echo "$summary"
