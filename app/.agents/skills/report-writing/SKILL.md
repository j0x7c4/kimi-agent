---
name: report-writing
type: capability
description: >
  End-to-end long-form report creation — outline design, multi-chapter content
  writing, review, and assembly. Covers industry research, market analysis,
  policy briefs, technical reports, consulting deliverables, and any structured
  long-form non-fiction requiring research, argumentation, and citations. Outputs
  are delivered in Markdown (`.md`) format.
  Do NOT use for: academic papers (use paper-writing), creative fiction, blog
  posts, or short-form content under 2000 words.
---

# Report Writing

Orchestrate the full lifecycle of professional long-form reports: outline design → content creation → review → assembly.

If the user explicitly requests an output format, deliver that format. If the user does not specify a format, deliver `.docx` by default. Workflow artifacts may still be generated in Markdown (`.md`) as intermediate files; when `.docx` delivery is needed, use the docx-related skill at `skills/docx/SKILL.md` to convert the generated Markdown artifact.

## Workflow Decision Tree

```
User Query
  │
  ├─ Research artifacts found at /mnt/agents/output/research/
  │   → Pre-Stage (load) → Stage 1 → Stage 2 → Stage 3 → Stage 4
  │
  ├─ No artifacts + topic requires research
  │   → Pre-Stage (create) → Stage 1 → Stage 2 → Stage 3 → Stage 4
  │
  ├─ Provides outline + asks for content
  │   → Stage 2 → Stage 3 → Stage 4
  │
  ├─ Asks for outline only → Stage 1 → deliver and stop
  │
  └─ Provides draft + asks for revision → Stage 3 → Stage 4
```

## Pre-Stage: Research Artifact Detection & Creation

**Before starting any stage**, check `/mnt/agents/output/research/` for research artifacts.

### Path A: Artifacts exist

If `{topic}_dim*.md`, `{topic}_cross_verification.md`, and `{topic}_insight.md` are found:
- Load them as research input for Stage 1–2. No additional research sub-agents needed.

### Path B: No artifacts — create them

If the directory is empty or missing and the task requires factual research:

1. Create `/mnt/agents/output/research/`
2. Decompose the topic into **3–5 research dimensions**
3. Deploy **parallel research sub-agents**, one per dimension, each performing ≥5 searches
4. Each sub-agent saves output to `/mnt/agents/output/research/{topic}_dim{NN}.md`
5. Orchestrator performs lightweight cross-verification → `{topic}_cross_verification.md`, extracts insights → `{topic}_insight.md`
6. Proceed to Stage 1

The downstream pipeline (Stage 1–4) is identical regardless of artifact source.

## Stage 1: Outline Design

**Read [outline.md](./outline.md) first.**

**Goal**: Produce a structured, executable outline.

**Process**:
1. Deploy parallel sub-agents:
   - `requirement_analyst` — extract requirements from user query + uploaded files
   - `structure_designer` — design chapter hierarchy, word counts
   - `artifact_analyst` — synthesize research artifacts from `/mnt/agents/output/research/`
   - `content_planner` — define content points and required elements per chapter
2. Synthesize into unified outline (4-level heading format per outline.md)
3. Save to `/mnt/agents/output/{filename}.agent.outline.md` — do not skip this step; Stage 2 depends on the outline file
4. If full report intended: one sentence asking whether to proceed
5. If outline only: deliver and stop

## Stage 2: Content Creation

**Read [content.md](./content.md) first. Follow its Resolution Principle, System Prompt Template, and Task Prompt Template.**

**Prerequisite**: Research artifacts MUST exist at `/mnt/agents/output/research/` before this stage begins.

**Research artifact handoff**: The Orchestrator passes research artifacts to each writer as Input Materials (see content.md template):
- **Every writer** receives: `{topic}_insight.md` and `{topic}_cross_verification.md`
- **Each writer** receives the `{topic}_dim{NN}.md` files relevant to their chapter
- **User-provided sources**: Even though research agents already read user-supplied files (PDFs, URLs, etc.) during the research stage, writers still need the original paths. Research extractions inevitably lose exact figures, table data, and nuanced arguments that writers need for accurate, detailed prose. Pass the relevant source paths to each writer alongside the dim files. Select per-chapter — not everything to everyone.
- **User-provided sources**: Even though research agents already read user-supplied files (PDFs, URLs, etc.) during the research stage, writers still need the original paths. Research extractions inevitably lose exact figures, table data, and nuanced arguments that writers need for accurate, detailed prose. Pass the relevant source paths to each writer alongside the dim files. Select per-chapter — not everything to everyone.
- **User-provided sources**: Even though research agents already read user-supplied files (PDFs, URLs, etc.) during the research stage, writers still need the original paths. Research extractions inevitably lose exact figures, table data, and nuanced arguments that writers need for accurate, detailed prose. Pass the relevant source paths to each writer alongside the dim files. Select per-chapter — not everything to everyone.

