#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TARGET_ROOTS=("$HOME/.claude" "$HOME/.codex")

# Global counters
TOTAL_INSTALLED=0
TOTAL_SKIPPED=0

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

    if [[ ! -d "$skill_path" ]]; then
        echo "Error: Skill directory not found: $skill_path"
        return 1
    fi

    if [[ ! -f "$skill_path/SKILL.md" ]]; then
        echo "Error: Not a valid skill (missing SKILL.md): $skill_path"
        return 1
    fi

    echo "[$skill_name]"

    for root in "${TARGET_ROOTS[@]}"; do
        if [[ -d "$root" ]]; then
            local root_name="$(basename "$root")"
            local skills_dir="$root/skills"
            mkdir -p "$skills_dir"
            local target_path="$skills_dir/$skill_name"

            if [[ -e "$target_path" ]]; then
                echo "  - $root_name: Skipped (already exists)"
                ((TOTAL_SKIPPED++))
            else
                ln -s "$skill_path" "$target_path"
                echo "  - $root_name: Installed"
                ((TOTAL_INSTALLED++))
            fi
        fi
    done
    return 0
}

# Check arguments
if [[ $# -eq 0 ]]; then
    usage
fi

# Ensure target directory exists


if [[ "$1" == "ALL" ]]; then
    for dir in "$PROJECT_DIR"/*-skill; do
        if [[ -d "$dir" && -f "$dir/SKILL.md" ]]; then
            skill_name="$(basename "$dir")"
            install_skill "$skill_name"
        fi
    done

    echo ""
    echo "Done: $TOTAL_INSTALLED links installed, $TOTAL_SKIPPED targets skipped"
else
    install_skill "$1"
fi
