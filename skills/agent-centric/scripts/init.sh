#!/usr/bin/env bash
#
# Initialize .agents/ directory structure for Agent Centric framework.
#
# DO NOT MODIFY THIS FILE - it will be automatically updated from the skill directory.
#
# Usage:
#     bash init.sh <project_dir>
#
# This script:
#   1. Creates .agents/ directory structure
#   2. Copies scripts from skill directory
#   3. Creates config.json
#   4. Creates .agents/CLAUDE.md
#   5. Adds reference to project's root CLAUDE.md
#   6. Creates empty index files
#

set -e

PROJECT_DIR="${1:-.}"
SKILL_DIR="${CLAUDE_SKILL_DIR:-$(dirname "$(dirname "$0")")}"
AGENTS_DIR="$PROJECT_DIR/.agents"

echo "Initializing .agents/ directory in $PROJECT_DIR..."

# Create directory structure
mkdir -p "$AGENTS_DIR/decisions"
mkdir -p "$AGENTS_DIR/scripts"

# Create .gitkeep for empty decisions directory
touch "$AGENTS_DIR/decisions/.gitkeep"

# Copy scripts
cp "$SKILL_DIR/scripts/utils.py" "$AGENTS_DIR/scripts/"
cp "$SKILL_DIR/scripts/validate-agds.py" "$AGENTS_DIR/scripts/"
cp "$SKILL_DIR/scripts/generate-index.py" "$AGENTS_DIR/scripts/"
cp "$SKILL_DIR/scripts/sync-scripts.sh" "$AGENTS_DIR/scripts/"
chmod +x "$AGENTS_DIR/scripts/"*.py "$AGENTS_DIR/scripts/"*.sh

# Create config.json if not exists
if [ ! -f "$AGENTS_DIR/config.json" ]; then
    cat > "$AGENTS_DIR/config.json" << 'EOF'
{
  "tags": [],
  "disableAutoUpdateScripts": []
}
EOF
    echo "Created config.json"
fi

# Create .agents/CLAUDE.md from template
if [ ! -f "$AGENTS_DIR/CLAUDE.md" ]; then
    cp "$SKILL_DIR/templates/CLAUDE.md" "$AGENTS_DIR/CLAUDE.md"
    echo "Created .agents/CLAUDE.md"
fi

# Create empty index files
for INDEX_FILE in INDEX-TAGS.md INDEX-AGD-RELATIONS.md; do
    if [ ! -f "$AGENTS_DIR/$INDEX_FILE" ]; then
        touch "$AGENTS_DIR/$INDEX_FILE"
    fi
done

# Run generate-index to create proper index headers
python3 "$AGENTS_DIR/scripts/generate-index.py" "$PROJECT_DIR"
echo "Generated index files"

# Add reference to project's root CLAUDE.md
ROOT_CLAUDE_MD="$PROJECT_DIR/CLAUDE.md"
AGENTS_REF="See [.agents/CLAUDE.md](.agents/CLAUDE.md) for the Agent Centric framework."

if [ -f "$ROOT_CLAUDE_MD" ]; then
    if ! grep -q ".agents/CLAUDE.md" "$ROOT_CLAUDE_MD"; then
        echo "" >> "$ROOT_CLAUDE_MD"
        echo "$AGENTS_REF" >> "$ROOT_CLAUDE_MD"
        echo "Added reference to root CLAUDE.md"
    else
        echo "Reference already exists in root CLAUDE.md"
    fi
else
    echo "$AGENTS_REF" > "$ROOT_CLAUDE_MD"
    echo "Created root CLAUDE.md with reference"
fi

echo ""
echo "Initialization complete!"
echo ""
echo "Next steps:"
echo "  1. Add tags to .agents/config.json tags array"
echo "  2. Start creating AGD files in .agents/decisions/"
