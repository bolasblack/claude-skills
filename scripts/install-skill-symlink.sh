#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
USER_SKILLS_DIR="$HOME/.claude/skills"

usage() {
    echo "Usage: $0 <skill-name|ALL>"
    echo ""
    echo "Install skills as user skills via symlink to ~/.claude/skills/"
    echo ""
    echo "Arguments:"
    echo "  <skill-name>  Name of the skill directory to install"
    echo "  ALL           Install all skills from this project"
    echo ""
    echo "Available skills:"
    for dir in "$PROJECT_DIR"/*-skill; do
        if [[ -d "$dir" && -f "$dir/SKILL.md" ]]; then
            echo "  $(basename "$dir")"
        fi
    done
    exit 1
}

install_skill() {
    local skill_name="$1"
    local skill_path="$PROJECT_DIR/$skill_name"
    local target_path="$USER_SKILLS_DIR/$skill_name"

    if [[ ! -d "$skill_path" ]]; then
        echo "Error: Skill directory not found: $skill_path"
        return 1
    fi

    if [[ ! -f "$skill_path/SKILL.md" ]]; then
        echo "Error: Not a valid skill (missing SKILL.md): $skill_path"
        return 1
    fi

    if [[ -e "$target_path" ]]; then
        echo "Skipped: $skill_name (skill folder already exists)"
        return 2
    fi

    ln -s "$skill_path" "$target_path"
    echo "Installed: $skill_name"
    return 0
}

# Check arguments
if [[ $# -eq 0 ]]; then
    usage
fi

# Ensure target directory exists
mkdir -p "$USER_SKILLS_DIR"

if [[ "$1" == "ALL" ]]; then
    installed=0
    skipped=0

    for dir in "$PROJECT_DIR"/*-skill; do
        if [[ -d "$dir" && -f "$dir/SKILL.md" ]]; then
            skill_name="$(basename "$dir")"
            # Capture return code to avoid `set -e` exit on non-zero
            ret=0
            install_skill "$skill_name" || ret=$?
            case $ret in
                # `|| true` prevents `set -e` exit when var increments from 0
                0) ((installed++)) || true ;;
                2) ((skipped++)) || true ;;
            esac
        fi
    done

    echo ""
    echo "Done: $installed installed, $skipped skipped"
else
    install_skill "$1"
fi
