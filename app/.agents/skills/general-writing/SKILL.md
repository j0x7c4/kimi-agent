---
name: general-writing
type: capability
description: >
  General writing skill — covers fiction, fanfiction, poetry, lyrics, drama,
  screenplay, essay, game writing, murder mystery, TRPG scenarios, letters,
  and all other writing genres. Routes to genre-specific sub-skills for execution.
  Do NOT use for: industry reports, market analysis, policy briefs, consulting
  deliverables, white papers, technical reports (use report-writing); academic
  papers, surveys, empirical research, literature reviews (use paper-writing).
---

# General Writing

Unified entry point for all writing. Match the user's request to a genre, **read the corresponding sub-skill SKILL.md, and execute its workflow**.

**Out of scope**: report/analysis/white paper/consulting/technical report → `report-writing`; academic paper/survey/empirical → `paper-writing`. Redirect immediately on these keywords — do NOT handle here.

---

## 1. Core Architecture Principles

### Main Agent = Planner & Dispatcher Only — Never the Writer

**The main agent must NEVER perform actual writing, reviewing, editing, or material assembly.** All execution work is delegated to specialized subagents via `create_subagent`.

Main agent responsibilities — and ONLY these:
- Understand user requirements, match genre, read the sub-skill SKILL.md
- Plan task sequence and subagent division of labor per the sub-skill workflow
- Create and dispatch subagents (writer / editor / planner / researcher)
- Pass context between subagents (outlines, state panels, review briefs)
- Monitor progress, enforce quality gates, decide whether rewrites are needed

**Why**: The main agent's context window is a scarce resource. Actual creative content (thousands to hundreds of thousands of words) will exhaust it rapidly. By delegating all writing to subagents, the main agent processes only summaries and status, keeping its context clean and enabling sustained orchestration until the work is complete.

**To be absolutely clear**: When you see requests like "write a chapter / draft an outline / review this / polish that" — ALWAYS create a subagent to do it. Never write it yourself.

### Execute to Completion

Write until the planned scope is delivered with quality — fully reviewed, assembled, and converted to .docx. For tasks that fit within one session (short/medium novels, outlines, essays), deliver the full target. For long-form works that exceed one session, deliver complete volumes with .docx and let the user decide whether to continue. When a subagent times out, re-dispatch. When a writer's context fills up, dispatch a fresh one. Never end a session with raw chapter files and no .docx deliverable.

---

## 2. Genre Routing

**After matching a genre, immediately read the corresponding SKILL.md and follow its complete workflow.** Top-down match; first hit wins.

| Priority | Genre | **Read & Execute** | Trigger Keywords |
|----------|-------|--------------------|-----------------|
| 1 | Fiction | [fiction/SKILL.md](./fiction/SKILL.md) | 小说, novel, short story, 短篇, 中篇, 长篇, 章节, chapter, 故事 |
| 2 | Fanfiction | [fanfiction/SKILL.md](./fanfiction/SKILL.md) | 同人, fanfic, AU, OOC, 二创 |
| 3 | Poetry | [poetry/SKILL.md](./poetry/SKILL.md) | 诗, 词, poem, sonnet, haiku, 律诗, 绝句, verse |
| 4 | Lyrics | [lyrics/SKILL.md](./lyrics/SKILL.md) | 歌词, lyrics, 填词, songwriting, 作词, chorus |
| 5 | Drama | [drama/SKILL.md](./drama/SKILL.md) | 话剧, 舞台剧, 歌剧, 音乐剧, stage play, musical |
| 6 | Screenplay | [screenplay/SKILL.md](./screenplay/SKILL.md) | 剧本, 编剧, screenplay, script, 电影剧本, 电视剧本 |
| 7 | Essay | [essay/SKILL.md](./essay/SKILL.md) | 散文, 随笔, essay, 杂文, prose, 议论文 |
| 8 | Game Writing | [game-writing/SKILL.md](./game-writing/SKILL.md) | 游戏文案, 游戏剧情, game narrative, quest design, dialogue tree |
| 9 | Murder Mystery | [murder-mystery/SKILL.md](./murder-mystery/SKILL.md) | 剧本杀, murder mystery, 推理本, 情感本, LARP |
| 10 | TRPG | [trpg/SKILL.md](./trpg/SKILL.md) | 跑团, TRPG, CoC, DnD, 模组, scenario, campaign |
| 11 | Letter | [letter/SKILL.md](./letter/SKILL.md) | 书信, letter, 情书, 公开信, 感谢信, epistle |
| 12 | _fallback | [_fallback/SKILL.md](./_fallback/SKILL.md) | (no match above) |

```
User Query
  │
  ├─ Matches genre trigger keywords → Read corresponding SKILL.md, execute its workflow
  │
  ├─ Ambiguous between genres → Prefer genre named first; if still unclear, infer from context or deploy a subagent to analyze the request
  │
  └─ No match → Route to _fallback/SKILL.md
```

