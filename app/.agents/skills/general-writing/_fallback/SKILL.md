---
name: _fallback
type: capability
description: >
  Fallback creative writing handler for genres that do not match any specific
  sub-skill. Applies the general-writing pipeline with genre-neutral defaults
  and adaptive genre research. Use this when the user's creative writing request
  cannot be routed to fiction, fanfiction, poetry, lyrics, drama, screenplay,
  essay, game-writing, murder-mystery, trpg, or letter.
---

# Fallback Creative Writing

Sub-skill of [general-writing](../SKILL.md). Inherits shared creative writing principles, anti-AI discipline, and quality gate framework.

> **CRITICAL — Review → Fix Brief → Dispatched Subagent**: When a review finds issues, translate them into a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh writer subagent to apply the fix. Never use inline sed/edit_file fixes.

> **CRITICAL — Anti-Read-Loop Rule**: The orchestrator must dispatch its first subagent (genre_researcher or writer) within 10 iterations. If the orchestrator has spent 10+ iterations only reading files without creating any subagent, it is in a read-loop. Stop reading, proceed with your best understanding of the genre, and dispatch immediately.

> **CRITICAL — .docx Delivery**: Every completed work must be converted to .docx using `skills/docx/SKILL.md`. Never end a session with raw .md files and no .docx deliverable.

## When This Activates

This fallback handles requests that are clearly creative writing but match no named sub-skill. Examples: eulogy, speech, toast, wedding vows, advertising copy, manifesto, journal entry, travel writing, food writing, sermon, commencement address, brand storytelling, product description, satire, parody, memoir excerpt, prayer, epitaph, artist statement, grant proposal narrative, political speech, and any other unlisted creative form.

---

## Stage 0: Genre Discovery (Orchestrator)

The Orchestrator must name and understand the genre before proceeding.

### 0.1 Name the Genre

Classify into: oratory/ceremony (speech, toast, eulogy, sermon, vows, keynote), personal/reflective (journal, memoir, confession, prayer, artist statement), persuasive/advocacy (manifesto, polemic, political speech, grant narrative), commercial/brand (ad copy, product description, brand story, tagline), journalistic/documentary (profile, travel/food/nature writing, feature), critical/analytical (review, critique, commentary), short-form/digital (listicle, explainer, how-to, thread), ritual/ceremonial (blessing, epitaph, inscription, invocation), or hybrid/experimental.

### 0.2 Autonomous Genre Resolution

The orchestrator infers the genre autonomously from the user's query and any provided context. For ambiguous cases, deploy a subagent to analyze the request in depth. Never prompt the user for clarification.

### 0.3 Research Genre Conventions (if unfamiliar)

Skip if genre is well-understood (e.g., eulogy, toast). Otherwise deploy a research subagent:

**`create_subagent`**: `name: "genre_researcher"`, `system:` "You are a genre research specialist. Research the given genre's structural conventions, voice norms, length expectations, anti-patterns, and exemplary models. Output a concise genre brief (under 500 words)."

**Task prompt**: genre name, user context, what to research. Use the returned brief to inform Stages 1-2.

---

## Stage 1: Conception (Orchestrator — no subagents unless researching)

### 1.1 Adapt Outline to Genre

Match structure to genre: speech (hook → body → climax → close), eulogy (who they were → a story → what they meant → what endures), manifesto (problem → vision → principles → call to action), product description (need → solution → proof → action), travel writing (arrival → immersion → seeing differently → departure), etc.

For works >5k words, produce a two-phase outline: (1) structural outline — overall arc, section purposes, thematic progression → (2) per-section detail — scene content, emotional beats, transitions, word count targets.

### 1.2 Determine Voice

Record: formality, register, relationship to audience, emotional range. Use genre brief from Stage 0 if available.

### 1.3 Save Outline

Save to `/mnt/agents/output/{filename}.agent.outline.md`. Include: genre name, structural arc, voice profile, audience, occasion.

---

## Stage 2: Creation — Writer Subagent

Match subagent count to work complexity. For short works (< 3000 words): **single writer**. For longer or multi-section works: one writer per section, with context handoff.

**Strictly one section per `task` call** for multi-section works.

### Create Writer

**`create_subagent`**: `name: "writer"`, `system:` inline all of the following —

1. **Genre conventions** from Stage 0 — structural norms, voice expectations. Inline genre brief if produced.

2. **Anti-AI rules** — read `../anti-ai.md` and inline full content. Emphasize: no chatbot artifacts, no AI vocabulary clusters, no significance inflation, no copula avoidance, no hedging stacks. Specificity is the antidote.

3. **Voice profile** from Stage 1.

### Dispatch via `task`

**Task prompt content**:
- The outline (full text)
- Tone and audience description
- Occasion and context
- Word count target
- Any user-provided reference material or constraints
- Output path: `/mnt/agents/output/{filename}_sec01.md`

After each section completes, orchestrator runs word count verification:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, return to writer with expansion instructions.

---

## Stage 3: Review — Shared Pipeline Only

Read `../review.md` and run the shared review pipeline. The fallback uses **no genre-specific editors** — only the three shared editors:

1. **`continuity_editor`** — skip for single-section works; use for multi-section
2. **`style_editor`** — AI-pattern scan, voice consistency, rhythm variety
3. **`structural_editor`** — pacing, transitions, arc completeness, balance

### Scoring

| Dimension | Weight | What to Check |
|-----------|--------|---------------|
| Genre appropriateness | 25% | Follows the genre's conventions? Feels like the right form? |
| Voice quality | 25% | Distinctive, appropriate voice? Anti-AI checklist passed? |
| Purpose fulfillment | 25% | Achieves what it's supposed to? |
| Craft quality | 25% | Prose quality, AI-pattern absence, structural integrity |

**Pass**: >= 75 overall. On FAIL: write a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh writer subagent to apply the fix → re-review. Max 2 cycles.

---

## Stage 4: Delivery

### Assemble

For multi-section works, concatenate all `{filename}_sec{NN}.md` files in order. Save to `/mnt/agents/output/{filename}.agent.final.md`.

### Convert to .docx

Convert the assembled markdown to Word using the `md2docx` pipeline (see `skills/docx/SKILL.md` → `references/md2docx-reference.md`).

Output: `/mnt/agents/output/{filename}.agent.final.docx`

**This step is mandatory.** Raw .md without a .docx deliverable is not an acceptable end state.

---

## Anti-AI Discipline

Do NOT duplicate the checklist here. Read and inline `../anti-ai.md` into every writer subagent's system prompt. Applies to every genre without exception. When in doubt: **add specific details**.

Before submitting to review, apply three self-tests: (1) **Read-aloud test** — if a sentence sounds awkward spoken, rewrite. (2) **Name-swap test** — change the subject; if the text works unchanged, it's generic — add specifics. (3) **Paragraph-removal test** — delete each paragraph; if the piece doesn't weaken, it's padding — cut it.

---

## Reference Files

| File | Purpose | When to Read |
|------|---------|--------------|
| [../anti-ai.md](../anti-ai.md) | AI patterns to avoid — inline into writer system prompt | Before Stage 2 |
| [../review.md](../review.md) | Shared review pipeline, editor definitions, quality gates | Before Stage 3 |
| [../scripts/check_wordcount.py](../scripts/check_wordcount.py) | Word count verification | After each section completes — Orchestrator runs directly |
| [../SKILL.md](../SKILL.md) | Parent skill — shared principles, routing, file naming | On entry |
