---
name: letter
type: capability
description: >
  Letter and epistle writing — personal letters, love letters, open letters,
  thank-you letters, condolence letters, formal correspondence, digital messages,
  application letters, and epistolary works. Handles tone calibration, relationship
  dynamics, voice adaptation, and the intimate voice of direct address.
---

# Letter Writing

Orchestrator dispatches all creation and review work to subagents. Before creation, copy user-uploaded files to `/mnt/agents/output/research/`.

Sub-skill of [general-writing](../SKILL.md). Inherits shared creative writing principles, anti-AI discipline, and quality gate framework.

> **CRITICAL — Review → Fix Brief → Dispatched Subagent**: When a review finds issues, translate them into a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh `letter_writer` subagent to apply the fix. Never use inline sed/edit_file fixes.

> **CRITICAL — Anti-Read-Loop Rule**: The orchestrator must dispatch its first subagent (letter_writer) within 10 iterations. If the orchestrator has spent 10+ iterations only reading files without creating any subagent, it is in a read-loop. Stop reading, draft your conception from what you have, and dispatch the writer immediately.

> **CRITICAL — .docx Delivery**: Every completed letter must be converted to .docx using `skills/docx/SKILL.md`. Never end a session with raw .md files and no .docx deliverable.

## File Paths

```
Output: /mnt/agents/output/
  {project_name}.letter.md              # Final letter
  research/                              # User uploads (writing samples, context docs)
```

## Trigger Keywords

书信, letter, 情书, 公开信, 遗书, 感谢信, open letter, epistle, 致辞, 家书, 道歉信, farewell letter, condolence letter, 推荐信, cover letter, application letter, email, 求职信, 申请信

---

## Pre-Stage: Context Inference

Infer letter type, sender/recipient relationship, occasion, tone, and length from the user's request. The orchestrator analyzes and infers all parameters autonomously; for complex requests, deploy a subagent to analyze requirements in depth. Never prompt the user for clarification.

If the user provides **writing samples from the sender** — collect them. Voice adaptation is mandatory when samples exist.

---

## Stage 1: Conception (Orchestrator — no subagents)

Letters are short works. The Orchestrator plans directly — no subagents for conception.

### 1.1 Identify the Emotional Core

One sentence: what must be communicated above all else? Not the topic — the feeling. Examples: love ("I need you to know what you changed in me"), condolence ("Your grief is witnessed"), apology ("I understand the specific harm I caused").

### 1.2 Calibrate the Relationship

Record: **intimacy** (strangers / acquaintances / friends / intimate / family), **power dynamic** (peer / sub-to-superior / superior-to-sub / mentor-mentee), **history** (long / recent / first contact), **current state** (strong / strained / broken / reconnecting).

### 1.3 Determine Voice

The letter must sound like the **sender**, not the writer.

**If writing samples provided** — analyze and extract:
1. Tone: formal vs. casual, warm vs. reserved, direct vs. circumspect
2. Cadence: sentence length patterns, fragments vs. complete sentences
3. Vocabulary: characteristic words, pet expressions, verbal tics ("anyway," "the thing is")
4. Emotional expression: direct ("I miss you") or indirect ("The house is quiet without you")?
5. Structural habits: long blocks? Staccato? Postscripts? Circling back?

Write a 2-3 sentence **voice profile** with 5+ distinctive markers.

**If no samples** — construct voice from context (age, background, relationship, occasion).

### 1.4 Save Plan

For a single letter: save a brief plan (emotional core, voice profile, relationship calibration, arc). No formal outline needed.

For letter series or epistolary collections: save full outline to `/mnt/agents/output/{filename}.agent.outline.md`.

---

## Stage 2: Writing — Single Subagent (mandatory)

A letter is one person's voice. **One writer. Never split.**

For letter collections: **strictly one letter per `task` call.**

### Create `letter_writer`

`create_subagent`:
- `name`: `"letter_writer"`
- `system_prompt`: Inline all of the following — (1) **Sender voice profile** (from Stage 1): the 2-3 sentence profile plus all markers. If from samples, include specific examples of the sender's phrasing. (2) **Relationship context**: intimacy, power dynamic, history, current state. (3) **Anti-AI rules** — read `../anti-ai.md` and inline full content. For letters, especially emphasize: no template language ("I wanted to take a moment to express..."), no generic superlatives (show WHY, don't claim), specificity required (concrete memories beat "I cherish our time"), no copula avoidance ("It was good to see you" not "Seeing you brought warmth"), no rule-of-three forcing, imperfection is a feature (asides, unresolved feelings). (4) **Letter conventions**: salutation and closing carry meaning. 亲爱的 vs. 尊敬的; Dear vs. Dearest. Choose deliberately, not by template.
- `description`: "Write letter in sender's authentic voice"

