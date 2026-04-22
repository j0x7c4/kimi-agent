---
name: fanfiction
type: capability
description: >
  Fanfiction and derivative creative writing — stories based on existing works
  (anime, manga, novels, games, film, TV, etc.). Handles character voice fidelity,
  canon compliance, AU construction, shipping dynamics, and fandom conventions.
---

# Fanfiction Writing

Orchestrate the full lifecycle of fanfiction: canon voice extraction, outline design, parallel chapter writing and review, and assembly. **The orchestrator never executes tasks directly** — all work (canon analysis, writing, reviewing, word count checking, assembly) is delegated to subagents via `create_subagent` + `task`.

Sub-skill of [general-writing](../SKILL.md). Inherits shared creative writing principles, anti-AI discipline, and quality gate framework.

> **CRITICAL — Review → Fix Brief → Dispatched Subagent**: When a review (canon_checker, voice_editor, or shared pipeline) finds issues, translate them into a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh subagent to apply the fix. Never use inline sed/edit_file fixes.

> **CRITICAL — Anti-Read-Loop Rule**: The orchestrator must dispatch its first subagent (canon_analyst or fanfic_writer) within 10 iterations. If the orchestrator has spent 10+ iterations only reading files without creating any subagent, it is in a read-loop. Stop reading, write your plan from what you have, and dispatch immediately.

> **CRITICAL — Step Budget & Delivery**: You have a limited step budget. Plan delivery accordingly:
> - **One-shots and short fics**: fully achievable in one session. Write, review, assemble, convert to .docx.
> - **Multi-chapter fics**: plan to deliver all chapters per session with full quality (review + assembly + .docx). For very long fics, deliver completed chapters with .docx and ask user whether to continue.
> - **Before your session ends**: always assemble whatever chapters are done and convert to .docx — never end with only raw chapter files.

> **CRITICAL — .docx Delivery**: Every completed fanfic must be converted to .docx using `skills/docx/SKILL.md`. Never end a session with raw .md files and no .docx deliverable.

## Trigger Keywords

同人, fanfic, fanfiction, AU, OOC, 二创, 同人文, CP, 原作向, 架空

## File Paths

### Output Directory Structure

```
/mnt/agents/output/
├── research/                                    # User uploads + canon source material
│   └── {uploaded_file}                          # Preserved original filename
├── {project_name}.outline.md
├── {project_name}.final.md
├── documents/
│   ├── {project_name}.voice_db.md               # Canon voice database
│   ├── {project_name}.characters.md
│   ├── {project_name}.divergence_log.md          # Canon divergence tracking
│   └── {project_name}.chapter_summaries.md
└── chapters/
    └── {project_name}.ch{NN}.md
```

### User-Uploaded Files

Before Stage 1, copy all user-uploaded files (canon excerpts, character references, source material) to `/mnt/agents/output/research/`. Preserve original filenames. Reference these copies (not originals) in all subagent task prompts — subagents may run in sandboxed environments without access to the original paths.

## Workflow Decision Tree

```
User Query
  │
  ├─ Provides existing draft + asks for revision → Stage 3 → Stage 4
  ├─ Provides outline + asks for content → Stage 2 → Stage 3 → Stage 4
  └─ New request → Stage 1 → Stage 2 → Stage 3 → Stage 4
```

## Pre-Stage: Canon Analysis

Infer source material, canon scope, ship/pairing, tone, AU type, and length from the user's request. The orchestrator analyzes and infers all parameters autonomously; for complex requests, deploy a subagent to analyze requirements in depth. Never prompt the user for clarification.

Orchestrator extracts from the user query:
1. **Canon source**: title, medium, completion status
2. **AU type**: canon-compliant (原作向) / canon-divergent / AU / crossover
3. **Ships**: pairings (romantic A/B, platonic A & B), or gen (无CP)
4. **Rating and tone**: G/T/M/E, fluff/angst/slow burn/darkfic
5. **Target platform**: AO3, Lofter, Wattpad — determines tagging and format conventions
6. **Target length**: one-shot vs. multi-chapter; approximate word count

Create working directory at `/mnt/agents/output/`.

## Stage 1: Canon Voice Database

**Read [../anti-ai.md](../anti-ai.md) before this stage.**

For every major character, create a voice profile. This is the most critical pre-writing artifact.

`create_subagent`:
- `name`: `"canon_analyst"`
- `system_prompt`: "You are a canon analysis specialist. Your job is to extract precise character voice profiles from source material. For each character, document: (1) speech patterns — sentence length, register, verbal tics, catchphrases, humor style, conflict style; (2) thought patterns — emotional processing, decision-making, what they notice first, internal monologue register; (3) behavioral signatures — physical habits, stress reactions, comfort behaviors; (4) relationship-specific voice shifts — how speech changes with different people; (5) 3-5 representative canon quotes with scene references. For AU: mark each trait as CORE (preserve) or SURFACE (adapt to setting)."
- `description`: "Extract character voice profiles from canon source material"

