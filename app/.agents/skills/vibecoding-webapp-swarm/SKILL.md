---
name: vibecoding-webapp-swarm
description: >
  Build any web-based project: websites, landing pages, web apps, dashboards,
  browser games, portfolios, and interactive experiences. Design-first
  React workflow. Skip if the user explicitly requests a non-React
  framework (Vue, Svelte, Angular, vanilla HTML) or the task is unrelated to
  web UI (CLI tools, scripts, data pipelines).
---

# Vibecoding — Multi-Agent Webapp Building

Design-first, multi-agent workflow for building rich, multi-page React webapps. We aim for **sophisticated, content-rich websites** — not minimal demos. Think 5-10+ pages with rich content, interactive features, animations, and polish.

**Full-stack requests** (Next.js, backend APIs, databases): full-stack backend is NOT possible in the current sandbox. Proceed with a frontend-only React SPA and explain to the user that backend/server-side is outside sandbox capabilities. Mock API responses with realistic static data so the frontend is fully functional and demonstrable.

**Default tech stack (pinned versions — communicate to all subagents):**
- Node.js 20 · Tailwind CSS v3.4.19 · Vite v7.2.4 · React 19 + TypeScript · shadcn/ui

Use this stack unless the user explicitly specifies a different one (e.g. Vue, Svelte, vanilla JS, Python+Flask). If the user specifies a different stack, follow their choice first — but you can still borrow the orchestration principles from this skill (design-first workflow, multi-agent decomposition, parallel page agents, octopus merge).

## Companion Skills

### design-guide (`/app/.agents/skills/vibecoding-webapp-swarm/design-guide.md`)

Design reference for the Pro_Designer subagent. Covers visual capabilities (GSAP, Framer Motion, Three.js, Lenis, Google Fonts), design document format, animation spec requirements, and asset manifest format. **Read by the Designer subagent** at the start of Phase 2.

### react-dev (`/app/.agents/skills/vibecoding-webapp-swarm/react-dev.md`)

React implementation guide. Covers GSAP, Framer Motion, Three.js/R3F, Tailwind v3, animation performance, layout patterns. **Read by all implementation subagents** (scaffold + page agents). Not read by Designer or main agent.

### webapp-building (`/app/.agents/skills/webapp-building-swarm/SKILL.md`)

Tech stack reference: project scaffolding via `init-webapp.sh`, worktree setup via `setup-local.sh`, 13 design templates, build pipeline. **Read by main agent** to understand init and build.

## Core Principles

1. **Design-first.** `design.md` is written before any implementation begins. It is the single source of truth.
2. **Design fidelity.** Subagents implement `design.md` faithfully — exact colors, exact values, exact text. No "improving" or substituting.
3. **Main agent owns init, merge, deploy.** Sub-agents implement and commit on their branches.
4. **Parallelism by pages AND features.** Each sub-agent can own pages (About, Services) or features (shopping cart, search system, interactive calculator). Group related work into one agent.
5. **Aim for richness.** We have multi-agent parallelism — use it. Build content-rich, feature-complete websites rather than minimal ones. 5-10+ pages, interactive features, animations.
6. **Git worktrees isolate work.** Heavy work (editing, builds) happens on local filesystems via `setup-local.sh`; the OSS repo is the coordination hub.
7. **Deploy once and STOP.** No verification loop after deployment. Do NOT open the URL, take screenshots, or review.
8. **Full-stack not possible.** Build a fully functional frontend with mock data. Explain backend is outside sandbox scope.

## Mode Selection

| Condition | Mode |
|-----------|------|
| Building a website/webapp IS the primary task | **Mode A** (multi-agent) |
| Building a website/webapp is sophisticated or content-rich | **Mode A** (multi-agent) |
| Cloning/replicating an existing website | **Mode A** (multi-agent) |
| Website is a side deliverable AND simple (1-3 pages, no complex interactions) AND the primary task already requires multi-agent work | **Mode B** (single agent) |
| When in doubt | **Mode A** (multi-agent) |

