---
name: drama
type: capability
description: >
  Stage drama writing — plays, operas, musicals, and other works intended for live
  theatrical performance. Handles dialogue, stage directions, act/scene structure,
  dramatic tension, and the unique constraints of the live stage.
---

# Drama Writing

Sub-skill of [general-writing](../SKILL.md). Inherits shared creative writing principles, anti-AI discipline, and quality gate framework.

> **CRITICAL — Writing Dispatch Rule**: Acts are sequential by nature (each act builds on prior dramatic tension) — dispatch one drama_writer per act and wait for completion before the next. Exception: within a musical act, book-writer and lyricist CAN run in parallel, then merge before review. Reviews (shared + genre editors) always run non-blocking alongside the next act's writing.

> **CRITICAL — Review → Fix Brief → Dispatched Subagent**: When a review finds issues, translate them into a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh subagent to apply the fix. Never use inline sed/edit_file fixes — dispatched subagents re-read context, run self-checks, and preserve voice.

> **CRITICAL — Anti-Read-Loop Rule**: The orchestrator must dispatch its first subagent (drama_planner or drama_writer) within 10 iterations. If the orchestrator has spent 10+ iterations only reading files without creating any subagent, it is in a read-loop. Stop reading, write your plan from what you have, and dispatch immediately.

> **CRITICAL — Step Budget & Delivery**: You have a limited step budget. Plan delivery accordingly:
> - **Short plays (one-act, sketch)**: fully achievable in one session. Write, review, assemble, convert to .docx.
> - **Multi-act plays / musicals**: plan to deliver all acts per session with full quality (review + assembly + .docx).
> - **Before your session ends**: always assemble whatever acts are done and convert to .docx — never end with only raw act files.

## Trigger Keywords

话剧, 舞台剧, 歌剧, 音乐剧, stage play, opera, musical, theatre, theater, 独幕剧, one-act, 小品, sketch, 戏剧

## File Paths

### Output Directory Structure

```
/mnt/agents/output/
├── research/                    # User uploads (reference plays, venue specs)
├── {project_name}.outline.md
├── {project_name}.final.md
├── documents/
│   ├── {project_name}.characters.md
│   └── {project_name}.props_costumes.md
└── acts/
    └── {project_name}.act{N}.md
```

### User-Uploaded Files

Before Stage 1, copy all user-uploaded files (reference plays, venue specs, cast lists, set photos) to `/mnt/agents/output/research/`. Preserve original filenames. Reference these copies (not originals) in all subagent task prompts — subagents may run in sandboxed environments without access to the original paths.

---

## Scope Inference

Infer medium, genre, format, length, tone, era/setting from the user's request. The orchestrator analyzes and infers all parameters autonomously; for complex requests, deploy a subagent to analyze requirements in depth. Never prompt the user for clarification.

---

## Stage 1: Outline

### Subagent: `drama_planner`

`create_subagent`:
- `name`: `"drama_planner"`
- `system_prompt`: "You are a drama planner specializing in theatrical structure. You design act/scene breakdowns, character webs, and satisfaction-element mappings for stage plays, musicals, and operas. You understand performability constraints (cast size, set changes, timing) and build outlines that are production-feasible."
- `description`: "Design theatrical outline with act/scene structure and satisfaction elements"

`task`:
- `agent`: `"drama_planner"`
- `prompt` must include:
- Inferred scope (form, cast size, acts, tone, theme, staging constraints)
- Satisfaction element library (see below) — instruct planner to select 3-5 and map to act phases
- Comeback path table (if applicable) — instruct planner to select one primary path and define 4-6 milestone beats
- For musicals/opera: instruct planner to identify song placements with dramatic function

**Planner deliverables** (saved to `/mnt/agents/output/{project_name}.outline.md`):