`task`:
- `agent`: `"canon_analyst"`
- `prompt`: "Extract voice profiles for [character list] from [source title]. The fic is [AU type]. Focus on traits that distinguish each character from every other character. Include the cover test: if names were removed from dialogue, a reader should identify each speaker." Include user-provided source materials from `/mnt/agents/output/research/`.

**Output**: Save to `/mnt/agents/output/documents/{project_name}.voice_db.md`. This file is passed to all downstream writer and reviewer subagents.

## Stage 2: Outline

For multi-chapter fics, use a two-phase outline process:

### Phase 1: Macro Outline

`create_subagent`:
- `name`: `"outline_designer"`
- `system_prompt`: "You are an outline designer for fanfiction. You create structured, executable outlines that respect (or deliberately subvert) canon."
- `description`: "Design fanfiction outlines with canon-aware structure"

`task`:
- `agent`: `"outline_designer"`
- `prompt`: "Design a macro outline for a [AU type] [ship/gen] fic based on [source]. Rating: [rating]. Tone: [tone]. Target length: [word count]. Include: (1) premise and central conflict; (2) canon divergence point and its ripple effects (if divergent/AU); (3) arc structure — beginning, midpoint turn, climax, resolution; (4) ship dynamics trajectory — initial state, tension points, breakthroughs, equilibrium shift; (5) thematic throughline." Inline voice database content and user requirements.

### Phase 2: Micro Outline

`task` (same `outline_designer` subagent):
- `agent`: `"outline_designer"`
- `prompt`: "Expand the macro outline into a per-chapter micro outline. For each chapter include: (1) scene list with POV assignments; (2) emotional beats and trajectory; (3) canon references and callbacks to use; (4) word count target; (5) relationship state entering and leaving the chapter; (6) foreshadowing registry entries." Inline macro outline from Phase 1 and voice database content.

For one-shots or short fics (<5k words), a single-phase outline covering premise, arc, and scene breakdown is sufficient.

**Output**: Save to `/mnt/agents/output/{project_name}.outline.md`. Orchestrator validates the outline for completeness and consistency, then proceeds automatically.

**Initialize state panels** (for works with 3+ chapters):
- Canon Facts Panel — immutable canon truths, locked after this stage
- Divergence Log — every intentional departure from canon with justification
- Ship Dynamic Tracker — relationship stage, power balance, intimacy levels per chapter
- Standard panels: characters, plot threads, timeline, POV rules

## Stage 3: Writing

**Read [../anti-ai.md](../anti-ai.md) — inline its content into writer system prompts.**

`create_subagent`:
- `name`: `"fanfic_writer"`
- `system_prompt`: Compose from these elements:
  1. Role: "You are a fanfiction writer specializing in [source title] [AU type] fiction."
  2. Voice reference: Inline the full voice database content from `{project_name}.voice_db.md`
  3. Anti-AI rules: Inline content from `../anti-ai.md`. Add fanfic-specific anti-patterns: "All characters must have distinguishable voices. No modern idioms in period settings. No abstract emotions replacing concrete actions."
  4. AU mapping rules (if AU): "Core personality traits are preserved. Surface traits adapt to setting. Established AU rules must hold consistently."
  5. Canon fidelity mandate: "Character voice fidelity is the #1 priority. Apply the cover test: remove character names from dialogue — a canon reader must identify each speaker."
- `description`: "Write fanfiction chapters with canon voice fidelity"

**Strictly one chapter per `task` call** for works with chapters. For short fics (<5k words), one task for the entire piece.

**Dispatch chapters**:

1. Parse outline: extract chapters, word counts, dependencies
2. Group chapters into rounds by dependency:
   - Round 1: chapters with no upstream dependencies (parallelize)
   - Round 2+: chapters depending on prior rounds (serialize with context)
   - Summary/climax chapters: always in a later round
3. For each chapter, dispatch via `task`:
   - **prompt**: "Write chapter [N]: [chapter title]. Word count: [target]."
   - **context** must include:
     - Outline excerpt for this chapter (scenes, POV, emotional arc)
     - Canon Facts Panel (immutable truths the chapter must not contradict)
     - Divergence Log (what has been changed and why)
     - State panels current as of previous chapter
     - Predecessor chapter summary (emotional state changes, relationship evolution, plot thread updates)
     - Ship Dynamic Tracker state (if shipping fic)
   - Save each chapter to `/mnt/agents/output/chapters/{project_name}.ch{NN}.md`
4. After each chapter completes, orchestrator runs word count verification:
   ```
   python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
   ```
   If FAIL, return to writer with expansion instructions.
