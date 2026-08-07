#!/bin/bash

# Common utilities for install/uninstall scripts

# Repository name to write to .managed-by file
REPO_NAME="bolasblack/claude-skills"

# Repository names that we manage (may change in the future)
MANAGED_REPOS=(
    "bolasblack/claude-skills"
    "c4605/claude-skills"
)

AVAILABLE_TOOLS=(agents claude codex opencode pi)
SELECTED_TOOLS=()
TOOLS_SPECIFIED=false
RESOLVED_TARGETS=()

is_project_install() {
    [[ "$BASE_DIR" != "$HOME" ]]
}

is_supported_tool() {
    local tool="$1"
    local available_tool
    for available_tool in "${AVAILABLE_TOOLS[@]}"; do
        if [[ "$available_tool" == "$tool" ]]; then
            return 0
        fi
    done
    return 1
}

add_selected_tool() {
    local tool="$1"
    if ! is_supported_tool "$tool"; then
        echo "Error: Unsupported tool: $tool" >&2
        echo "Supported tools: ${AVAILABLE_TOOLS[*]}" >&2
        return 1
    fi

    local selected_tool
    for selected_tool in "${SELECTED_TOOLS[@]}"; do
        if [[ "$selected_tool" == "$tool" ]]; then
            return 0
        fi
    done

    SELECTED_TOOLS+=("$tool")
}

parse_tools_arg() {
    local tools_arg="$1"
    if [[ -z "$tools_arg" ]]; then
        echo "Error: --tools requires a comma-separated tool list" >&2
        return 1
    fi

    TOOLS_SPECIFIED=true

    local parts
    local old_ifs="$IFS"
    IFS=',' read -r -a parts <<< "$tools_arg"
    IFS="$old_ifs"

    local tool
    for tool in "${parts[@]}"; do
        tool="${tool//[[:space:]]/}"
        if [[ -n "$tool" ]]; then
            add_selected_tool "$tool" || return 1
        fi
    done

    if [[ ${#SELECTED_TOOLS[@]} -eq 0 ]]; then
        echo "Error: --tools requires at least one tool" >&2
        return 1
    fi
}

add_resolved_target() {
    local tool_name="$1"
    local target_dir="$2"
    local detect_path="$3"

    if [[ "$TOOLS_SPECIFIED" != "true" && ! -d "$detect_path" ]]; then
        return 0
    fi

    local resolved_target
    for resolved_target in "${RESOLVED_TARGETS[@]}"; do
        if [[ "${resolved_target#*|}" == "$target_dir" ]]; then
            return 0
        fi
    done

    RESOLVED_TARGETS+=("$tool_name|$target_dir")
}

add_tool_target() {
    local tool_name="$1"
    local type="$2"
    local detect_path target_dir target_subdir

    case "$tool_name" in
        agents)
            [[ "$type" != "skills" ]] && return 0
            detect_path="$BASE_DIR/.agents"
            target_dir="$BASE_DIR/.agents/skills"
            ;;
        claude)
            [[ "$type" == "pi-extensions" ]] && return 0
            detect_path="$BASE_DIR/.claude"
            target_subdir=$(get_target_subdir "claude" "$type")
            target_dir="$detect_path/$target_subdir"
            ;;
        codex)
            [[ "$type" != "skills" ]] && return 0
            if is_project_install; then
                detect_path="$BASE_DIR/.codex"
                target_dir="$BASE_DIR/.agents/skills"
            else
                detect_path="$BASE_DIR/.codex"
                target_dir="$BASE_DIR/.codex/skills"
            fi
            ;;
        opencode)
            [[ "$type" == "pi-extensions" ]] && return 0
            if is_project_install && [[ "$type" == "skills" ]]; then
                detect_path="$BASE_DIR/.opencode"
                target_dir="$BASE_DIR/.agents/skills"
            else
                if is_project_install; then
                    detect_path="$BASE_DIR/.opencode"
                else
                    detect_path="$BASE_DIR/.config/opencode"
                fi
                target_subdir=$(get_target_subdir "opencode" "$type")
                target_dir="$detect_path/$target_subdir"
            fi
            ;;
        pi)
            case "$type" in
                skills|agents)
                    if is_project_install; then
                        detect_path="$BASE_DIR/.pi"
                    else
                        detect_path="$BASE_DIR/.pi/agent"
                    fi
                    target_subdir=$(get_target_subdir "pi" "$type")
                    target_dir="$detect_path/$target_subdir"
                    ;;
                pi-extensions)
                    if is_project_install; then
                        detect_path="$BASE_DIR/.pi"
                    else
                        detect_path="$BASE_DIR/.pi/agent"
                    fi
                    target_dir="$detect_path/extensions"
                    ;;
                *)
                    return 0
                    ;;
            esac
            ;;
    esac

    add_resolved_target "$tool_name" "$target_dir" "$detect_path"
}

resolve_targets() {
    local type="$1"
    RESOLVED_TARGETS=()

    local tools
    if [[ "$TOOLS_SPECIFIED" == "true" ]]; then
        tools=("${SELECTED_TOOLS[@]}")
    else
        tools=(claude agents codex opencode pi)
    fi

    local tool_name
    for tool_name in "${tools[@]}"; do
        add_tool_target "$tool_name" "$type"
    done
}

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
    if [[ "$link_target" != /* ]]; then
        local link_dir link_parent
        link_dir="$(dirname "$target_path")/$(dirname "$link_target")"
        link_parent=$(cd "$link_dir" && pwd) || return 1
        link_target="$link_parent/$(basename "$link_target")"
    fi
    if [[ "$link_target" == "$PROJECT_DIR" || "$link_target" == "$PROJECT_DIR/"* ]]; then
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
