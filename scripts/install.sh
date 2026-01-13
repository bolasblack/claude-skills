#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Global counters
TOTAL_INSTALLED=0
TOTAL_SKIPPED=0

usage() {
    echo "Usage: $0 <TYPE> <NAME|ALL>"
    echo ""
    echo "Install extensions as symlinks to Claude Code, Codex, and OpenCode"
    echo ""
    echo "Arguments:"
    echo "  TYPE   Extension type: ALL, skills, commands, or agents"
    echo "  NAME   Name of the extension to install, or ALL for all of that type"
    echo ""
    echo "Examples:"
    echo "  $0 ALL                  # Install all extensions of all types"
    echo "  $0 skills ALL           # Install all skills"
    echo "  $0 skills color-master  # Install specific skill"
    echo "  $0 commands ALL         # Install all commands"
    echo "  $0 agents code-reviewer # Install specific agent"
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

get_main_file() {
    local type="$1"
    case "$type" in
        skills) echo "SKILL.md" ;;
        commands) echo "COMMAND.md" ;;
        agents) echo "AGENT.md" ;;
        *) echo "" ;;
    esac
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

    # Determine target subdirectory name (OpenCode uses singular form)
    local target_subdir="$type"
    if [[ "$tool_name" == "opencode" ]]; then
        case "$type" in
            commands) target_subdir="command" ;;
            agents) target_subdir="agent" ;;
        esac
    fi

    local target_dir="$tool_root/$target_subdir"
    mkdir -p "$target_dir"

    # Skills: link to directory
    # Commands/Agents: link to main file as <name>.md (they don't support directories)
    local target_path
    local link_source
    if [[ "$type" == "skills" ]]; then
        target_path="$target_dir/$name"
        link_source="$source_path"
    else
        target_path="$target_dir/${name}.md"
        local main_file
        main_file=$(get_main_file "$type")
        link_source="$source_path/$main_file"
    fi

    if [[ -e "$target_path" ]]; then
        echo "  - $tool_name: Skipped (already exists)"
        TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
    else
        ln -s "$link_source" "$target_path"
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

    # OpenCode: supports skills, commands (as command), agents (as agent)
    install_to_tool "$HOME/.config/opencode" "opencode" "$type" "$name" "$source_path"

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
elif [[ $# -eq 2 ]]; then
    type="$1"
    name="$2"
    if [[ "$type" != "skills" && "$type" != "commands" && "$type" != "agents" ]]; then
        usage
    fi
    if [[ "$name" == "ALL" ]]; then
        install_all_of_type "$type"
    else
        install_extension "$type" "$name"
    fi
else
    usage
fi

echo ""
echo "Done: $TOTAL_INSTALLED links installed, $TOTAL_SKIPPED targets skipped"