---

## Mode A — Webapp as Main Task (Multi-Agent)

### Phase 1: Plan & Init (Main Agent)

1. **Read skills**: Read this SKILL.md and `webapp-building-swarm/SKILL.md`.
2. **Init project**:
   ```bash
   PROJECT_PATH=$HOME/init REMOTE_PATH=/mnt/agents/output/app bash /app/.agents/skills/webapp-building-swarm/scripts/init-webapp.sh "<website-title>"
   ```
   Creates the project locally at `$HOME/init`, initializes git, clones to `/mnt/agents/output/app` (shared OSS hub).
   Use the default template (`0-origin`) unless the user explicitly requests a specific template by name.
3. **Research** (if needed): Browse URLs, search for content. Write findings to `/mnt/agents/output/info.md`.

**Important:** Do NOT plan page structure, page count, visual direction, or design details in this phase. Those decisions belong entirely to the Designer in Phase 2. Your task here is only to init the project and gather research.

### Phase 2: Design (Pro_Designer Subagent)

Create a subagent named **"Pro_Designer"** (name must contain "designer" — case-insensitive — for model routing).

**Designer system prompt** — use this exact text (do NOT customize per query):
> "You are a world-class web designer. You create comprehensive, detailed design documents for websites. You have deep expertise in modern web design, typography, color theory, animation, and responsive layouts."

**Designer task prompt** — use this exact template, filling in only {USER_QUERY} and {RESEARCH} placeholders:

```
Read `/app/.agents/skills/vibecoding-webapp-swarm/design-guide.md` in full. Follow it as your design reference.

## User Request

"{USER_QUERY}"

{RESEARCH — include this section only if /mnt/agents/output/info.md exists:
## Research Findings
[paste contents of info.md]
}

## Instructions

Read the user's request and create a complete design. Determine the appropriate page count, structure, and visual direction based on the request. Aim for a content-rich, ambitious website with interactive features and visual polish. For clone/replicate requests, faithfully capture the main page's design and expand into additional sub-pages the original site would have.

Write all design files to `/mnt/agents/output/design/`:
- `design.md` — Global design document
- `[page].md` — One per page, named by topic (e.g. `home.md`, `about.md`, `services.md`)
```

**Rules — the prompt must be exactly the template above:**
- Do NOT add sections like "Key Context", "Design Guidelines", "Important Notes", or "Output Requirements".
- Do NOT add your own creative interpretation of the user's request (color suggestions, style directions, reference companies, mock data instructions).
- Do NOT paraphrase the user request — copy it character-for-character.
- The Designer reads the design guide and user request; it makes ALL creative decisions independently.

### Phase 3: Read Design & Delegate (Main Agent)

After the Designer completes:

1. **Read `design/design.md`** — the global design and page list. You do NOT need to read per-page designs.
2. **Decide grouping**: Based on **the page list in design.md** (not your own assumptions), group pages/features into 3-6 parallel agents. Each agent can own multiple related pages or features (e.g., "Services + Pricing" → one agent, "Shopping cart + checkout" → one agent).
4. **Create scaffold branch only** (page branches are created AFTER scaffold merge — see Phase 5):
   ```bash
   cd /mnt/agents/output/app
   git branch scaffold
   ```
5. **Launch Scaffold subagent**.

### Phase 4: Scaffold (Single Subagent)

Launch one subagent. Its prompt MUST include:

