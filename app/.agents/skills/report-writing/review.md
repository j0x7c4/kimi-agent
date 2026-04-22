# Review Pipeline Reference

## Pipeline Architecture

Review runs sequentially — each stage gates the next. Later stages assume earlier issues are resolved.

```
section_editor (per chapter, parallelizable across chapters)
  ↓ all chapters pass
transition_editor (cross-chapter, single agent reads all chapters)
  ↓ pass
intro_conclusion_reviewer (if report has intro/executive summary/conclusion)
  ↓ pass
citation_manager (consolidate references — see citation.md)
```

## Section Editor

**Scope**: One chapter at a time. Multiple section_editors can run in parallel on different chapters.

**Task prompt must include**: file path of the chapter, the outline section it was written against, and the review criteria below.

**Review dimensions**:

1. **Completeness**: Does the chapter cover every H4 point from the outline? Word count targets met? Required elements (tables, case studies) present?

2. **Information density**: Does every paragraph carry a concrete information point? Flag paragraphs that are filler or throat-clearing.

3. **Analytical depth**: Does the chapter explain "why" and "so what," or just list facts? Flag sections that describe without analyzing.

4. **Citation quality**: Are key claims backed by `[^N^]` citations? Are sources T1/T2? Flag uncited statistics and vague attributions ("studies show...").

5. **Writing quality**: Is prose natural and professional? Flag AI-isms ("It's worth noting that...", "In the rapidly evolving landscape of..."). Flag bullet-heavy sections that should be prose.

6. **Visual compliance**: Do tables have inline citations and ≥100 words of follow-up analysis? Do charts have labels, legends, and source notes?

**Decision**:
- **Pass**: Note strengths briefly. Proceed to next stage.
- **Fail**: Identify specific problems with locations (section numbers, paragraph descriptions). Write concrete fix instructions. Delegate a Writer sub-agent to rewrite the same file. Re-review after rewrite.

**Rewrite protocol**: Always rewrite in the original file. The writer receives: specific issues, locations, and fix instructions — not just "improve quality."

## Transition Editor

**Scope**: Cross-chapter coherence. A single agent reads all chapter files in sequence.

**Must receive**: Paths to all completed chapter files in order, plus the outline for global structure reference.

**Review dimensions**:

1. **Inter-chapter flow**: Does each chapter's opening connect naturally to the previous ending? Flag jarring transitions.

2. **Terminology consistency**: Same concept, same term throughout. Flag alternating terminology for the same metric.

3. **Logical progression**: Does the argument build across chapters? Do later chapters reference earlier findings, or feel isolated?

4. **Data consistency**: If Chapter 2 cites $50B and Chapter 4 says "approximately $50B," do numbers match exactly? Flag discrepancies.

5. **Redundancy**: Same points made in multiple chapters? Flag and recommend consolidation.

**Output**: Specific issues with chapter/section locations. For each, specify which file needs editing and what the fix should be. Delegate targeted rewrites to Writer sub-agents.

## Intro and Conclusion Reviewer

**Scope**: Only introductory sections (executive summary, introduction) and concluding sections (conclusion, recommendations).

**Why separate**: Intros and conclusions have different quality criteria than body chapters. An intro must preview key findings accurately. A conclusion must synthesize, not summarize.

**Intro / Executive Summary criteria**:
- Accurately reflects the report's actual findings (not just outline expectations)
- Self-contained: busy reader gets the core message from this alone
- Establishes scope without excessive detail
- 3–5 most important findings prominently featured

**Conclusion / Recommendations criteria**:
- Synthesizes across chapters rather than summarizing each sequentially
- Recommendations are actionable and specific
- Addresses limitations honestly
- Points to implications or future developments

**Timing**: Runs AFTER transition_editor — intro/conclusion quality depends on the body being finalized.

## Quality Gate Protocol

At each stage, the result is binary: pass or fail.

**On failure**:
1. Editor produces a remediation brief: which file, which section, what's wrong, how to fix
2. Orchestrator dispatches a Writer sub-agent with the remediation brief to rewrite in-place
3. Same editor re-reviews the rewritten sections (not the entire chapter unless issues were pervasive)
4. Maximum 2 rewrite cycles per chapter per editor stage. If still failing, flag to Orchestrator for escalation or proceed with a note

**Context maintenance**: When transition_editor delegates a rewrite for Chapter 3 based on inconsistency with Chapter 1, the writer for Chapter 3 must receive the relevant excerpt from Chapter 1 — not just "be consistent with Chapter 1."