### Dispatch via `task`

`task`:
- `agent`: `"letter_writer"`
- `prompt` content:
- The emotional core (one sentence)
- Occasion and context
- Specific details to include: shared memories, inside references, concrete moments the sender would remember
- Length guidance (letters are rarely > 1500 words; most are 300-800)
- Format: date / salutation / body / closing / signature (adjust for medium)
- Medium conventions (if email: subject line, front-load purpose, shorter paragraphs, sign-off carries meaning)
- Output path: `/mnt/agents/output/{filename}_sec01.md`

After each letter completes, orchestrator runs word count verification:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, return to writer with expansion instructions.

---

## Stage 3: Review

### Step 1: Shared Pipeline

Read `../review.md`. For a single letter, skip `continuity_editor`. Run `style_editor` (AI-pattern scan, voice consistency, rhythm) and `structural_editor` (arc: opening connection → core → closing feeling).

### Step 2: Genre-Specific Editors

#### `tone_editor`

`create_subagent`:
- `name`: `"tone_editor"`
- `system_prompt`: "You are a tone editor for letters. Check: (1) occasion appropriateness, (2) formality match for the relationship, (3) emotional calibration — overwritten or underwritten? (4) medium-appropriate tone. Output: PASS/FAIL + specific feedback."
- `description`: "Tone and occasion appropriateness review"

`task`:
- `agent`: `"tone_editor"`
- `prompt`: Include letter file path, relationship calibration from Stage 1, occasion type, medium.

#### `authenticity_editor`

`create_subagent`:
- `name`: `"authenticity_editor"`
- `system_prompt`: "You are an authenticity editor for letters. Primary test: the template test — change sender and recipient names; if the letter still works, it is a TEMPLATE — FAIL. Also check: (1) specificity — 2-3+ concrete details, (2) AI-pattern scan — template openings, significance inflation, copula avoidance, rule-of-three, (3) imperfection — human texture present? (4) voice consistency through emotional shifts. Output: PASS/FAIL + template test result + specific feedback."
- `description`: "Authenticity and template-detection review"

`task`:
- `agent`: `"authenticity_editor"`
- `prompt`: Include letter file path, sender voice profile, anti-AI rules from `../anti-ai.md`.

### Scoring

| Dimension | Weight | What to Check |
|-----------|--------|---------------|
| Tone appropriateness | 25% | Matches relationship and occasion? |
| Authenticity | 25% | Real person, not a template? Specific details? |
| Emotional impact | 20% | Achieves the emotional core? |
| Sender voice fidelity | 20% | Sounds like the sender? Passes interleaving test? |
| Convention compliance | 10% | Salutation, closing, format correct for type/medium? |

**Pass**: >= 75 overall. **Authenticity must be >= 70.**

On FAIL: write a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh `letter_writer` subagent to apply the fix → re-review. Max 2 cycles. If still failing after 2 cycles, deliver with annotated issues for the user.

---

## Stage 4: Delivery

### Convert to .docx

Convert the final letter to Word using the `md2docx` pipeline (see `skills/docx/SKILL.md` → `references/md2docx-reference.md`).

Output: `/mnt/agents/output/{filename}.agent.final.docx`

**This step is mandatory.** Raw .md without a .docx deliverable is not an acceptable end state.

---

## Occasion-Specific Notes

| Occasion | Core Principle | Pitfalls to Avoid |
|----------|---------------|-------------------|
| Love letter (情书) | Be vulnerable and specific | Being generic; being too literary; AI-perfect emotion |
| Condolence (悼念/慰问) | Witness the grief — don't fix it | Platitudes ("they're in a better place"); making it about yourself |
| Apology (道歉信) | Take responsibility for specific actions | Apologizing for the other's feelings; over-explaining; conditional apology |
| Thank-you (感谢信) | Name the specific kindness and its impact | Being generic; being perfunctory |
| Farewell (告别信) | Be honest and gentle | Melodrama; not actually saying goodbye |
| Application (求职信) | Evidence of fit — show, don't claim | Generic claims; no research on recipient; sycophancy |

---

## Reference Files

| File | Purpose | When to Read |
|------|---------|--------------|
| [../anti-ai.md](../anti-ai.md) | AI patterns to avoid — inline into `letter_writer` system prompt | Before Stage 2 |
| [../review.md](../review.md) | Shared review pipeline, editor definitions, quality gates | Before Stage 3 |
| [../scripts/check_wordcount.py](../scripts/check_wordcount.py) | Word count verification | After each section completes — Orchestrator runs directly |
| [../SKILL.md](../SKILL.md) | Parent skill — shared principles, routing, file naming | On entry |