#### Phase 1 — Macro Outline
1. **Story arc**: logline, synopsis, thematic statement, overall dramatic trajectory
2. **Act structure**: number of acts, dramatic question per act, act break design
3. **Character list**: name, role, relationships, arc, voice traits, wants/obstacles/change, motivated entrances/exits
4. **Satisfaction elements selected** (3-5) with act-phase payoff map: setup plants deficit → build teases/delays → payoff delivers release
5. **Comeback path milestones** (if applicable)
6. **Performability pre-check**: cast count vs tier, set change levels, timing estimate
7. For musicals: song list with placement and dramatic function ("I Want" song, eleven o'clock number, reprises)

#### Phase 2 — Micro Outline
8. **Per-act scene breakdown**: scene-by-scene detail including dramatic question, characters present, entrance/exit motivations, emotional arc, timing estimate
9. **Entrance/exit chart**: per scene, who enters, who exits, motivation for each
10. **State panels initialized**: Characters (onstage/offstage per scene), Plot Threads, Timeline, Props

The macro outline is reviewed and locked before the micro outline begins. The micro outline feeds directly into writer task prompts.

### Satisfaction Element Library

| Element | Examples |
|---------|----------|
| **Inspirational / 励志奋斗** | Underdog triumph, mentor sacrifice, comeback from humiliation |
| **Truth, Goodness, Beauty / 真善美** | Hidden kindness revealed, costly forgiveness, integrity under pressure |
| **Emotional / 情感** | Reunion after separation, parent-child reconciliation, sacrifice understood late |
| **Catharsis / 爽感** | Power reversal, villain undone by hubris, long-planted secret detonates |

**Mapping rule**: At least one element pays off per act break; the strongest at climax. Never front-load all satisfaction into Act 1.

---

## Stage 2: Writing

### Dispatch Strategy

**Strictly one act per `task` call.** Multi-act dispatch causes the model to cut corners. No exceptions.

- **One-act / sketch**: single writer agent
- **Multi-act**: one writer agent per act, dispatched sequentially (each act depends on prior)
- **Musical**: parallel book-writer + lyricist per act, then merge

### Non-Blocking Review (Multi-Act Works)

When an act finishes writing and passes word count, dispatch review subagents for that act AND start writing the next act simultaneously. Reviews run in the background — only dispatch fixes when a review finds issues. This maximizes throughput by never blocking writing on review.

```
Act K:  [Write] → [WC check] ──→ Act K+1 writing starts immediately
                       └──→ [Review Act K in background]
                                    └──→ [Fix if needed, also in background]
```

### Word Count Verification

After each act is delivered, the orchestrator runs:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If the check returns FAIL, return the file to the writer with expansion instructions specifying which scenes are underweight.

### Subagent: `drama_writer` (one per act)

`create_subagent`:
- `name`: `"drama_writer"`
- `description`: "Write one act of stage drama from outline spec"
- `system_prompt`: "You are a drama writer for live stage performance.

DIALOGUE CRAFT:
- Every exchange carries subtext: said (literal words), meant (speaker's intent),
  understood (what audience reads from context). Minimum 3 exchanges per scene where
  all three layers are distinct. Climactic scenes: every exchange carries subtext.
- Speakability: write lines meant to be spoken aloud. Flag breath-requiring mid-clause
  sentences, tongue-tripping clusters, 3+ consecutive lines of similar cadence.
- Exposition through conflict only. Secrets revealed to wound; arguments about the past
  that reveal it through disagreement. FORBIDDEN: 'As you know' dialogue; characters
  whose sole function is exposition delivery.
- Silence is a tool: use (beat), (pause), (a long silence), action-replaces-reply.
  At least one significant silence per scene.

STAGE DIRECTIONS:
- Minimal and functional. Describe only what the audience must see.
- Over-direction insults collaborators. No emotional adjectives on directions.
- Every entrance and exit must be motivated; 'the plot needs them' is not motivation.

PERFORMABILITY CONSTRAINTS:
- Respect cast size tier: [Orchestrator fills from outline]
- Max 2 Level-3 set changes per act (Level 3 = major pieces, turntable, 1-3min)
- Quick-changes <90s must specify velcro/snap closures and offstage change location
- Timing targets: Act 1 40-55min, Act 2 35-50min, one-act 30-90min, sketch 8-20min

FORMAT:
ACT [N]
Scene [N]: [Location]
[Stage directions in brackets]

CHARACTER NAME
(parenthetical — sparingly)
Dialogue text.

[Stage direction — action, movement, lighting cue]

[INLINE anti-ai.md CONTENT HERE — Orchestrator reads ../anti-ai.md and pastes full content]"

`task` (one call per act):
- `agent`: `"drama_writer"`
- `prompt` must include:
1. Act assignment (which act number, scene range)
2. Outline excerpt for this act (from the outline file)
3. Character profiles with voice traits
4. Satisfaction elements mapped to this act and their target payoff moments
5. Continuity state from predecessor act:
   - Who is onstage at end of prior act
   - What each character knows (information asymmetry / dramatic irony state)
   - Unresolved plot threads carrying forward
   - Prop tracking state (which objects are where)
6. Predecessor act summary (for Act 2+): 1-2 paragraph summary of prior act events and emotional arc
7. For musicals: song placements in this act with dramatic function
8. Word count / timing target for this act

---

## Stage 3: Review

**Read [../review.md](../review.md) before this stage.**

Run the shared review pipeline first (continuity_editor → style_editor → structural_editor), then add genre-specific editors:

### Genre-Specific Editor 1: `performability_editor`

`create_subagent`:
- `name`: `"performability_editor"`
- `system_prompt`: "You are a performability editor for stage drama. You assess whether a script can be physically produced within its stated constraints. You check cast size vs budget tier, set change count/complexity, quick-change feasibility, technical requirements, and running time estimates. Output: PASS or FAIL with specific issues."
- `description`: "Verify script is physically producible within staging constraints"

`task`:
- `agent`: `"performability_editor"`
- `prompt` must include:
- All act files
- Outline (cast size tier, staging constraints, timing targets)
- Checklist: cast count vs tier, set change levels per act (max 2 Level-3), quick-change flags (<90s), technical requirements rated Basic/Intermediate/Advanced, running time estimate per act + total

### Genre-Specific Editor 2: `dialogue_editor`

`create_subagent`:
- `name`: `"dialogue_editor"`
- `system_prompt`: "You are a dialogue editor for stage drama. You audit subtext layers (said/meant/understood), speakability, voice distinctiveness across characters, exposition management, silence usage, and AI-pattern absence. Output: PASS or FAIL with line-level feedback."
- `description`: "Audit dialogue quality: subtext, speakability, voice distinction"

`task`:
- `agent`: `"dialogue_editor"`
- `prompt` must include:
- All act files
- Character voice profiles from outline
- Anti-AI rules (inline from `../anti-ai.md`)
- Checklist: subtext layer audit (minimum 3 distinct-layer exchanges per scene), speakability read-aloud test, voice distinctiveness between characters, silence audit (flag 2+ unbroken dialogue pages), exposition-through-conflict check, AI-pattern scan

### Genre-Specific Editor 3: `dramatic_tension_editor`

`create_subagent`:
- `name`: `"dramatic_tension_editor"`
- `system_prompt`: "You are a dramatic tension editor. You verify per-scene dramatic questions, tension arc build across acts, act break placement, satisfaction element tracking, motivated entrances/exits, and the 'so what' test for every scene. Output: PASS or FAIL with specific issues."
- `description`: "Verify dramatic tension arcs, act breaks, and satisfaction element payoffs"

`task`:
- `agent`: `"dramatic_tension_editor"`
- `prompt` must include:
- All act files
- Outline with satisfaction element map and act structure
- Checklist: per-scene dramatic question identified, tension arc builds properly, act breaks land at correct moments, satisfaction elements pay off at mapped phases, all entrances/exits motivated, "so what" test per scene

### Scoring

| Dimension | Weight |
|-----------|--------|
| Dialogue quality | 25% |
| Dramatic structure | 20% |
| Performability | 20% |
| Satisfaction delivery | 15% |
| Character arcs | 10% |
| Stage direction quality | 10% |

**Pass**: >= 75 overall. Dialogue >= 70. Performability >= 65.

**On failure**: follow quality gate protocol from `../review.md` — write a detailed fix brief and dispatch a fresh subagent to apply the fix → re-review (max 2 cycles). **Forced pass after 3 total attempts** — remaining issues flagged for user review.

---

## Stage 4: Assembly

Assemble final output including:
1. Cast list with character descriptions
2. Scene breakdown (act/scene, location, characters)
3. Staging notes and technical rider summary
4. Running time estimate (per act + total with intermission: 15-20min)
5. All act scripts concatenated

Save to `/mnt/agents/output/{project_name}.final.md`.

### Convert to .docx

Convert the assembled markdown to Word using the `md2docx` pipeline (see `skills/docx/SKILL.md` → `references/md2docx-reference.md`).

Output: `/mnt/agents/output/{project_name}.final.docx`

**This step is mandatory.** Raw .md without a .docx deliverable is not an acceptable end state.

---

## Core Principles

1. **Orchestrator = coordinator.** Dispatches tasks to subagents, manages state, merges outputs. Never writes dialogue, never reviews content, never runs scripts directly.
2. **One act per `task` call.** Never merge acts into a single dispatch. No exceptions.
3. **Non-blocking review.** For multi-act works, reviews run in the background — writing the next act never waits on review of the current act. Only word count check gates the next dispatch.
4. **Execute to completion.** Once outline is ready, do not pause.
5. **Language follows the user.** Content in user's language. Filenames and metadata in English.

---

## Musical-Specific Additions

When the form is musical (音乐剧) or opera (歌剧), apply these additional rules:

- **Songs must advance plot or deepen character** — if a song is cuttable without story loss, cut it
- **"I Want" song**: early Act 1, protagonist's desire becomes the dramatic engine
- **Eleven o'clock number**: emotional climax near the end, highest-stakes moment
- **Reprises shift meaning**: same melody, changed context = changed emotional weight
- **Song placement in outline**: each song entry must state its dramatic function (not just "emotional moment")
- **Parallel dispatch**: book-writer and lyricist can work simultaneously per act; merge before review

---

## Reference Files

| File | Purpose | When to Read | How to Use |
|------|---------|-------------|------------|
| [../anti-ai.md](../anti-ai.md) | Anti-AI discipline rules | Before creating writer subagents | Inline into `drama_writer` system prompt |
| [../review.md](../review.md) | Shared review pipeline + quality gate protocol | Before Stage 3 | Follow review sequence |
| [../SKILL.md](../SKILL.md) | Parent skill — shared principles, routing, file naming | Reference | Inherit shared conventions |
| [../scripts/check_wordcount.py](../scripts/check_wordcount.py) | Word count verification | After each section completes | Orchestrator runs directly |