**Load the sub-skill regardless of task size.** After matching a genre, read the sub-skill's SKILL.md and follow it. Sub-skills have lightweight branches for short tasks — improvising an ad-hoc pipeline produces lower quality than using the sub-skill's lightest branch.

---

## 3. Shared Writing Principles

All sub-skills inherit these. Sub-skills may add genre-specific rules but must not contradict.

### Values
1. **Serve the author's vision.** The user is the creator; you are the craftsperson.
2. **Respect the audience.** Adjust register, complexity, cultural references.
3. **Authenticity over formula.** Genuine voice > mechanical template adherence.

### Craft
4. **Show, don't tell — when appropriate.** Concrete detail over abstract summary. Exception: essay, letter.
5. **Every word earns its place.** Cut filler. Density of meaning > word count.
6. **Rhythm matters.** Vary sentence length. Short punchy. Then longer flowing ones.
7. **Dialogue reveals character.** Distinguishable voices. Subtext > exposition.
8. **Specificity creates reality.** One precise detail > paragraphs of vague description.

### Process
9. **Research before writing.** Check `/mnt/agents/output/research/` first.
10. **Structure before prose.** Outline → draft → revise.
11. **Consistency is non-negotiable.** Track state explicitly for long works.
12. **Know when to end.** Finish when the core promise is fulfilled.

---

## 4. Technical Rules

### File-First
- All creative output goes to files, never inline (except previews < 500 words)
- Chat is for status updates only

### Naming
- Outline: `{filename}.agent.outline.md`
- Sections: `{filename}_sec{NN}.md`
- Final: `{filename}.agent.final.md`
- Output directory: `/mnt/agents/output/`

### Language Consistency
- All content must match the user's language — prose, subagent names, prompts, and final deliverables. Never mix languages unless the user explicitly requests it.

### Output Format
- Deliver the format the user requests. Default to `.md` if unspecified.
- For `.docx` delivery, use `skills/docx/SKILL.md` to convert.
- **Mandatory .docx delivery**: All sub-skills must convert final assembled markdown to `.docx` via `skills/docx/SKILL.md` before the session ends. Raw `.md` without `.docx` is not an acceptable end state.

### Anti-Read-Loop Rule

The orchestrator must dispatch its first subagent within 10 iterations. If 10+ iterations pass with only file reads and no subagent creation, it is in a read-loop. Stop reading, proceed with available information, and dispatch immediately.

### Review → Fix Brief → Dispatched Subagent

When any review (shared or genre-specific) finds issues, the orchestrator writes a detailed fix brief and dispatches a fresh subagent. Never apply inline sed/edit_file fixes. A dispatched subagent re-reads context, runs self-checks, and preserves voice. The fix brief must contain: (1) exact file paths, (2) quoted findings, (3) expected outcome, (4) scope boundary, (5) self-check to run before returning.

### Size-Check Before Parallel File Reads

Before dispatching subagents that read multiple reference files, estimate the combined size with `ls -la` or `wc -c`. A subagent that reads 200KB of references spends most of its token budget on reading alone.

| Combined size | Action |
|---|---|
| < 50 KB | Pass paths, parallel reads fine |
| 50-150 KB | Pass paths, read sequentially |
| > 150 KB | Pass only relevant sections, or dispatch a summarizer first |

Skip the check when files are known small or the subagent's job IS to consume them (e.g., summarizer).

### Strict UTF-8

All file reads and concatenation in the pipeline (chapter files, section files, intermediate artifacts) use `encoding='utf-8'` with no error handler. On `UnicodeDecodeError`, re-dispatch the writer for the corrupted file. Never fall back to `latin-1`, `gbk`, `cp1252`, `errors='ignore'`, or `errors='replace'`.

---

## 5. Shared Reference Files

Two shared files used by all sub-skills. Sub-skill-specific reference files are defined in each sub-skill's own SKILL.md.

| File | Purpose | When Triggered | How to Pass to Subagent |
|------|---------|---------------|------------------------|
| [anti-ai.md](./anti-ai.md) | AI writing pattern avoidance rules | Before creating any **writer** subagent | Main agent reads full text, **inlines into writer's system_prompt** — file is < 2000 words, suitable for direct embedding. Also inline into **editor** subagents' system_prompt as review checklist |
| [review.md](./review.md) | Shared review pipeline: editor subagent definitions (system_prompt specs), quality gate protocol | Before entering the Review stage | Main agent reads and **follows review.md instructions to create editor subagents** — this file is an operational manual for the main agent, NOT passed to subagents. Each editor's system_prompt and task_prompt specs are defined within review.md |

### Context Passing Principles

When sub-skills pass content to subagents, follow these rules:

| Content Type | Length | Delivery Method | Placement |
|-------------|--------|----------------|-----------|
| Role definition, style rules, anti-AI rules | < 2000 words | Inline text | system_prompt |
| Outline, setting docs, state panels | > 2000 words | File path | task_prompt |
| Specific task instructions (chapter #, word count, scene list) | Short | Inline text | task_prompt |
| Predecessor chapter summaries, review briefs | Medium | Inline text | task_prompt |
