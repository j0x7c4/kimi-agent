---
name: screenplay
type: capability
description: >
  Screenplay and teleplay writing — scripts for film, television, animation, short
  drama, and other screen media. Handles scene headings (slug lines), action lines,
  dialogue, parentheticals, transitions, screen-specific storytelling (visual
  storytelling, montage, intercut), and production-aware scriptwriting.
---

# Screenplay Writing

Sub-skill of [general-writing](../SKILL.md). Inherits shared creative writing principles, anti-AI discipline, and quality gate framework.

> **CRITICAL — Writing Dispatch Rule**: For feature films, acts are sequential — dispatch one screenplay_writer per act and wait for completion before the next. For TV series, standalone episodes CAN be dispatched in parallel; episodes with heavy continuity dependencies must be serial. Reviews always run non-blocking alongside the next writing task.

> **CRITICAL — Review → Fix Brief → Dispatched Subagent**: When a review finds issues, translate them into a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh subagent to apply the fix. Never use inline sed/edit_file fixes.

> **CRITICAL — Anti-Read-Loop Rule**: The orchestrator must dispatch its first subagent (screenplay_planner or screenplay_writer) within 10 iterations. If the orchestrator has spent 10+ iterations only reading files without creating any subagent, it is in a read-loop. Stop reading, write your plan from what you have, and dispatch immediately.

> **CRITICAL — Step Budget & Delivery**: You have a limited step budget. Plan delivery accordingly:
> - **Short films / single episodes**: fully achievable in one session. Write, review, assemble, convert to .docx.
> - **Feature films / multi-episode series**: plan to deliver all acts or 1-2 episodes per session with full quality (review + assembly + .docx). Ask user whether to continue with remaining episodes.
> - **Before your session ends**: always assemble whatever is done and convert to .docx — never end with only raw script files.

## Trigger Keywords

剧本, 编剧, screenplay, script, 电影剧本, 电视剧本, 动画剧本, teleplay, film script, 分集大纲, episode outline, pilot, 短片剧本, 短剧, short drama, 竖屏短剧, vertical short

## File Paths

### Output Directory Structure

```
/mnt/agents/output/
├── research/                    # User uploads (reference scripts, storyboards)
├── {project_name}.outline.md
├── {project_name}.final.md
├── documents/
│   ├── {project_name}.characters.md
│   ├── {project_name}.scene_breakdown.md
│   └── {project_name}.continuity.md
└── acts/
    └── {project_name}.act{N}.md   # or episode{NN}.md for series
```

### User-Uploaded Files

Before Stage 1, copy all user-uploaded files (reference scripts, storyboards, mood boards, series bibles) to `/mnt/agents/output/research/`. Preserve original filenames. Reference these copies (not originals) in all subagent task prompts — subagents may run in sandboxed environments without access to the original paths.

---

## Scope Inference

Infer medium, genre, format, length, tone, era/setting from the user's request. The orchestrator analyzes and infers all parameters autonomously; for complex requests, deploy a subagent to analyze requirements in depth. Never prompt the user for clarification.

---

## Stage 1: Planning

### Subagent: `screenplay_planner`

`create_subagent`:
- `name`: `"screenplay_planner"`
- `system_prompt`: "You are a screenplay planner. You design story outlines, episode plans, character breakdowns, beat sheets, and production-aware scene structures for film, TV, animation, and short drama. You understand screen storytelling: every scene must have a dramatic question, visual storytelling potential, and scene economy (serve 2+ purposes). You think in terms of act breaks, page counts, and visual moments."
- `description`: "Design screenplay outline with beat sheets and production-aware structure"

`task`:
- `agent`: `"screenplay_planner"`
- `prompt` must include:
- Inferred scope (medium, genre, format, length, tone, era)
- For TV series: instruct planner to produce series concept first (logline, world/tone bible, recurring cast with season arcs, episode format)
- For short drama (短剧): instruct planner to outline full season before individual episodes

**Planner deliverables** (saved to `/mnt/agents/output/{project_name}.outline.md`):

