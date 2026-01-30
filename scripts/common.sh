#!/bin/bash

# Common utilities for install/uninstall scripts

# Repository name to write to .managed-by file
REPO_NAME="bolasblack/claude-skills"

# Repository names that we manage (may change in the future)
MANAGED_REPOS=(
    "bolasblack/claude-skills"
    "c4605/claude-skills"
)

# Get the main file name for a given extension type
get_main_file() {
    local type="$1"
    case "$type" in
        skills) echo "SKILL.md" ;;
        commands) echo "COMMAND.md" ;;
        agents) echo "AGENT.md" ;;
        *) echo "" ;;
    esac
}

# Check if a .managed-by file indicates we own this extension
is_managed_by_file() {
    local managed_by_file="$1"
    if [[ ! -f "$managed_by_file" ]]; then
        return 1
    fi
    local repo_name
    repo_name=$(cat "$managed_by_file" 2>/dev/null || echo "")
    for managed_repo in "${MANAGED_REPOS[@]}"; do
        if [[ "$repo_name" == "$managed_repo" ]]; then
            return 0
        fi
    done
    return 1
}

# Check if a symlink points to our project directory
# Requires PROJECT_DIR to be set by the calling script
is_our_symlink() {
    local target_path="$1"
    if [[ ! -L "$target_path" ]]; then
        return 1
    fi
    local link_target
    link_target=$(readlink "$target_path" 2>/dev/null || echo "")
    # Check if symlink points to our project directory
    if [[ "$link_target" == "$PROJECT_DIR"* ]]; then
        return 0
    fi
    return 1
}

# Check if an extension is managed by us (either by .managed-by file or symlink)
# Requires PROJECT_DIR to be set by the calling script
is_managed_by_us() {
    local target_path="$1"
    local managed_by_file="$2"

    # Check .managed-by file first (new style)
    if is_managed_by_file "$managed_by_file"; then
        return 0
    fi

    # Check if it's a symlink pointing to our project (old style)
    if is_our_symlink "$target_path"; then
        return 0
    fi

    return 1
}

# Get target subdirectory name for a tool
# OpenCode uses singular form for commands and agents
get_target_subdir() {
    local tool_name="$1"
    local type="$2"
    local target_subdir="$type"
    if [[ "$tool_name" == "opencode" ]]; then
        case "$type" in
            commands) target_subdir="command" ;;
            agents) target_subdir="agent" ;;
        esac
    fi
    echo "$target_subdir"
}

# Get target path and managed-by file path for an extension
# Sets: target_path, managed_by_file
get_target_paths() {
    local target_dir="$1"
    local type="$2"
    local name="$3"

    if [[ "$type" == "skills" ]]; then
        target_path="$target_dir/$name"
        managed_by_file="$target_path/.managed-by"
    else
        target_path="$target_dir/${name}.md"
        managed_by_file="$target_dir/.${name}.managed-by"
    fi
}
