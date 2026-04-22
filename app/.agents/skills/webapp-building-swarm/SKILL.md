---
name: webapp-building-swarm
type: artifact
description: Tools for building modern React webapps with TypeScript, Tailwind CSS and shadcn/ui. Best suited for applications with complex UI components and state management. Supports optional templates for specialized requirement.
---

# WebApp Building

**Stack**: React + TypeScript + Vite + Tailwind CSS + shadcn/ui

## Architecture

Two key directories in the swarm setup:

| Path | Purpose | Who uses it |
|------|---------|-------------|
| `/mnt/agents/output/app` | Shared git repo on OSS — coordination hub for branches. **Do NOT build or edit code here.** | Main agent (branch creation, merges) |
| `$HOME/app-<branch>` | Local worktree — fast local filesystem for editing, building, npm install. Each subagent uses a **unique path** per branch to avoid worktree metadata collisions. | All subagents (scaffold, page agents) |

## Scripts

All scripts use absolute paths from `/app/.agents/skills/webapp-building-swarm/scripts/`.

### `init-webapp.sh` — Project initialization (run by main agent)

```bash
# Multi-agent mode: creates project locally, clones to shared OSS repo
PROJECT_PATH=$HOME/init REMOTE_PATH=/mnt/agents/output/app \
  bash /app/.agents/skills/webapp-building-swarm/scripts/init-webapp.sh "<website-title>"
```

- Unzips template, copies pre-built `node_modules`, sets HTML title
- With `REMOTE_PATH`: initializes git, clones to OSS for multi-agent coordination
- Optional second arg: template name (default: `0-origin`)

### `setup-local.sh` — Worktree setup (run by subagents)

```bash
bash /app/.agents/skills/webapp-building-swarm/scripts/setup-local.sh <branch> $HOME/app-<branch>
```

- Creates a git worktree from the shared repo at `/mnt/agents/output/app`
- **Each subagent MUST use a unique local path** (`$HOME/app-<branch>`) to avoid worktree metadata collisions in the shared git repo
- Copies pre-built `node_modules` from `scripts/template/`
- Runs `npm install` to resolve any additional deps
- Handles re-entry: reuses existing worktree if same branch, recreates if different
- **Never run `git worktree prune`** — it destroys other agents' worktree entries

### `.prepare-template.sh` — Image build-time only

Creates `scripts/template/node_modules/` by unzipping `0-origin` and running `npm install`. Run once at image build time, not at runtime.

## What the template includes

- React + TypeScript (via Vite)
- Tailwind CSS 3.4.19 with shadcn/ui theming system
- Path aliases (`@/`) configured
- 40+ shadcn/ui components pre-installed
- All Radix UI dependencies included
- Production build optimization with Vite
- Node 20+ compatibility

## Build & Deploy

Build and deploy happen on a **local worktree**, not on the shared OSS repo:

```bash
# Build locally (use the worktree path for the final-build branch)
cd $HOME/app-final-build && npm run build 2>&1

# Copy dist to OSS for deployment
cp -r $HOME/app-final-build/dist /mnt/agents/output/app/

# Deploy from OSS
# (use deploy_website tool with local_dir: /mnt/agents/output/app/dist)
```

**Output** (`dist/`):
- `index.html` — Entry point
- `assets/index-[hash].js` — Bundled JS
- `assets/index-[hash].css` — Bundled CSS

## Available Templates

Use the default template (`0-origin`) unless the user explicitly requests a specific template by name.

| Template | Description |
|----------|-------------|
| 0-origin | Base template with 40+ shadcn/ui components (default) |
| airlens-style | Premium dark forest portfolio with GSAP/Lenis/Swiper |
| exhibition-style | Editorial magazine with custom cursor, noise overlay |
| exvia-style | Cinematic hero with mouse-tracking, bento grid |
| forest-style | Dark chocolate brand with Framer Motion |
| kaleo-style | Earth-toned editorial with card stack, Ken Burns |
| lipstick-style | Bold Swiss-grid beauty product with GSAP pinned scroll |
| modo-style | Premium gallery with stacking cards, custom cursor |
| photographer-style | Dark cinematic with particles, 3D transforms |
| playza-style | Cyberpunk music with 3D album cube (Three.js/R3F) |
| shibumi-style | Artisan e-commerce with shopping cart, parallax |
| swiss-dada-style | Bold product landing with 3D mouse parallax |
| villa-style | Winery/villa with showcase tabs, carousel, timeline |

## Reference

- [shadcn/ui Components](https://ui.shadcn.com/docs/components)