1. "Run `bash /app/.agents/skills/webapp-building-swarm/scripts/setup-local.sh scaffold $HOME/app-scaffold`"
2. "Read `/app/.agents/skills/vibecoding-webapp-swarm/react-dev.md` in full."
3. "Read `/mnt/agents/output/design/design.md` in full."
4. "Read `/mnt/agents/output/design/home.md` in full (the landing page design)."
5. Tech stack versions: Node.js 20, Tailwind CSS v3.4.19, Vite v7.2.4.
6. The original user request.
7. **"Generate media assets: Read the Assets section in design.md. For each image asset listed, use the image generation tool with the description as the prompt. For each video asset listed, use the video generation tool with the description as the prompt. Save all generated media to `$HOME/app-scaffold/public/<filename>`. After generating all media, commit: `cd $HOME/app-scaffold && git add public/ && git diff --cached --quiet || git commit -m 'assets: add generated media'`"**
8. "Implement the COMPLETE landing/home page following `design/home.md`."
9. "Create shared components at these EXACT paths (page agents depend on them): `src/components/Navbar.tsx` (with links to all routes), `src/components/Footer.tsx`, `src/components/Layout.tsx`."
10. "Set up `HashRouter` with route stubs for all sub-pages."
11. "Configure Tailwind theme, global CSS, Google Fonts per design.md."
12. "Install additional packages from design.md Dependencies."
13. "Reference generated media via `/<filename>` (e.g. `<img src="/hero-bg.png" />`, `<video src="/hero-loop.mp4" />`) — these are served from `public/` at build time."
14. "`cd $HOME/app-scaffold && git add -A && git commit -m 'scaffold: landing page + shared infra'`"
15. "After committing, return immediately. No need to run the dev server, open a browser, take screenshots, or verify your work. The main agent handles building and deployment."

### Phase 5: Merge Scaffold & Create Page Branches (Main Agent)

```bash
cd /mnt/agents/output/app && git merge scaffold --no-edit
```

**Now** create page branches — they must branch from the merged master so page agents inherit scaffold code (Navbar, Footer, Layout, shared styles):
```bash
cd /mnt/agents/output/app
git branch <group1>
git branch <group2>
# ... one branch per agent group
```

### Phase 6: Parallel Subagents

Launch **all** subagents simultaneously (single message, multiple `task` tool calls).

Each subagent prompt MUST include:

1. "Run `bash /app/.agents/skills/webapp-building-swarm/scripts/setup-local.sh <branch> $HOME/app-<branch>`" (each subagent MUST use a unique path — `$HOME/app-<branch>`)
2. "Read `/app/.agents/skills/vibecoding-webapp-swarm/react-dev.md` in full."
3. "Read `/mnt/agents/output/design/design.md` in full."
4. "Read `/mnt/agents/output/design/[page].md` for your assigned page(s)."
5. Tech stack versions: Node.js 20, Tailwind CSS v3.4.19, Vite v7.2.4.
6. Clear assignment — pages AND/OR features. A subagent can own a feature like "shopping cart system" or "interactive quiz", not just named pages.
7. "Read the existing design system from the scaffold: `cat src/components/Navbar.tsx src/components/Footer.tsx src/index.css src/App.tsx`"
8. "ONLY create/modify files for your assigned scope. Must NOT modify: `src/App.tsx`, `src/index.css`, shared components, `public/`."
9. "Install any additional packages your pages require that aren't already in the project."
10. "Export each page as a default React component."
11. "Reference generated media via `/<filename>` as specified in your page design files (e.g. `<img src="/hero-bg.png" />`, `<video src="/hero-loop.mp4" />`). The Scaffold agent has already generated and committed them."
12. "`cd $HOME/app-<branch> && git add -A && git commit -m '<scope>: implement'`"
13. "After committing, return immediately. No need to run the dev server, open a browser, take screenshots, or verify your work. The main agent handles building and deployment."

### Phase 7: Merge, Build & Deploy (Main Agent)

1. **Merge all branches**:
   ```bash
   cd /mnt/agents/output/app && git branch final-build
   bash /app/.agents/skills/webapp-building-swarm/scripts/setup-local.sh final-build $HOME/app-final-build
   cd $HOME/app-final-build
   git merge <group1> <group2> ... --no-edit
   ```
   If octopus merge fails (conflicts), merge branches one at a time: `git merge <group1> --no-edit`, resolve, then `git merge <group2> --no-edit`, etc.

