#!/bin/bash
set -e

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────

# Default template (base project with 40+ shadcn/ui components)
ORIGIN_TEMPLATE_NAME="0-origin"

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Pre-built node_modules from image (prepared by .prepare-template.sh at image build time)
ORI_TEMPLATE_PATH="$SCRIPTS_DIR/template"

REPO_ROOT="$(cd "$SCRIPTS_DIR/.." && pwd)"
PROJECT_NAME="$1"
TEMPLATE_NAME="${2:-$ORIGIN_TEMPLATE_NAME}"
[[ "$OSTYPE" == "darwin"* ]] && SED_INPLACE="sed -i ''" || SED_INPLACE="sed -i"

TEMPLATE_PATH="$REPO_ROOT/templates/$TEMPLATE_NAME"

# ─────────────────────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────────────────────

! command -v npm &>/dev/null && { echo "Error: npm not found"; exit 1; }
[[ -z "$1" ]] && { echo "Usage: $0 <project-name>"; exit 1; }
[[ ! -d "$TEMPLATE_PATH" ]] && { echo "Error: template not found: $TEMPLATE_NAME"; exit 1; }
TEMPLATE_ZIP="$TEMPLATE_PATH/$TEMPLATE_NAME.zip"
INFO_MD="$TEMPLATE_PATH/info.md"
if [[ ! -f "$TEMPLATE_ZIP" ]]; then
    echo "Error: Template '$TEMPLATE_NAME' not found at: $TEMPLATE_ZIP"
    echo "Available templates:"
    ls "$REPO_ROOT/templates" 2>/dev/null | sed 's/^/  - /' || true
    exit 1
fi

PROJECT_PATH=${PROJECT_PATH:-"/mnt/agents/output/app"}
TEMP_PATH=${TEMP_PATH:-"/tmp/temp-webapp"}

# ─────────────────────────────────────────────────────────────────────────────
# Project Creation
# ─────────────────────────────────────────────────────────────────────────────

echo "Creating project: $PROJECT_PATH"
mkdir -p "$PROJECT_PATH"
[[ -d "$TEMP_PATH" ]] && rm -rf "$TEMP_PATH"
mkdir -p "$TEMP_PATH"

# ─────────────────────────────────────────────────────────────────────────────
# Dependencies
# ─────────────────────────────────────────────────────────────────────────────

echo "Installing dependencies..."

unzip "$TEMPLATE_ZIP" -d "$TEMP_PATH" > /dev/null 2>&1
# If extracted dir has template name, use that
if [[ -d "$TEMP_PATH/$TEMPLATE_NAME" ]]; then
    TEMP_PATH="$TEMP_PATH/$TEMPLATE_NAME"
fi

cp "$INFO_MD" "$TEMP_PATH"/info.md

ESCAPED_REPLACE=$(printf '%s\n' "$PROJECT_NAME" | sed 's/[\/&]/\\&/g')
$SED_INPLACE 's/<title>.*<\/title>/<title>'"$ESCAPED_REPLACE"'<\/title>/' "$TEMP_PATH"/index.html

cp -r "$TEMP_PATH"/* "$PROJECT_PATH"/

# Copy pre-built node_modules
cp -r "$ORI_TEMPLATE_PATH"/node_modules "$PROJECT_PATH"/

# For non-default templates, install additional dependencies
if [[ "$TEMPLATE_NAME" != "$ORIGIN_TEMPLATE_NAME" ]]; then
  cd "$PROJECT_PATH"
  npm install
fi

# ─────────────────────────────────────────────────────────────────────────────
# Done
# ─────────────────────────────────────────────────────────────────────────────
if [[ "$TEMPLATE_NAME" != "$ORIGIN_TEMPLATE_NAME" ]]; then
  echo ""
  echo "✓ Template '$TEMPLATE_NAME' extracted successfully to: $PROJECT_PATH"
  echo ""
  echo "═══════════════════════════════════════════════════════════════════════════"
  echo "TEMPLATE INFO"
  echo "═══════════════════════════════════════════════════════════════════════════"
  echo ""
  if [[ -f "$INFO_MD" ]]; then
    cat "$INFO_MD"
  else
    echo "⚠ No info.md found for this template."
  fi
  echo ""
  echo "═══════════════════════════════════════════════════════════════════════════"
else
  [[ -f "$INFO_MD" ]] && cat "$INFO_MD"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Git init + clone to remote (OSS) for multi-agent worktree coordination
# ─────────────────────────────────────────────────────────────────────────────
if [ -n "$REMOTE_PATH" ]; then
    cd "$PROJECT_PATH"
    echo -e 'node_modules\ndist\n.DS_Store' >> .gitignore
    git init
    git add -A
    git commit -m "project init"
    git clone "$PROJECT_PATH" "$REMOTE_PATH"
    cd "$REMOTE_PATH" && git remote remove origin
    echo ""
    echo "Git repo cloned to: $REMOTE_PATH"
fi
