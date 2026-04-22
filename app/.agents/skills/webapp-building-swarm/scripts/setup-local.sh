#!/bin/bash
set -e

# ─────────────────────────────────────────────────────────────────────────────
# Robust worktree setup with re-entry handling
#
# Usage: setup-local.sh <branch> [local-path]
#
# IMPORTANT: Each parallel subagent MUST use a unique local-path to avoid
# worktree metadata collisions in the shared git repo. Convention:
#   setup-local.sh <branch> $HOME/app-<branch>
#
# Handles:
#   - Fresh setup: creates worktree, copies node_modules, npm install
#   - Re-entry with same branch: reuses existing worktree (skips npm install)
#   - Re-entry with different branch: removes old worktree, creates fresh
#   - Stale non-git dir at local-path: removes and creates fresh
#   - Uses --force to handle stale entries from dead sandboxes
#
# WARNING: Never run `git worktree prune` — in multi-agent setups, other
# agents' worktree entries share the same .git/worktrees/ directory.
# Pruning would destroy their metadata.
# ─────────────────────────────────────────────────────────────────────────────

REPO_PATH="/mnt/agents/output/app"
BRANCH="${1:?Usage: setup-local.sh <branch> [local-path]}"
LOCAL_PATH="${2:-$HOME/app-$BRANCH}"

# Template node_modules from the image
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_NODE_MODULES="$SCRIPTS_DIR/template/node_modules"

cd "$REPO_PATH"

# ─────────────────────────────────────────────────────────────────────────────
# Handle existing directory at LOCAL_PATH
# ─────────────────────────────────────────────────────────────────────────────
if [ -d "$LOCAL_PATH" ]; then
    if [ -d "$LOCAL_PATH/.git" ] || git -C "$LOCAL_PATH" rev-parse --git-dir >/dev/null 2>&1; then
        # It's a git worktree — check if it's the right branch
        CURRENT_BRANCH=$(git -C "$LOCAL_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
        if [ "$CURRENT_BRANCH" = "$BRANCH" ]; then
            echo "Re-entry: worktree at $LOCAL_PATH already on branch '$BRANCH'. Reusing."
            cd "$LOCAL_PATH"
            echo "Ready: $LOCAL_PATH (branch: $BRANCH)"
            exit 0
        else
            echo "Re-entry: worktree at $LOCAL_PATH on branch '$CURRENT_BRANCH', need '$BRANCH'. Recreating."
            git worktree remove --force "$LOCAL_PATH" 2>/dev/null || rm -rf "$LOCAL_PATH"
        fi
    else
        echo "Stale non-git directory at $LOCAL_PATH. Removing."
        rm -rf "$LOCAL_PATH"
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# Create worktree (--force handles stale entries from dead sandboxes)
# ─────────────────────────────────────────────────────────────────────────────
git worktree add --force "$LOCAL_PATH" "$BRANCH"
cd "$LOCAL_PATH"

# ─────────────────────────────────────────────────────────────────────────────
# Install dependencies
# ─────────────────────────────────────────────────────────────────────────────
if [ -d "$TEMPLATE_NODE_MODULES" ]; then
    cp -r "$TEMPLATE_NODE_MODULES" ./
fi
npm install

echo "Ready: $LOCAL_PATH (branch: $BRANCH)"
