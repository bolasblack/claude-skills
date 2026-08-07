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

# Base directory for installation (default: $HOME, override with --project <dir>)
BASE_DIR="$HOME"
INSTALL_MODE="copy"

get_pi_extensions_dir() {
    if [[ -d "$PROJECT_DIR/pi-extensions/extensions" ]]; then
        echo "$PROJECT_DIR/pi-extensions/extensions"
    else
        echo "$PROJECT_DIR/pi-extensions"
    fi
}

relative_path() {
    local path="$1"
    local base="$2"
    local result=""

    while [[ "$path" != "$base/"* ]]; do
        base="${base%/*}"
        result="../$result"
    done

    printf '%s\n' "$result${path#"$base"/}"
}

usage() {
    echo "Usage: $0 [--mode <mode>] [--project <dir>] [--tools <tools>] <TYPE> <NAME...>"
    echo ""
    echo "Install extensions by copying or creating relative symlinks"
    echo ""
    echo "Options:"
    echo "  --mode <mode>     Installation mode: copy (default) or symlink"
    echo "  --project <dir>   Install to a specific project directory instead of home directory"
    echo "  --tools <tools>   Comma-separated targets: agents,claude,codex,opencode,pi"
    echo ""
    echo "Arguments:"
    echo "  TYPE    Extension type: ALL, __ALL, skills, commands, agents, or pi-extensions"
    echo "  NAME    One or more extension names, ALL for public, or __ALL for all (incl. private)"
    echo ""
    echo "Examples:"
    echo "  $0 ALL                          # Install all public extensions to detected tools"
    echo "  $0 --mode symlink skills guardrails  # Install a skill as relative symlinks"
    echo "  $0 --tools claude,pi skills ALL # Install all public skills to Claude Code and pi"
    echo "  $0 --project /path/to/myapp --tools agents,claude skills ALL  # Install skills to a project"
    echo "  $0 __ALL                        # Install all public and private extensions"
    echo "  $0 skills ALL                   # Install all public skills"
    echo "  $0 skills __ALL                 # Install all skills including private"
    echo "  $0 skills guardrails            # Install specific skill"
    echo "  $0 skills skill-1 skill-2       # Install multiple skills"
    echo "  $0 commands ALL                 # Install all commands"
    echo "  $0 agents code-reviewer         # Install specific agent"
    echo "  $0 pi-extensions ALL            # Install all pi extensions"
    echo "  $0 pi-extensions permission-guard.ts  # Install specific pi extension"
    echo ""
    echo "Available extensions:"
    echo ""
    echo "Skills:"
    for dir in "$PROJECT_DIR"/skills/*/ "$PROJECT_DIR"/private/skills/*/; do
        if [[ -d "$dir" && -f "$dir/SKILL.md" ]]; then
            [[ "$dir" == */private/* ]] && echo "  $(basename "$dir") (private)" || echo "  $(basename "$dir")"
        fi
    done
    echo ""
    echo "Commands:"
    for dir in "$PROJECT_DIR"/commands/*/ "$PROJECT_DIR"/private/commands/*/; do
        if [[ -d "$dir" && -f "$dir/COMMAND.md" ]]; then
            [[ "$dir" == */private/* ]] && echo "  $(basename "$dir") (private)" || echo "  $(basename "$dir")"
        fi
    done
    echo ""
    echo "Agents:"
    for dir in "$PROJECT_DIR"/agents/*/ "$PROJECT_DIR"/private/agents/*/; do
        if [[ -d "$dir" && -f "$dir/AGENT.md" ]]; then
            [[ "$dir" == */private/* ]] && echo "  $(basename "$dir") (private)" || echo "  $(basename "$dir")"
        fi
    done
    echo ""
    echo "Pi Extensions:"
    local pi_extensions_dir
    pi_extensions_dir=$(get_pi_extensions_dir)
    for path in "$pi_extensions_dir"/*; do
        if [[ -e "$path" ]]; then
            echo "  $(basename "$path")"
        fi
    done
    exit 1
}

install_to_target() {
    local tool_name="$1"
    local target_dir="$2"
    local type="$3"
    local name="$4"
    local source_path="$5"

    mkdir -p "$target_dir"

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

    local is_update=false
    if [[ -e "$target_path" || -L "$target_path" ]]; then
        if is_managed_by_us "$target_path" "$managed_by_file"; then
            rm -rf "$target_path"
            [[ "$type" != "skills" && -f "$managed_by_file" ]] && rm -f "$managed_by_file"
            is_update=true
        else
            echo "  - $tool_name: WARNING - Skipped (already exists, not managed by us)"
            TOTAL_WARNINGS=$((TOTAL_WARNINGS + 1))
            TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
            return 0
        fi
    fi

    if [[ "$INSTALL_MODE" == "symlink" ]]; then
        local link_source="$source_path"
        if [[ "$type" != "skills" && "$type" != "pi-extensions" ]]; then
            local main_file
            main_file=$(get_main_file "$type")
            link_source="$source_path/$main_file"
        fi
        ln -s "$(relative_path "$link_source" "$target_dir")" "$target_path"
    elif [[ "$type" == "skills" ]] || [[ "$type" == "pi-extensions" && -d "$source_path" ]]; then
        cp -r "$source_path" "$target_path"
        echo "$REPO_NAME" > "$target_path/.managed-by"
    else
        local main_file
        if [[ "$type" == "pi-extensions" ]]; then
            cp "$source_path" "$target_path"
        else
            main_file=$(get_main_file "$type")
            cp "$source_path/$main_file" "$target_path"
        fi
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

install_from_source() {
    local type="$1"
    local name="$2"
    local source_path="$3"

    resolve_targets "$type"
    if [[ ${#RESOLVED_TARGETS[@]} -eq 0 ]]; then
        return 0
    fi

    echo "[$type/$name]"

    local resolved_target tool_name target_dir
    for resolved_target in "${RESOLVED_TARGETS[@]}"; do
        tool_name="${resolved_target%%|*}"
        target_dir="${resolved_target#*|}"
        install_to_target "$tool_name" "$target_dir" "$type" "$name" "$source_path"
    done
}

install_extension() {
    local type="$1"
    local name="$2"
    local source_path="$PROJECT_DIR/$type/$name"
    if [[ ! -d "$source_path" && -d "$PROJECT_DIR/private/$type/$name" ]]; then
        source_path="$PROJECT_DIR/private/$type/$name"
    fi
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

    install_from_source "$type" "$name" "$source_path"
}

install_pi_extension() {
    local name="$1"
    local pi_extensions_dir
    pi_extensions_dir=$(get_pi_extensions_dir)
    local source_path="$pi_extensions_dir/$name"

    if [[ ! -e "$source_path" ]]; then
        echo "Error: Pi extension not found: $source_path"
        return 1
    fi

    install_from_source "pi-extensions" "$name" "$source_path"
}

install_all_of_type() {
    local type="$1"
    local include_private="${2:-false}"

    if [[ "$type" == "pi-extensions" ]]; then
        local pi_extensions_dir
        pi_extensions_dir=$(get_pi_extensions_dir)
        for path in "$pi_extensions_dir"/*; do
            if [[ -e "$path" ]]; then
                local name
                name=$(basename "$path")
                install_pi_extension "$name"
            fi
        done
        return 0
    fi

    local main_file
    main_file=$(get_main_file "$type")

    # Private extensions (private/<type>/): __ALL only.
    local roots=("$PROJECT_DIR/$type")
    if [[ "$include_private" == "true" && -d "$PROJECT_DIR/private/$type" ]]; then
        roots+=("$PROJECT_DIR/private/$type")
    fi

    local root
    for root in "${roots[@]}"; do
        for dir in "$root"/*/; do
            if [[ -d "$dir" && -f "$dir/$main_file" ]]; then
                local name
                name=$(basename "$dir")
                install_extension "$type" "$name"
            fi
        done
    done
}

# Parse options
while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode)
            case "${2:-}" in
                copy|symlink)
                    INSTALL_MODE="$2"
                    shift 2
                    ;;
                *)
                    echo "Error: Unsupported installation mode: ${2:-}" >&2
                    exit 1
                    ;;
            esac
            ;;
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
    echo "Installing to project: $BASE_DIR"
fi

# Main logic
if [[ $# -eq 0 ]]; then
    usage
elif [[ $# -eq 1 ]]; then
    if [[ "$1" == "ALL" || "$1" == "__ALL" ]]; then
        local_include_private="false"
        [[ "$1" == "__ALL" ]] && local_include_private="true"
        for type in skills commands agents pi-extensions; do
            if [[ -d "$PROJECT_DIR/$type" ]]; then
                install_all_of_type "$type" "$local_include_private"
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
        if [[ "$name" == "ALL" || "$name" == "__ALL" ]]; then
            local_include_private="false"
            [[ "$name" == "__ALL" ]] && local_include_private="true"
            install_all_of_type "$type" "$local_include_private"
        elif [[ "$type" == "pi-extensions" ]]; then
            install_pi_extension "$name"
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