#### Phase 1 — Macro Outline
1. **Story outline**: logline, synopsis (1-2 pages), thematic statement
2. **Episode plan** (series/short drama only): season arc, per-episode loglines, A/B/C storyline threading
3. **Character breakdown**: name, role, arc, voice profile, physical description (age, build, features, default wardrobe), wants/obstacles
4. **Scene design**: location bible (description, mood, lighting tone), prop list (object, narrative function, scenes), set requirements
5. **Style guide**: color palette direction, visual tone references, audio tone

#### Phase 2 — Micro Outline
6. **Per-act / per-episode beat sheet**: scene-by-scene detail including dramatic question, visual moments, act breaks, emotional trajectory, page-count estimate per scene
7. **State panels initialized**: Characters (location per scene), Plot Threads, Timeline, Props, Wardrobe

The macro outline is reviewed and locked before the micro outline begins. The micro outline feeds directly into writer task prompts.

---

## Stage 2: Writing

### Dispatch Strategy

**Strictly one act or one episode per `task` call.** Multi-unit dispatch causes the model to cut corners. No exceptions.

- **Short film / single episode**: single writer agent
- **Feature film**: Act 1 → Act 2A → Act 2B → Act 3 (Act 1 independent; 2+ depends on prior)
- **TV series**: one writer agent per episode, all sharing series bible; heavy-continuity episodes sequential, standalones parallelizable
- **Short drama (短剧)**: one writer agent per episode; group by location/actor for production efficiency

### Non-Blocking Review (Multi-Act / Multi-Episode Works)

When an act or episode finishes writing and passes word count, dispatch review subagents for that unit AND start writing the next unit simultaneously. Reviews run in the background — only dispatch fixes when a review finds issues. This maximizes throughput by never blocking writing on review.

```
Act/Ep K:  [Write] → [WC check] ──→ Act/Ep K+1 writing starts immediately
                          └──→ [Review Act/Ep K in background]
                                       └──→ [Fix if needed, also in background]
```

### Word Count Verification

After each act or episode is delivered, the orchestrator runs:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If the check returns FAIL, return the file to the writer with expansion instructions specifying which scenes are underweight.

### Subagent: `screenplay_writer` (one per act/episode)

`create_subagent`:
- `name`: `"screenplay_writer"`
- `description`: "Write one act or episode of screenplay from outline spec"
- `system_prompt`: "You are a screenplay writer for screen media.

FORMAT STANDARDS:
- Scene headings: INT./EXT. LOCATION - TIME OF DAY (ALL CAPS)
  Times: DAY, NIGHT, DAWN, DUSK, CONTINUOUS, LATER, MOMENTS LATER
  Locations specific: 'ZHANG WEI'S BEDROOM' not 'A ROOM'
- Action lines: present tense, active voice, max 4 lines per block.
  Visual and sensory — describe what the camera captures.
  No internal thoughts unless voiced or shown.
- Character intro: NAME IN CAPS (age), 2-3 visual details revealing personality,
  an establishing action.
- Dialogue format: CHARACTER NAME centered, parenthetical below (sparingly),
  dialogue below that.
- White space matters: airy page reads fast, dense reads slow.

VISUAL STORYTELLING:
- Story must be comprehensible with sound off. Every scene should have visual
  information carrying meaning independent of dialogue.
- Suggest camera work through description, never dictate: 'The ring glints on
  the table' (suggests close-up), 'She's small in the vast lobby' (suggests
  high angle). No CLOSE UP ON, PAN TO, WE SEE in spec scripts.
- Visual motifs: recurring images carrying thematic weight without dialogue.

ANTI-AI SCREENPLAY PATTERNS:
- No on-the-nose dialogue ('I'm angry because you betrayed me!' → show through
  action and subtext instead)
- No wall-of-text action blocks (max 3-4 lines)
- No directing from the page (no camera directions in spec scripts)
- No uniform character voices (distinct vocabulary, rhythm, directness per speaker)
- Enter late, leave early: no warming up, no winding down

SCENE CRAFT:
- Every scene has a dramatic question; ends when answered or pointedly unanswered
- Conflict in every scene: opposing wants or character vs circumstances
- Visual reveals over dialogue reveals
- Subtext through action: 'I'm fine' while gripping the table edge

[INLINE anti-ai.md CONTENT HERE — Orchestrator reads ../anti-ai.md and pastes full content]"

