---
name: paper-writing
type: capability
description: >
  End-to-end academic paper creation — outline design, structured content writing,
  review, and assembly. Covers survey papers, empirical research, technical papers,
  case studies, literature reviews, and any formal academic writing requiring
  methodology sections, contribution positioning, and rigorous citation. Outputs
  are delivered in Markdown (`.md`) format.
  Do NOT use for: industry reports, consulting deliverables, policy briefs (use report-writing).
---

# Paper Writing

Orchestrate the full lifecycle of academic papers: outline design → content creation → review → assembly.

If the user explicitly requests an output format, deliver that format. If the user does not specify a format, deliver `.docx` by default. Workflow artifacts may still be generated in Markdown (`.md`) as intermediate files; when `.docx` delivery is needed, use the docx-related skill at `skills/docx/SKILL.md` to convert the generated Markdown artifact.

## Workflow Decision Tree

```
User Query
  │
  ├─ Research artifacts found at /mnt/agents/output/research/
  │   → Pre-Stage (load) → Stage 1 → Stage 2 → Stage 3 → Stage 4
  │
  ├─ No artifacts + topic requires literature survey
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

If the directory is empty or missing and the task requires literature survey or factual research:

1. Create `/mnt/agents/output/research/`
2. Decompose the research scope into **3–5 literature dimensions** (e.g., by research thread, methodology family, application domain)
3. Deploy **parallel research sub-agents**, one per dimension, each performing ≥5 searches focused on academic sources
4. Each sub-agent saves output to `/mnt/agents/output/research/{topic}_dim{NN}.md`
5. Orchestrator performs lightweight cross-verification → `{topic}_cross_verification.md`, extracts insights (research gaps, methodological tensions, contribution angles) → `{topic}_insight.md`
6. Proceed to Stage 1

The downstream pipeline (Stage 1–4) is identical regardless of artifact source.

## Stage 1: Outline Design

**Read [outline.md](./outline.md) first.**

**Goal**: Produce a structured, executable outline following academic paper conventions.

**Process**:
1. Deploy parallel sub-agents:
   - `requirement_analyst` — extract research questions, scope, target venue
   - `artifact_analyst` — synthesize research artifacts from `/mnt/agents/output/research/` to identify prior work, research gaps, and positioning opportunities
   - `structure_designer` — design section hierarchy, word budgets
   - `methodology_planner` — outline research approach, evaluation criteria
2. Synthesize into unified outline (4-level heading format per outline.md)
3. Save to `/mnt/agents/output/{filename}.agent.outline.md` — do not skip this step; Stage 2 depends on the outline file
4. If full paper intended: one sentence asking whether to proceed
5. If outline only: deliver and stop

**Academic-specific**: The outline must establish the paper's **contribution statement** — what is new, how it differs from prior work, and why it matters.

## Stage 2: Content Creation

**Read [content.md](./content.md) first. Follow its Resolution Principle, System Prompt Template, and Task Prompt Template.**

**Prerequisite**: Research artifacts MUST exist at `/mnt/agents/output/research/` before this stage begins.

**Research artifact handoff**: The Orchestrator passes research artifacts to each writer as Input Materials (see content.md template):
- **Every writer** receives: `{topic}_insight.md` (research gaps, contribution angles) and `{topic}_cross_verification.md` (confidence tiers)
- **Each writer** receives the `{topic}_dim{NN}.md` files relevant to their section (e.g., Related Work gets literature-focused dims, Methodology gets technique-focused dims)
- **User-provided sources**: Even though research agents already read user-supplied files (PDFs, URLs, etc.) during the research stage, writers still need the original paths. Research extractions inevitably lose exact figures, table data, formulas, and nuanced arguments that writers need for accurate, detailed prose. Pass the relevant source paths to each writer alongside the dim files. Select per-section — not everything to everyone.
- **User-provided sources**: Even though research agents already read user-supplied files (PDFs, URLs, etc.) during the research stage, writers still need the original paths. Research extractions inevitably lose exact figures, table data, formulas, and nuanced arguments that writers need for accurate, detailed prose. Pass the relevant source paths to each writer alongside the dim files. Select per-section — not everything to everyone.
- **User-provided sources**: Even though research agents already read user-supplied files (PDFs, URLs, etc.) during the research stage, writers still need the original paths. Research extractions inevitably lose exact figures, table data, formulas, and nuanced arguments that writers need for accurate, detailed prose. Pass the relevant source paths to each writer alongside the dim files. Select per-section — not everything to everyone.

- Writers do NOT perform web searches for core literature (minor supplementary searches acceptable)

**Goal**: Produce all sections as individual markdown files with academic rigor, proper citation density, and methodological transparency.

**Process**:
1. Parse outline: extract sections, word counts, dependencies
2. **Resolve all writer configuration** before creating any sub-agent (style, color scheme, section conventions — see content.md)
3. Section grouping: independent → parallelize; dependent → serialize
   **Round dispatch** (for stages with 3+ sections):
   Parallel tasks CANNOT see each other's output. Before dispatching, analyze dependencies:
   1. List the dependency graph among sections.
   2. Group into rounds: Round 1 = sections with no upstream dependencies; Round 2 = sections depending on Round 1 outputs; and so on.
   3. Abstract / conclusion / synthesis sections MUST be in a later round than the content they summarize.
   4. For later-round sections, pass the actual outputs from earlier rounds as context — do not substitute with pre-existing materials when the produced content is available.
   5. When in doubt, dispatch in separate rounds.
4. Create Writer via `create_subagent` (System Prompt Template), dispatch via `task` (Task Prompt Template)
5. Validate each section before proceeding to dependents

**Critical dependency chain**: Introduction → (Related Work ∥ Methodology) → Results → Discussion → Conclusion → Abstract (written last)

## Stage 3: Review Pipeline

**Read [review.md](./review.md) first.**

**Pipeline** (sequential):
```
section_editor (per section, parallelizable)
  → methodology_reviewer (rigor and reproducibility check)
    → coherence_editor (cross-section consistency)
      → abstract_reviewer (accuracy against final content)
        → citation_manager (read citation.md for this step)
