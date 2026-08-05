#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

# Global counters
TOTAL_REMOVED=0
TOTAL_SKIPPED=0

# Base directory for uninstallation (default: $HOME, override with --project <dir>)
BASE_DIR="$HOME"

get_pi_extensions_dir() {
    if [[ -d "$PROJECT_DIR/pi-extensions/extensions" ]]; then
        echo "$PROJECT_DIR/pi-extensions/extensions"
    else
        echo "$PROJECT_DIR/pi-extensions"
    fi
}

uninstall_from_target() {
    local tool_name="$1"
    local target_dir="$2"
    local type="$3"
    local name="$4"
    local source_path="${5:-}"

    local target_path managed_by_file
    if [[ "$type" == "pi-extensions" ]]; then
        target_path="$target_dir/$name"
        if [[ -d "$source_path" ]]; then
            managed_by_file="$target_path/.managed-by"
        else
            managed_by_file="$target_dir/.${name}.managed-by"
        fi
    else
        get_target_paths "$target_dir" "$type" "$name"
    fi

    if [[ ! -e "$target_path" && ! -L "$target_path" ]]; then
        return 0
    fi

    if is_managed_by_us "$target_path" "$managed_by_file"; then
        rm -rf "$target_path"
        [[ "$type" != "skills" && -f "$managed_by_file" ]] && rm -f "$managed_by_file"
        echo "  - $tool_name: Removed"
        TOTAL_REMOVED=$((TOTAL_REMOVED + 1))
    else
        echo "  - $tool_name: Skipped (not managed by us)"
        TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
    fi
}

uninstall_from_source() {
    local type="$1"
    local name="$2"
    local source_path="${3:-}"

    resolve_targets "$type"
    if [[ ${#RESOLVED_TARGETS[@]} -eq 0 ]]; then
        return 0
    fi

    echo "[$type/$name]"

    local resolved_target tool_name target_dir
    for resolved_target in "${RESOLVED_TARGETS[@]}"; do
        tool_name="${resolved_target%%|*}"
        target_dir="${resolved_target#*|}"
        uninstall_from_target "$tool_name" "$target_dir" "$type" "$name" "$source_path"
    done
}

uninstall_extension() {
    local type="$1"
    local name="$2"

    uninstall_from_source "$type" "$name"
}

uninstall_pi_extension() {
    local name="$1"
    local pi_extensions_dir
    pi_extensions_dir=$(get_pi_extensions_dir)
    local source_path="$pi_extensions_dir/$name"

    if [[ ! -e "$source_path" ]]; then
        echo "Error: Pi extension not found: $source_path"
        return 1
    fi

    uninstall_from_source "pi-extensions" "$name" "$source_path"
}

uninstall_all_of_type() {
    local type="$1"

    if [[ "$type" == "pi-extensions" ]]; then
        local pi_extensions_dir
        pi_extensions_dir=$(get_pi_extensions_dir)
        for path in "$pi_extensions_dir"/*; do
            if [[ -e "$path" ]]; then
                local name
                name=$(basename "$path")
                uninstall_pi_extension "$name"
            fi
        done
        return 0
    fi

    local main_file
    main_file=$(get_main_file "$type")

    # ALL uninstalls cover private extensions (private/<type>/) too.
    local root
    for root in "$PROJECT_DIR/$type" "$PROJECT_DIR/private/$type"; do
        for dir in "$root"/*/; do
            if [[ -d "$dir" && -f "$dir/$main_file" ]]; then
                local name
                name=$(basename "$dir")
                uninstall_extension "$type" "$name"
            fi
        done
    done
}

usage() {
    echo "Usage: $0 [--project <dir>] [--tools <tools>] <TYPE> <NAME...>"
    echo ""
    echo "Uninstall extensions managed by this repository"
    echo ""
    echo "Options:"
    echo "  --project <dir>   Uninstall from a specific project directory instead of home directory"
    echo "  --tools <tools>   Comma-separated targets: agents,claude,codex,opencode,pi"
    echo ""
    echo "Arguments:"
    echo "  TYPE    Extension type: ALL, skills, commands, agents, or pi-extensions"
    echo "  NAME    One or more extension names, or ALL for all of that type"
    echo ""
    echo "Examples:"
    echo "  $0 ALL                          # Uninstall all extensions from detected tools"
    echo "  $0 --tools claude,pi skills ALL # Uninstall all skills from Claude Code and pi"
    echo "  $0 --project /path/to/myapp --tools agents,claude ALL # Uninstall from a project"
    echo "  $0 skills ALL                   # Uninstall all skills"
    echo "  $0 skills guardrails            # Uninstall specific skill"
    echo "  $0 skills skill-1 skill-2       # Uninstall multiple skills"
    echo "  $0 pi-extensions ALL            # Uninstall all pi extensions"
    echo "  $0 pi-extensions permission-guard.ts  # Uninstall specific pi extension"
    exit 1
}

# Parse options
while [[ $# -gt 0 ]]; do
    case "$1" in
        --project)
            if [[ -z "$2" || "$2" == --* ]]; then
                echo "Error: --project requires a directory argument" >&2
                exit 1
            fi
            BASE_DIR="$(cd "$2" && pwd)"
            shift 2
            ;;
        --tools)
            if [[ -z "$2" || "$2" == --* ]]; then
                echo "Error: --tools requires a comma-separated tool list" >&2
                exit 1
            fi
            parse_tools_arg "$2" || exit 1
            shift 2
            ;;
        *)
            break
            ;;
    esac
done

if is_project_install; then
    echo "Uninstalling from project: $BASE_DIR"
fi

# Main logic
if [[ $# -eq 0 ]]; then
    usage
elif [[ $# -eq 1 ]]; then
    if [[ "$1" == "ALL" ]]; then
        for type in skills commands agents pi-extensions; do
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
    if [[ "$type" != "skills" && "$type" != "commands" && "$type" != "agents" && "$type" != "pi-extensions" ]]; then
        usage
    fi
    for name in "$@"; do
        if [[ "$name" == "ALL" ]]; then
            uninstall_all_of_type "$type"
        elif [[ "$type" == "pi-extensions" ]]; then
            uninstall_pi_extension "$name"
        else
            uninstall_extension "$type" "$name"
        fi
    done
else
    usage
fi

echo ""
echo "Done: $TOTAL_REMOVED removed, $TOTAL_SKIPPED skipped"