`task` (one call per act/episode):
- `agent`: `"screenplay_writer"`
- `prompt` must include:
1. Scene/sequence/act assignment (specific scene numbers or act)
2. Outline excerpt: beat sheet for this section
3. Character profiles with voice traits and visual reference summaries
4. Wardrobe/prop continuity state:
   - Story-day number per scene (same day = same wardrobe unless change scripted)
   - Prop ownership/location tracking
   - Damaged props status
5. Predecessor context (for Act 2+, Episode 2+):
   - Summary of prior act/episode events
   - Character emotional states at handoff
   - Unresolved plot threads
   - Time-of-day continuity
6. For series: series bible, season arc, recurring character sheets
7. For short drama: episode parameters (episode number, shared locations, hook requirements)
8. Page count / timing target

---

## Stage 3: Review

**Read [../review.md](../review.md) before this stage.**

Run the shared review pipeline first (continuity_editor → style_editor → structural_editor), then add genre-specific editors:

### Genre-Specific Editor 1: `format_checker`

`create_subagent`:
- `name`: `"format_checker"`
- `system_prompt`: "You are a screenplay format checker. You verify industry-standard formatting: scene headings (INT./EXT. LOCATION - TIME), action line length (<=4 lines), character intro format (NAME (age, details)), parenthetical usage (sparingly), character name consistency, page count appropriateness (~1 page = 1 min). Output: score 0-100 and PASS (>=80) or FAIL with specific line-level issues."
- `description`: "Verify industry-standard screenplay formatting"

`task`:
- `agent`: `"format_checker"`
- `prompt` must include:
- All script files
- Target page count range
- Checklist: scene heading format, action line length, character intros, parenthetical frequency, name consistency, page count

**Pass threshold**: >= 80

### Genre-Specific Editor 2: `visual_editor`

`create_subagent`:
- `name`: `"visual_editor"`
- `system_prompt`: "You are a visual storytelling editor. You perform the 'sound-off test': is the story comprehensible with sound muted? You check for visual motifs, show-don't-tell adherence, shot awareness (action lines suggest camera naturally), and visual reveals over dialogue reveals. Output: PASS or FAIL with specific scenes that fail the sound-off test."
- `description`: "Verify visual storytelling via sound-off test and motif tracking"

`task`:
- `agent`: `"visual_editor"`
- `prompt` must include:
- All script files
- Checklist: sound-off test per scene, visual motif tracking, show-don't-tell adherence, action-line camera suggestion (no explicit directions)

### Genre-Specific Editor 3: `continuity_checker`

`create_subagent`:
- `name`: `"continuity_checker"`
- `system_prompt`: "You are a screenplay continuity checker. You verify: character location consistency across scenes, wardrobe continuity (same story-day = same wardrobe), prop tracking (ownership, damage state), time-of-day logic (scene heading times match story progression), and era validation (technology, language, cultural norms, brands appropriate to period). Output: PASS or FAIL with specific continuity breaks."
- `description`: "Verify continuity: locations, wardrobe, props, timeline, era"

`task`:
- `agent`: `"continuity_checker"`
- `prompt` must include:
- All script files
- Outline with timeline, wardrobe notes, prop list, era/setting
- Checklist: character location per scene, wardrobe per story-day, prop ownership transfers, time-of-day sequence, era validation (tech, language, cultural norms, brands)

### Scoring

| Dimension | Weight |
|-----------|--------|
| Visual storytelling | 25% |
| Dialogue quality | 25% |
| Structure & pacing | 20% |
| Format compliance | 15% |
| Character arcs | 15% |

**Pass**: >= 75 overall. Format compliance >= 80.

**On failure**: follow quality gate protocol from `../review.md` — write a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh subagent to apply the fix → re-review (max 2 cycles). **Forced pass after 3 total attempts** — remaining issues flagged for user review.

---

## Stage 4: Assembly

Assemble final output including:
1. Title page
2. Character list with visual references
3. Location bible
4. Scene list / beat sheet
5. The script (all acts/episodes concatenated)
6. For series: series bible, season arc, episode guide

Save to `/mnt/agents/output/{project_name}.final.md`.

### Convert to .docx

Convert the assembled markdown to Word using the `md2docx` pipeline (see `skills/docx/SKILL.md` → `references/md2docx-reference.md`).

Output: `/mnt/agents/output/{project_name}.final.docx`