- Writers do NOT perform web searches for core research (minor supplementary searches acceptable)

**Process**:
1. Parse outline: extract chapters, word counts, dependencies
2. **Resolve all writer configuration** before creating any sub-agent (style, color scheme, instructions — see content.md)
3. Chapter grouping: independent → parallelize; dependent → serialize with context handoff
   **Round dispatch** (for stages with 3+ chapters):
   Parallel tasks CANNOT see each other's output. Before dispatching, analyze dependencies:
   1. List the dependency graph among chapters.
   2. Group into rounds: Round 1 = chapters with no upstream dependencies; Round 2 = chapters depending on Round 1 outputs; and so on.
   3. Summary / conclusion / synthesis chapters MUST be in a later round than the content they summarize.
   4. For later-round chapters, pass the actual outputs from earlier rounds as context — do not substitute with pre-existing materials when the produced content is available.
   5. When in doubt, dispatch in separate rounds.
4. Create Writer via `create_subagent` (System Prompt Template), dispatch via `task` (Task Prompt Template)
5. **One chapter per task — never merge.**
6. Validate each chapter output before proceeding to dependents

## Stage 3: Review Pipeline

**Read [review.md](./review.md) first.**

**Pipeline** (sequential — each stage gates the next):
```
section_editor (per chapter, parallelizable)
  → transition_editor (cross-chapter coherence)
    → intro_conclusion_reviewer (bookend quality)
      → citation_manager (read citation.md for this step)
```

Each editor can pass or delegate rewrites. Rewrites happen in-place.

## Stage 4: Assembly

1. **Blocked until citation_manager completes** — `_ref.md` must exist before merging
2. Merger sub-agent concatenates all `_sec{NN}.md` files, appends reference list, saves as `/mnt/agents/output/{filename}.agent.final.md`
3. Final validation: cross-references, heading hierarchy, citation continuity
4. Convert to `.docx` by default (pass docx skill path `/app/.agents/skills/docx/SKILL.md` to merger). User-specified format overrides. Both `.md` and formatted file are delivered.

## Core Principles

1. **Research and writing are separate agents.** Research agents gather information; writer agents produce content from provided materials. Non-negotiable.
2. **Markdown first, then format.** `.agent.final.md` is mandatory intermediate output.
3. **Execute to completion.** Do not pause unless outline needs confirmation.
4. **Everything is a file.** No long-form content in chat. Chat is for status updates only.
5. **File naming**: `{filename}_sec{NN}.md` for chapters, `{filename}_ref.md` for references, `{filename}.agent.outline.md` for outline, `{filename}.agent.final.md` for final.
6. **Rewrites are in-place.** No version proliferation.
7. **Language consistency.** All content — prose, sub-agent names, prompts, deliverables — must match the user's language. Never mix languages unless explicitly requested.
8. **Context flows forward.** Orchestrator passes cross-chapter context explicitly to later-stage agents.
9. **Citation integrity.** MCP tools auto-record to `/mnt/agents/.citation.jsonl` and return globally unique citation indices (e.g., `[^49^]`). Writers MUST use these indices as-is — never renumber. Chapter files contain only `[^N^]` markers in body text, no reference lists. See [citation.md](./citation.md).
10. **User-provided sources reach writers.** Research-stage extractions (dim files) inevitably lose exact figures, formulas, and nuanced arguments. When the user supplied reference files or URLs, include the relevant original paths in each writer's task prompt — even though research agents already read them. Select per-chapter, not dump all.
11. **Strict UTF-8.** When reading or concatenating `_sec{NN}.md` files during assembly, always use `encoding='utf-8'` with no error handler. On `UnicodeDecodeError`, re-dispatch the writer for the corrupted section. Never fall back to `latin-1`, `gbk`, `cp1252`, `errors='ignore'`, or `errors='replace'` — these convert a detectable error into silent mojibake in the delivered `.docx`.

## Reference Files

| File | When to Read | Content |
|------|-------------|---------|
| [outline.md](./outline.md) | Before Stage 1 | Outline methodology, format spec, sub-agent strategy |
| [content.md](./content.md) | Before Stage 2 | Resolution principle, prompt templates, writing standards, color schemes |
| [review.md](./review.md) | Before Stage 3 | Editor roles, review criteria, quality gates |
| [citation.md](./citation.md) | Before citation_manager | Citation format, source tiers, manager workflow |
| [styles/*.md](./styles/) | Before Stage 2 | Domain-specific voice, tone, conventions |
