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

# Public skills included in "ALL" installs.
# Experimental skills (environment-specific) are excluded from ALL
# but included in __ALL.
PUBLIC_SKILLS=(
    agent-centric
    command-creator
    design-md
    frontend-design
    guardrails
    mcp-context7
    mcp-deepwiki
    mcp-fetch
    mcp-grep
    mcp-skill-generator
    parallel-agent-workflow
    pi-extension-dev
    playwright
    seo-article-optimizer
    seo-site-audit
    skill-composer
)

get_pi_extensions_dir() {
    if [[ -d "$PROJECT_DIR/pi-extensions/extensions" ]]; then
        echo "$PROJECT_DIR/pi-extensions/extensions"
    else
        echo "$PROJECT_DIR/pi-extensions"
    fi
}

usage() {
    echo "Usage: $0 [--project <dir>] [--tools <tools>] <TYPE> <NAME...>"
    echo ""
    echo "Install extensions by copying to Claude Code, Codex, OpenCode, agents, and pi"
    echo ""
    echo "Options:"
    echo "  --project <dir>   Install to a specific project directory instead of home directory"
    echo "  --tools <tools>   Comma-separated targets: agents,claude,codex,opencode,pi"
    echo ""
    echo "Arguments:"
    echo "  TYPE    Extension type: ALL, __ALL, skills, commands, agents, or pi-extensions"
    echo "  NAME    One or more extension names, ALL for public, or __ALL for all (incl. experimental)"
    echo ""
    echo "Examples:"
    echo "  $0 ALL                          # Install all public extensions to detected tools"
    echo "  $0 --tools claude,pi skills ALL # Install all public skills to Claude Code and pi"
    echo "  $0 --project /path/to/myapp --tools agents,claude skills ALL  # Install skills to a project"
    echo "  $0 __ALL                        # Install all extensions including experimental"
    echo "  $0 skills ALL                   # Install all public skills"
    echo "  $0 skills __ALL                 # Install all skills including experimental"
    echo "  $0 skills color-master          # Install specific skill"
    echo "  $0 skills skill-1 skill-2       # Install multiple skills"
    echo "  $0 commands ALL                 # Install all commands"
    echo "  $0 agents code-reviewer         # Install specific agent"
    echo "  $0 pi-extensions ALL            # Install all pi extensions"
    echo "  $0 pi-extensions permission-guard.ts  # Install specific pi extension"
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

    if [[ "$type" == "skills" ]] || [[ "$type" == "pi-extensions" && -d "$source_path" ]]; then
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

is_public_skill() {
    local name="$1"
    for s in "${PUBLIC_SKILLS[@]}"; do
        if [[ "$s" == "$name" ]]; then
            return 0
        fi
    done
    return 1
}

install_all_of_type() {
    local type="$1"
    local include_experimental="${2:-false}"

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

    for dir in "$PROJECT_DIR/$type"/*/; do
        if [[ -d "$dir" && -f "$dir/$main_file" ]]; then
            local name
            name=$(basename "$dir")
            # For skills, skip experimental ones unless include_experimental is true
            if [[ "$type" == "skills" && "$include_experimental" != "true" ]]; then
                if ! is_public_skill "$name"; then
                    continue
                fi
            fi
            install_extension "$type" "$name"
        fi
    done
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
    echo "Installing to project: $BASE_DIR"
fi

# Main logic
if [[ $# -eq 0 ]]; then
    usage
elif [[ $# -eq 1 ]]; then
    if [[ "$1" == "ALL" || "$1" == "__ALL" ]]; then
        local_include_experimental="false"
        [[ "$1" == "__ALL" ]] && local_include_experimental="true"
        for type in skills commands agents pi-extensions; do
            if [[ -d "$PROJECT_DIR/$type" ]]; then
                install_all_of_type "$type" "$local_include_experimental"
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
            local_include_experimental="false"
            [[ "$name" == "__ALL" ]] && local_include_experimental="true"
            install_all_of_type "$type" "$local_include_experimental"
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