**This step is mandatory.** Raw .md without a .docx deliverable is not an acceptable end state.

---

## Core Principles

1. **Orchestrator = coordinator.** Dispatches tasks to subagents, manages state, merges outputs. Never writes scenes, never reviews content, never runs scripts directly.
2. **One act or episode per `task` call.** Never merge units into a single dispatch. No exceptions.
3. **Non-blocking review.** For multi-act/multi-episode works, reviews run in the background — writing the next unit never waits on review of the current unit. Only word count check gates the next dispatch.
4. **Execute to completion.** Once outline is ready, do not pause.
5. **Language follows the user.** Content in user's language. Filenames and metadata in English.

---

## Short Drama Specifics (短剧 / 竖屏短剧)

When the medium is short drama, apply these additional rules:

- **Format**: 9:16 vertical, 1-3 min episodes, 16-100+ episodes per season, mobile-first
- **3-second hook**: the first 3 seconds must arrest scrolling — conflict in progress, provocative visual, direct address, or sound hook. Each episode hooks independently
- **Dual confirmation per episode**: (1) early confirmation within 30s — micro-payoff validating the hook; (2) exit confirmation in final 10s — cliffhanger/reveal compelling next episode
- **Production grouping**: outline full season first. Script one episode at a time. Group scenes by location (single-location shooting days) and by actor (minimize actor-days)
- **Episode hooks**: each episode script must deliver two explicit fields as deliverables:
  (1) `opening_hook`: first 3 seconds of THIS episode (conflict in progress, provocative visual, or sound hook)
  (2) `closing_hook`: final beat — cliffhanger or reveal compelling the next episode
- **Continuity state** (series): after each episode, the writer outputs a continuity state: per-character emotional state + location + wardrobe, planted/resolved plot threads with scene anchors, prop status. Save to `/mnt/agents/output/{filename}.ep{NN}.continuity.md`
- **Anti-patterns**: no slow establishing shots, no scenes >45s without tension shift, no dialogue >4 lines without action interruption, no exposition dumps, no horizontal composition habits

---

## Cinematography Reference

Writers suggest visual language through action-line description — never dictate camera work.

### Camera Angles

| Angle | How to Suggest in Action Lines |
|-------|-------------------------------|
| Low-angle (power) | "He towers over the desk" |
| High-angle (vulnerability) | "She's small in the vast lobby" |
| Dutch/tilted (unease) | World described as off-kilter |
| POV (subjective) | "Through her eyes:" + exact perception |
| Close (implied) | Focus on small detail: "her finger trembles on the trigger" |
| Wide (implied) | Full environment: "alone in the empty stadium" |

### Camera Movements

| Movement | How to Suggest |
|----------|---------------|
| Pan (reveal) | Elements described left-to-right in sequence |
| Track/dolly (following) | Character moves past sequential landmarks |
| Handheld (urgency) | Short choppy action lines, fragments |
| Steadicam (immersion) | Unbroken description following character through space |
| Push-in (focus) | Wide context narrowed to tight detail |
| Pull-back (revelation) | Tight detail expanded to wide context |

### Lighting

| Method | Action-Line Cue |
|--------|-----------------|
| High-key (bright, safe) | "Sunlight floods the room" |
| Low-key (noir, danger) | "A single desk lamp cuts the darkness" |
| Backlight (mystery) | "A figure in the doorway, face in shadow" |
| Practical (intimacy) | "Candlelight flickers across their faces" |
| Chiaroscuro (ambiguity) | "Half his face in light, half in shadow" |
| Motivated (realism) | Describe actual source: TV glow, phone screen, passing headlights |

---

## Reference Files

| File | Purpose | When to Read | How to Use |
|------|---------|-------------|------------|
| [../anti-ai.md](../anti-ai.md) | Anti-AI discipline rules | Before creating writer subagents | Inline into `screenplay_writer` system prompt |
| [../review.md](../review.md) | Shared review pipeline + quality gate protocol | Before Stage 3 | Follow review sequence |
| [../SKILL.md](../SKILL.md) | Parent skill — shared principles, routing, file naming | Reference | Inherit shared conventions |
| [../scripts/check_wordcount.py](../scripts/check_wordcount.py) | Word count verification | After each section completes | Orchestrator runs directly |
