---
name: essay
type: capability
description: >
  Essay and prose writing — personal essays, literary essays, argumentative essays,
  随笔, 杂文, and other non-fiction prose that prioritizes voice, thought, and
  style over formal structure. Distinguished from reports (data-driven) and papers
  (academic rigor).
---

# Essay Writing

Orchestrator dispatches all creation and review work to subagents. Before creation, copy user-uploaded files to `/mnt/agents/output/research/`.

Sub-skill of [general-writing](../SKILL.md). Inherits shared creative writing principles, anti-AI discipline, and quality gate framework.

> **CRITICAL — Review → Fix Brief → Dispatched Subagent**: When a review finds issues, translate them into a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh `essay_writer` subagent to apply the fix. Never use inline sed/edit_file fixes.

> **CRITICAL — Anti-Read-Loop Rule**: The orchestrator must dispatch its first subagent (essay_writer) within 10 iterations. If the orchestrator has spent 10+ iterations only reading files without creating any subagent, it is in a read-loop. Stop reading, draft your conception from what you have, and dispatch the writer immediately.

> **CRITICAL — .docx Delivery**: Every completed essay must be converted to .docx using `skills/docx/SKILL.md`. Never end a session with raw .md files and no .docx deliverable.

## File Paths

```
Output: /mnt/agents/output/
  {project_name}.essay.md               # Final essay
  research/                              # User uploads (source material, references)
```

## Trigger Keywords

散文, 随笔, essay, personal essay, 杂文, prose, 小品文, 议论文, 抒情散文, 叙事散文, op-ed, 评论, commentary, reflection, thought leadership, 洞见, insight essay, 公众号文章, 小红书

---

## Workflow Decision Tree

```
User Query
  │
  ├─ Provides draft + asks for revision → Stage 3 → Stage 4
  ├─ Specifies type/theme clearly → Stage 1 → Stage 2 → Stage 3 → Stage 4
  └─ Vague request → Infer parameters (see below) → Stage 1 → Stage 2 → Stage 3 → Stage 4
```

Infer essay type, audience, platform, length, and language from the user's request. The orchestrator analyzes and infers all parameters autonomously; for complex requests, deploy a subagent to analyze requirements in depth. Never prompt the user for clarification.

---

## Stage 1: Conception (Orchestrator — no subagents)

The Orchestrator designs the essay structure directly. Do not delegate this.

### 1.1 Identify the Central Claim

Not the topic — the **claim**. One sentence: what does this essay argue or reveal?

### 1.2 Find "The Turn"

The moment where thinking deepens or complicates. Identify explicitly: what does the reader believe before? What do they understand after? For insight essays: this is the **cognitive gap** — "Many think X, but the evidence points to Y."

### 1.3 Determine Voice

Record: **formality** (conversational / measured / formal / literary), **use of "I"** (frequent / occasional / rare), **humor** (none / dry wit / satirical / self-deprecating), **rhythm** (short-punchy / long-flowing / varied), **critical intensity** (observer / commentator / provocateur).

### 1.4 Choose Structure

**For insight/thought-leadership essays (Chinese tradition)**:
1. 破题 — Reframe the topic so the reader sees it fresh
2. 拆解 — Pull the topic apart; reveal hidden mechanisms
3. 破局 — The insight itself; the "turn" at maximum intensity
4. 升华 — Lift the specific insight to a broader principle

**For personal/narrative essays**:
- Hook → Setup → Complication → The Turn → Landing (resonant close, not summary)

**For thought leadership**: additionally plan content mix —
| Type | Share | Purpose |
|------|-------|---------|
| Data-driven analysis | 40% | Anchor in evidence |
| Tactical frameworks | 30% | Actionable mental models |
| Contrarian takes | 20% | Challenge received wisdom |
| Personal narrative | 10% | Selective vulnerability |

Identify 2-3 candidate **concluding aphorisms** using concrete structures: (1) **Juxtaposition** — three escalating levels: "X改变结果, Y改变原因, Z改变模型"; (2) **Contrast** — negate + affirm: "不是A, 而是B"; (3) **Causal loop** — "A导致B, B导致C, C加剧A"; (4) **Negation flip** — "XXX的本质, 其实不是…而是…" Pick structure before drafting; test by reading aloud.

### 1.5 Outline

**For short essays (< 3k words):** Save a single outline to `/mnt/agents/output/{filename}.agent.outline.md`. Include: central claim, the turn, voice profile, structural arc, platform conventions (if any).

**For long essays (>= 3k words):** Two-phase outline process:
1. **Structural outline** — Central claim, the turn, section purposes, and overall arc. Save to `/mnt/agents/output/{filename}.agent.outline.md`.
2. **Per-section detail outline** — For each section: the section's argument, key evidence or examples, transitions into and out of the section, and target word count. Append to the same outline file.

---

## Stage 2: Writing — Single Subagent (mandatory)

Voice unity is paramount. **One writer for the entire essay. Never split.**

For multi-section essays: **strictly one section per `task` call.** Single writer mandatory for voice unity — reuse the same `essay_writer` subagent.