2. **Wire routes** in `src/App.tsx`: import page components, add `<Route>` entries inside `<HashRouter>`.

3. **Build**:
   ```bash
   cd $HOME/app-final-build && npm run build 2>&1
   ```
   If build fails: fix, rebuild (up to 3 retries).

4. **Copy dist to OSS and update master**:
   ```bash
   cp -r $HOME/app-final-build/dist /mnt/agents/output/app/
   cd /mnt/agents/output/app && git merge final-build --no-edit
   ```

5. **Deploy** from `/mnt/agents/output/app/dist/`. Present URL to user.

6. **STOP.** No verification after deploy.

---

## Mode B — Webapp as Side Task (Single Agent)

1. **Main agent**: Read `webapp-building-swarm/SKILL.md`. Run `init-webapp.sh` with `REMOTE_PATH`:
   ```bash
   PROJECT_PATH=$HOME/init REMOTE_PATH=/mnt/agents/output/app bash /app/.agents/skills/webapp-building-swarm/scripts/init-webapp.sh "<website-title>"
   ```
   Then create a work branch:
   ```bash
   cd /mnt/agents/output/app && git branch work
   ```
2. **Single subagent**: Its prompt MUST include:
   - "Read `/app/.agents/skills/vibecoding-webapp-swarm/design-guide.md` for design inspiration and `/app/.agents/skills/vibecoding-webapp-swarm/react-dev.md` for implementation reference."
   - "Run `bash /app/.agents/skills/webapp-building-swarm/scripts/setup-local.sh work $HOME/app-work`"
   - Tech stack versions: Node.js 20, Tailwind CSS v3.4.19, Vite v7.2.4.
   - The original user request.
   - "Write a single `/mnt/agents/output/design/design.md` (no per-page files needed — one comprehensive document). Then implement the entire site. Commit."
3. **Main agent**: Merge, build, deploy:
   ```bash
   cd /mnt/agents/output/app && git merge work --no-edit
   bash /app/.agents/skills/webapp-building-swarm/scripts/setup-local.sh final $HOME/app-final
   cd $HOME/app-final && npm run build 2>&1
   cp -r $HOME/app-final/dist /mnt/agents/output/app/
   ```
   Deploy from `/mnt/agents/output/app/dist/`. **No verification after deploy.**

---

## Actor Reference

| Action | Actor |
|--------|-------|
| Read vibecoding-webapp-swarm SKILL.md | Main agent |
| Run init-webapp.sh | Main agent |
| Research (browse, search) | Main agent |
| Create Pro_Designer subagent | Main agent |
| Read design-guide.md, write design.md + per-page designs + asset manifest | Pro_Designer subagent |
| Read design.md | Main agent |
| Decide grouping, create branches | Main agent |
| Read react-dev.md | All implementation subagents |
| Generate & commit media assets from design.md asset manifest | Scaffold subagent |
| Implement landing page + shared infra | Scaffold subagent |
| Merge scaffold | Main agent |
| Implement pages/features | Parallel subagents |
| Merge all branches | Main agent |
| Wire routes in App.tsx | Main agent |
| Build + Deploy | Main agent |

## File Layout

```
/mnt/agents/output/
├── design/                       # Design documents
│   ├── design.md                 # Global design (fonts, colors, spacing, style)
│   ├── home.md                   # Landing page design
│   ├── about.md                  # Per-page design (named by topic)
│   └── ...
├── info.md                       # Research findings (if applicable)
├── app/                          # Shared git repo on OSS
│   ├── .git/
│   ├── public/
│   │   └── *.png/jpg/mp4/...     # Generated & committed by Scaffold subagent
│   ├── src/
│   └── dist/                     # Copied from local build for deployment
│
$HOME/app-<branch>/               # Local worktree (unique per subagent)
├── public/
│   └── *.png/jpg/mp4/...         # Available to all agents; reference as /<file>
├── src/
├── node_modules/
├── dist/
└── ...
```