5. After each chapter: update all state panels before dispatching the next round

**Horse-racing**: For the first meeting/reunion scene or emotional climax, dispatch 2-3 parallel writers with different approaches. Present variants to user for selection.

## Stage 4: Review

**Read [../review.md](../review.md) first. Follow the shared pipeline, then add genre-specific editors.**

### Shared Pipeline (from review.md)

```
continuity_editor (per chapter, parallelizable)
  → style_editor (per chapter, parallelizable)
    → structural_editor (cross-chapter, reads all)
```

### Non-Blocking Review

Reviews run **in the background and do not block writing**. When a chapter finishes writing and passes word count check, the orchestrator dispatches `canon_checker` and `voice_editor` immediately but also starts writing the next chapter without waiting for review results. Only when a review finds issues does the orchestrator dispatch a targeted fix.

### Genre-Specific Editors (after shared pipeline)

**1. `canon_checker`** — The most critical reviewer. Per chapter, parallelizable.

`create_subagent`:
- `name`: `"canon_checker"`
- `system_prompt`: "You are a canon fidelity checker. You compare character dialogue and behavior against the voice database. Flag any moment where a character would make a fan say 'they would NEVER do that.' For AU: verify core traits are preserved. Check canon facts against the Canon Facts Panel. Verify all divergences are in the Divergence Log."
- `description`: "Check chapter canon fidelity against voice database"

`task`:
- `agent`: `"canon_checker"`
- `prompt`: Inline chapter text, voice database content, Canon Facts Panel, and Divergence Log.

Scoring:
- Character Voice Fidelity: 35% weight, floor 70 (non-negotiable)
- Canon Consistency: 25% weight, floor 60
- Original Contribution: 20% weight, floor 50
- Craft Quality: 20% weight, floor 60
- **Pass**: >= 75 overall AND voice fidelity >= 70 AND no dimension below floor

**Iterative loop**: flag violations → translate into a fix brief → dispatch a fresh subagent to apply the fix → re-check. Max 2 revision rounds. **Forced pass after 3 total attempts** (1 original + 2 revisions) — remaining issues go to the backpatch queue for resolution after all chapters are written.

**2. `voice_editor`** — Beyond accuracy, checks distinguishability. Per chapter.

`create_subagent`:
- `name`: `"voice_editor"`
- `system_prompt`: "You check that characters are distinguishable from each other and that the narrative voice complements without overshadowing. Internal monologue must feel like THIS character thinking, not the author thinking."
- `description`: "Check character voice distinguishability per chapter"

### Backpatch Pass

After all chapters pass review:
- Create a `backpatch_editor` subagent that reads all chapters sequentially
- Task: "Read all chapters end-to-end. Fix: (1) canon inconsistencies visible only across chapters; (2) character voice drift; (3) unresolved threads; (4) AU world-building continuity errors; (5) relationship progression coherence."
- For each issue found, translate into a fix brief and dispatch a fresh subagent to apply the fix.

### Assembly

1. Add front matter: title, author notes, tags, warnings, rating (platform-appropriate)
2. Concatenate all `chapters/{project_name}.ch{NN}.md` files
3. Save to `/mnt/agents/output/{project_name}.final.md`
4. Convert to .docx using the `md2docx` pipeline (see `skills/docx/SKILL.md` → `references/md2docx-reference.md`). Output: `/mnt/agents/output/{project_name}.final.docx`. **This step is mandatory.**
5. Final continuity pass on chapter seams

## Platform Conventions (Brief Reference)

- **AO3**: Relationship tags (A/B romantic, A & B platonic), rating (G/T/M/E), archive warnings, freeform tags, author's notes (HTML)
- **Lofter**: Tag format "fandom name + ship name", content warnings in opening A/N, word count and genre tags at top
- **Wattpad**: Chapter-by-chapter, ~25 tags, Mature toggle, inline A/N

## Reference Files

| File | When to Read | Content | Usage |
|------|-------------|---------|-------|
| [../anti-ai.md](../anti-ai.md) | Before creating any writer subagent | AI patterns to avoid — inline into system prompts | Writer and reviewer subagents |
| [../review.md](../review.md) | Before Stage 4 | Shared review pipeline, editor definitions, quality gates | Orchestrator |
| [../scripts/check_wordcount.py](../scripts/check_wordcount.py) | After each section completes | Word count verification | Orchestrator runs directly |
| Voice database (`documents/{project_name}.voice_db.md`) | Generated in Stage 1 | Per-character speech/thought/behavior profiles | All downstream subagents |
| Outline (`{project_name}.outline.md`) | Generated in Stage 2 | Plot structure, chapter breakdown, state panel setup | Writer and reviewer subagents |
