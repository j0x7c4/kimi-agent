---
name: vibecoding-general-swarm
description: >
  General-purpose coding orchestration. MANDATORY for ANY coding task
  not covered by vibecoding-webapp-swarm. Skip ONLY if the task matches
  vibecoding-webapp-swarm or is entirely non-coding.
---

# Vibecoding General — Multi-Agent Coding Orchestration

Design-first, multi-agent workflow for building general software projects. Covers Python tools, data pipelines, ML systems, APIs, games, bots, CLI apps, mobile apps, and any non-frontend coding task.

## Core Principles

1. **Spec-first.** A specification document (`SPEC.md`) is written before any implementation. It is the single source of truth for architecture, modules, interfaces, and data flow.
2. **Spec fidelity.** Subagents implement SPEC.md faithfully — exact interfaces, exact module boundaries, exact data formats. No unilateral changes.
3. **Main agent owns init, merge, integration.** Subagents implement and commit on their branches.
4. **Parallelism by modules & features.** Each subagent owns one or more modules/features. Group related work into one agent to minimize cross-agent dependencies.
5. **Git worktrees isolate work.** Each subagent works in its own git worktree to avoid conflicts. The shared repo is the coordination hub.
6. **Interface contracts are sacred.** Define function signatures, data schemas, and file formats in the spec. Subagents implement to these contracts so modules integrate cleanly.
7. **Test before merge.** Each subagent runs tests for their module before committing. Main agent runs integration tests after merge.

## Mode Selection

| Condition | Mode |
|-----------|------|
| Task has 3+ distinct modules or components | **Mode A** (multi-agent) |
| Task involves both infrastructure and application logic | **Mode A** (multi-agent) |
| Task is a full system (API + workers + data pipeline, etc.) | **Mode A** (multi-agent) |
| Task is a single script, tool, or focused feature | **Mode B** (single agent) |
| Task is a bug fix or small enhancement | **Mode B** (single agent) |
| When in doubt | **Mode B** (single agent) |

---

## Worktree Reference

Git worktrees allow multiple agents to work on the same repo simultaneously without conflicts.

### Setup (each subagent)
```bash
cd /mnt/agents/output/project                         # shared repo
git worktree add $HOME/work-<branch> <branch>     # create local worktree
cd $HOME/work-<branch>                            # work here
```

### Rules
- Each subagent MUST use a unique worktree path (`$HOME/work-<branch>`).
- **Never run `git worktree prune`** — it destroys other agents' worktree entries.
- Never work directly in `/mnt/agents/output/project` — always use a worktree.
- After committing in a worktree, the main agent merges from the shared repo.

### Cleanup (main agent, after all merges complete)
```bash
cd /mnt/agents/output/project
git worktree remove $HOME/work-<branch>   # optional, per branch
```

---

## File Layout

```
/mnt/agents/output/
├── SPEC.md                        # Project specification (single source of truth)
├── info.md                        # Research findings (if applicable)
├── project/                       # Shared git repo (coordination hub)
│   ├── .git/
│   └── ...                        # Project structure per SPEC.md
│
$HOME/work-<branch>/               # Local worktree (unique per subagent)
└── ...                            # Same structure, isolated working copy
```