```

Each editor can pass or delegate rewrites in-place.

## Stage 4: Assembly

1. **Blocked until citation_manager completes** — `_ref.md` must exist before merging
2. Merger sub-agent concatenates all `_sec{NN}.md` files in academic order, appends reference list, saves as `/mnt/agents/output/{filename}.agent.final.md`
3. Final validation: cross-references, heading hierarchy, citation/figure/table numbering continuity
4. Convert to `.docx` by default (pass docx skill path `/app/.agents/skills/docx/SKILL.md` to merger). User-specified format overrides. Both `.md` and formatted file are delivered.

## Core Principles

1. **Research and writing are separate agents.** Research agents gather information; writer agents produce content from provided materials. Non-negotiable.
2. **Markdown first, then format.** `.agent.final.md` is mandatory intermediate output.
3. **Execute to completion.** Do not pause unless outline needs confirmation.
4. **Everything is a file.** No long-form content in chat.
5. **File naming**: `{filename}_sec{NN}.md` for sections, `{filename}_ref.md` for references, `{filename}.agent.outline.md` for outline, `{filename}.agent.final.md` for final.
6. **Rewrites are in-place.** No version proliferation.
7. **Language consistency.** All content — prose, sub-agent names, prompts, deliverables — must match the user's language. Never mix languages unless explicitly requested.
8. **Context flows forward.** Orchestrator maintains cross-section context for dependent sections.
9. **Citation integrity.** MCP tools auto-record to `/mnt/agents/.citation.jsonl` and return globally unique citation indices (e.g., `[^49^]`). Writers MUST use these indices as-is — never renumber. Section files contain only `[^N^]` markers in body text, no reference lists. See [citation.md](./citation.md).
10. **Abstract is written last.** It summarizes actual findings, not planned findings.
11. **User-provided sources reach writers.** Research-stage extractions (dim files) inevitably lose exact figures, formulas, and nuanced arguments. When the user supplied reference files or URLs, include the relevant original paths in each writer's task prompt — even though research agents already read them. Select per-section, not dump all.
12. **Strict UTF-8.** When reading or concatenating `_sec{NN}.md` files during assembly, always use `encoding='utf-8'` with no error handler. On `UnicodeDecodeError`, re-dispatch the writer for the corrupted section. Never fall back to `latin-1`, `gbk`, `cp1252`, `errors='ignore'`, or `errors='replace'` — these convert a detectable error into silent mojibake in the delivered `.docx`.

## Reference Files

| File | When to Read | Content |
|------|-------------|---------|
| [outline.md](./outline.md) | Before Stage 1 | Academic outline methodology, structure conventions, contribution framing |
| [content.md](./content.md) | Before Stage 2 | Resolution principle, prompt templates, section writing conventions, color schemes |
| [review.md](./review.md) | Before Stage 3 | Academic review criteria, methodology review, quality gates |
| [citation.md](./citation.md) | Before citation_manager | Citation styles (APA/IEEE/etc.), source tiers, manager workflow |
| [styles/*.md](./styles/) | Before Stage 2 | Paper-type-specific conventions |