### Create `essay_writer`

`create_subagent`:
- `name`: `"essay_writer"`
- `system_prompt`: Inline all of the following — (1) **Voice profile** (from Stage 1) — be specific: "conversational, dry wit, varied rhythm with short declaratives after long analytical passages, frequent first-person, provocateur stance." (2) **Anti-AI rules** — read `../anti-ai.md` and inline full content. CRITICAL for essays. Emphasize: no throat-clearing, no summarizing endings, no transition chains, no soulless neutrality, no copula avoidance, no significance inflation. Chinese essays: "形散神不散." (3) **Platform conventions** if targeting a venue (see Platform Variants below).
- `description`: "Write essay with consistent voice"

### Dispatch via `task`

`task`:
- `agent`: `"essay_writer"`
- `prompt` content:
- The outline (full text, not path)
- Central claim and "the turn" specification
- For insight essays: the 4-part arc (破题→拆解→破局→升华) and the cognitive gap
- For thought leadership: content mix targets and aphorism candidates
- Word count target
- Audience description
- Output path: `/mnt/agents/output/{filename}_sec{NN}.md`

### Word Count Verification

After each completed section, orchestrator runs:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, return to writer with expansion instructions.

---

## Stage 3: Review

### Step 1: Shared Pipeline

Read `../review.md` and run the shared review pipeline. For single-section essays, `continuity_editor` is skipped; run `style_editor` and `structural_editor`.

### Step 2: Genre-Specific Editor — `voice_editor`

`create_subagent`:
- `name`: `"voice_editor"`
- `system_prompt`: "You are a voice editor for essays. The cover test: remove the byline — would you know a human wrote this? Check: (1) voice distinctiveness, (2) opinions and risk-taking, (3) AI-pattern scan, (4) rhythm variety, (5) authenticity (mixed feelings, imperfection). Output: score 0-100 for voice distinctiveness + PASS/FAIL + line-level feedback."
- `description`: "Voice distinctiveness and authenticity review"

`task`:
- `agent`: `"voice_editor"`
- `prompt`: Include essay file path, anti-AI rules (from `../anti-ai.md`), voice profile from Stage 1.

**Scoring**:

| Dimension | Weight | What to Check |
|-----------|--------|---------------|
| Voice distinctiveness | 25% | Sounds like a specific person? |
| Central insight clarity | 25% | Reader can state "the point"? |
| Structural arc | 20% | Hook, turn, resonant landing? |
| Argument quality | 15% | Logic, evidence, emotional honesty? |
| Craft and editing | 15% | AI-pattern absence, rhythm, transitions? |

**Pass**: >= 75 overall. **Voice distinctiveness must be >= 70.**

On FAIL: remediation brief → dispatch a fresh `essay_writer` subagent to apply the fix → re-review. Max 2 cycles. If still failing after 2 cycles, deliver with annotated issues for the user.

---

## Stage 4: Delivery

### Assemble

For multi-section essays, concatenate all section files in order. Save to `/mnt/agents/output/{filename}.agent.final.md`.

### Convert to .docx

Convert the assembled markdown to Word using the `md2docx` pipeline (see `skills/docx/SKILL.md` → `references/md2docx-reference.md`).

Output: `/mnt/agents/output/{filename}.agent.final.docx`

**This step is mandatory.** Raw .md without a .docx deliverable is not an acceptable end state.

---

## Platform Variants

| Platform | Key Conventions |
|----------|----------------|
| 微信公众号 | Insight first. Emotional hook in line 1. Bold key sentences. Short paragraphs (2-4 sentences). |
| 小红书 | Ultra-short paragraphs (1-2 sentences). Emoji as rhythm (not decoration). "I" mandatory. Hook in first 2 lines. **Anti-AI checklist**: no "首先/其次/最后" structure, no "值得注意的是/综上所述", no uniform paragraph lengths, no missing emotional markers. Replace "赋能" → "帮", "值得注意的是" → "说真的". Post-write check: warm greeting opener? personal voice? sentence length varied? interaction CTA at end? |
| Blog / Newsletter | SEO-aware title. Skimmable (H2/H3, pull quotes, bold). 2000-5000 words. Author bio. |
| Literary Magazine | Pure voice — no SEO, no hooks. Sentence-level craft. Ambiguity welcome. |

---

## Reference Files

| File | Purpose | When to Read | Who Runs |
|------|---------|--------------|----------|
| [../anti-ai.md](../anti-ai.md) | AI patterns to avoid — inline into `essay_writer` system prompt | Before Stage 2 | Orchestrator inlines into subagent |
| [../review.md](../review.md) | Shared review pipeline, editor definitions, quality gates | Before Stage 3 | Orchestrator follows |
| [../SKILL.md](../SKILL.md) | Parent skill — shared principles, routing, file naming | On entry | Orchestrator reads |
| [../scripts/check_wordcount.py](../scripts/check_wordcount.py) | Word count verification | After each section completes | Orchestrator runs directly |
