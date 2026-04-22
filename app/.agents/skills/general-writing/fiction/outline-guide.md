# Outline Guide

Skill-level reference. Tells the orchestrator how to create and maintain the project outline and satellite files.

**Naming**: `{project_name}` = slugified title (e.g., `dark_city`, `sword_of_dawn`).

| File | Role | Path |
|------|------|------|
| Master Outline | Global — foundation, volume structure, plot points, file index, current volume pointer | `/mnt/agents/output/{project_name}.outline.md` |
| Volume Outline | Per-volume — chapter status + working window for the active volume | `/mnt/agents/output/{project_name}.outline_vol{NN}.md` |
| Outline Raw | Static — full chapter specs archive, written in Stage 1, read-only | `/mnt/agents/output/documents/{project_name}.outline_raw.md` |

---

## Modules

```
/mnt/agents/output/
├── {project_name}.outline.md                    # Master outline: foundation + volume structure + file index
├── {project_name}.outline_vol01.md              # Vol 1 working outline: chapter status + working window
├── {project_name}.outline_vol02.md              # Vol 2 working outline (created when Vol 2 starts)
├── documents/
│   ├── {project_name}.outline_raw.md            # Full chapter specs archive (read-only after Stage 1)
│   ├── {project_name}.characters.md             # Character profiles, living
│   ├── {project_name}.world.md                  # Locations, rules, props, factions
│   ├── {project_name}.foreshadowing.md          # Plant/payoff tracking
│   ├── {project_name}.threads.md                # Plot thread status
│   └── {project_name}.chapter_summaries.md      # Done blocks, appended per chapter
└── chapters/
    ├── {project_name}.ch01.md
    └── ...
```

| Module | What It Tracks | Grows With |
|--------|---------------|------------|
| **outline.md** | Foundation, volume structure, plot points, file index, current volume pointer | Volume-level status updates only |
| **outline_vol{NN}.md** | Chapter status + working window for one volume | Window slides per chapter within that volume |
| **outline_raw.md** | Volume headers + all per-chapter spec blocks | Written once in Stage 1; read-only reference |
| **characters.md** | Full profiles: identity, psychology, arc, voice, relationships, current state | Character state changes per chapter |
| **world.md** | Locations (sensory), rules, props, faction map | New locations/rules/props discovered |
| **foreshadowing.md** | Plant → payoff registry | New plants OPEN, paid items CLOSED |
| **threads.md** | Named plot threads with status | Thread state changes per chapter |
| **chapter_summaries.md** | Done block per completed chapter | One entry appended per chapter |

---

## Master Outline Template (`{project_name}.outline.md`)

Global overview — stable, compact, does not grow with chapter count. The writer reads this for Foundation and File Index.

```markdown
# [Title]

## Foundation

| Key | Value |
|-----|-------|
| Genre | [primary / secondary] |
| POV | [first / third-limited / omniscient / multi-POV] |
| Tense | [past / present] |
| Tone | [2-3 descriptors] |
| Chapters | [N] |
| Words/chapter | [target range] |
| Total target | [N words] |

**Premise**: [One sentence]
**Theme**: [One question — "Can X survive Y?"]

## Volume Structure

| Vol | Title | Chapters | Core Conflict | Turning Point | Status | Words |
|-----|-------|----------|---------------|---------------|--------|-------|
| 1 | [title] | 1–30 | [what is at stake] | [midpoint shift] | DONE | 95,000 |
| 2 | [title] | 31–60 | [what is at stake] | [midpoint shift] | WRITING | 42,000 |
| 3 | [title] | 61–90 | [what is at stake] | [midpoint shift] | TODO | — |

## Plot Points

1. [Event — why it matters]
2. ...
(8–15 total. One sentence each.)

## File Index

| File | Description | Path |
|------|-------------|------|
| Current Volume Outline | Active working outline | `/mnt/agents/output/{project_name}.outline_vol02.md` |
| Outline Raw | Full chapter specs archive (read-only) | `/mnt/agents/output/documents/{project_name}.outline_raw.md` |
| Characters | Character profiles, living | `/mnt/agents/output/documents/{project_name}.characters.md` |
| World | Locations, rules, props | `/mnt/agents/output/documents/{project_name}.world.md` |
| Foreshadowing | Plant/payoff registry | `/mnt/agents/output/documents/{project_name}.foreshadowing.md` |
| Threads | Plot thread tracker | `/mnt/agents/output/documents/{project_name}.threads.md` |
| Summaries | Chapter Done blocks | `/mnt/agents/output/documents/{project_name}.chapter_summaries.md` |

## Progress

| Metric | Value |
|--------|-------|
| Completed | 42 / N |
| Words | 137,000 |
| Current Volume | 2 |
```

## Volume Outline Template (`{project_name}.outline_vol{NN}.md`)

Per-volume working outline — this is what the **writer actually reads**. Contains only this volume's chapter status and sliding window.

```markdown
# Vol 2: [Volume Title] (Ch 31–60)

**Core Conflict**: [what is at stake]
**Character Focus**: [which characters drive this volume]
**Arc**: [start state] → [end state]

## Chapter Status

| Ch | Title | Status | Words |
|----|-------|--------|-------|
| 31 | [title] | DONE | 3,200 |
| 32 | [title] | DONE | 3,400 |
| 33 | [title] | WRITING | — |
| 34 | [title] | TODO | — |
| ... | ... | TODO | — |

## Working Window

### ← Ch 31 [DONE] (3,200w)
**Summary**: [compact — 2-3 sentences max]
**Hook-out**: [exact hook that carries into Ch 32]

### ← Ch 32 [DONE] (3,400w)
**Summary**: [compact — 2-3 sentences max]
**Hook-out**: [exact hook that carries into Ch 33]

### → Ch 33 [WRITING]
- POV: [character] | Scenes: [N] | Words: [target]
- Conflict: [core dramatic question]
- Hook-in: [pick up from Ch 32 hook-out] → Hook-out: [technique]
- Beats: [key moments, comma-separated]
- Foreshadowing: [F## to plant], [F## to pay]

### → Ch 34 [TODO]
- POV: [character] | Scenes: [N] | Words: [target]
- Conflict: [core dramatic question]
- Hook-in: [technique] → Hook-out: [technique]
- Beats: [key moments]
- Foreshadowing: [F## to plant], [F## to pay]

### → Ch 35 [TODO]
- POV: [character] | Scenes: [N] | Words: [target]
- Conflict: [core dramatic question]
- Hook-in: [technique] → Hook-out: [technique]
- Beats: [key moments]
- Foreshadowing: [F## to plant], [F## to pay]
```

For single-volume novels (≤30 chapters), only one `outline_vol01.md` is created — functionally identical to the old monolithic outline.

---

## Outline Raw Template (`{project_name}.outline_raw.md`)

Complete chapter specs archive, organized by volume. Two-pass generation: coarse outline (粗纲) defines volumes → fine outline (细纲) fills per-chapter specs within each volume. Read-only after Stage 1. The orchestrator copies specs from here into the Working Window as chapters are promoted.

```markdown
# Outline Raw — [Title]

## Vol 1: [Volume Title] (Ch 1–N)

**Core Conflict**: [what is at stake in this volume]
**Character Focus**: [which characters drive this volume]
**Arc**: [volume start state] → [volume end state]
**Key Events**: [3-5 major events, comma-separated]

### Ch 01: [Title]
- POV: [character] | Scenes: [N] | Words: [target]
- Conflict: [core dramatic question]
- Hook-in: [technique] → Hook-out: [technique]
- Beats: [key moments, comma-separated]
- Foreshadowing: [F## to plant], [F## to pay]
- Deps: [none]

### Ch 02: [Title]
- POV: [character] | Scenes: [N] | Words: [target]
- ...

---

## Vol 2: [Volume Title] (Ch N+1–M)

**Core Conflict**: [what is at stake]
**Character Focus**: [which characters]
**Arc**: [start] → [end]
**Key Events**: [3-5 events]

### Ch N+1: [Title]
- ...

(All volumes and chapters listed.)
```

---

## Satellite File Templates

### characters.md

```markdown
# Character Registry

## [Character Name]

**Identity**: [name, age, specific appearance — "scar bisecting left eyebrow" not "attractive"]
**Role**: [protagonist / antagonist / supporting] — [narrative function]
**Desire**: [what they want most]
**Fear**: [what they avoid/deny]
**Contradiction**: [internal tension — "brave in battle, cowardly in love"]
**Arc**: [start state] → [current state] → [projected end]
**Voice**: [speech patterns, vocabulary, verbal tics, topics avoided]
**Relationships**:
| Character | Nature | Tension |
|-----------|--------|---------|
| [name] | [type] | [conflict source] |

**Current State**: [≤10 words — emotional + physical + situational]
**Last Seen**: Ch [N]
```

### world.md

```markdown
# World Bible

## Overview
- **Type**: [real-world / alternate history / secondary world]
- **Era**: [when]
- **Tech/Magic**: [what is possible, what isn't]
- **Social**: [power structures, taboos, customs]

## Locations

### [Location Name]
- **Sensory**: [sight, sound, smell, texture — 2-3 sentences]
- **Function**: [why it matters]
- **Last Used**: Ch [N]

## Rules
| Rule | Description | Established In |
|------|-------------|---------------|
| [rule] | [what] | Ch [N] / outline |

## Props
| Object | Location | Function | Last Seen |
|--------|----------|----------|-----------|

## Faction Map (if 3+ organized groups)
| Faction | Leader | Goal | Territory |
|---------|--------|------|-----------|

### Faction Relationships
| | Faction A | Faction B |
|---|----------|----------|
| Faction A | — | [relation] |
```

### foreshadowing.md

```markdown
# Foreshadowing Registry

| ID | Description | Planted | Target | Paid | Status |
|----|-------------|---------|--------|------|--------|
| F01 | [concrete detail] | Ch N | Ch M | — | OPEN |

Status: OPEN · CLOSED · INTENTIONAL · DANGLING
Rule: no OPEN or DANGLING at assembly.
```

### threads.md

```markdown
# Thread Tracker

| Thread | Status | Last Ch | Notes |
|--------|--------|---------|-------|
| [name] | ACTIVE / PARKED / RESOLVED | Ch N | [one-line] |
```

### chapter_summaries.md

```markdown
# Chapter Summaries

## Ch 01: [Title] (3,280w)
**Summary**: [200-300 words narrative — events, decisions, revelations]
**Characters**: [Name]: [state delta ≤1 line] | [Name]: [delta]
**Environment**: [setting/world state changes]
**Hook-out**: [exact hook — what tension carries forward]
**Foreshadowing**: F01 PLANTED (the locked door) | F03 PAID (the missing letter)
**Threads**: [thread]: PLANTED / ADVANCED / RESOLVED

---

(New entries appended at bottom.)
```

---

## Writing Standards

- **Spec blocks**: dense, no prose. `|` separators and comma lists.
- **Window summaries**: compact, 2-3 sentences. Just enough for the next writer to pick up.
- **Full summaries** (in `chapter_summaries.md`): 200-300 words narrative. What happened, changed, unresolved.
- **Character current state**: ≤10 words. Emotional + physical + situational.
- **Hook-out**: specific. "Lin discovers the letter is forged" — not "cliffhanger ending".
- **Foreshadowing entries**: concrete. "the cracked mirror" — not "symbolism of self".
- **Thread names**: short. "missing-father", "Lin-Zhao-rivalry", "poison-source".

---

## Update Mechanism

### What to Pass to Writers (task prompt)

**File-path-based** — the orchestrator passes paths, the writer reads files directly:

| Data | How to Pass |
|------|-------------|
| Chapter assignment | Chapter number(s) to write |
| Volume outline | Path to `{project_name}.outline_vol{NN}.md` — writer reads Working Window for chapter spec, previous summary, hook-out, next preview |
| Master outline | Path to `{project_name}.outline.md` — writer reads File Index to locate satellite files |
| Previous chapter | Path to `chapters/{project_name}.ch{N-1}.md` — writer reads for continuity |
| Output path | `chapters/{project_name}.ch{NN}.md` |
| Style/requirements | Word count target, genre, tone (brief inline text) |

**The orchestrator must pass the correct volume outline for the chapters being written.** Do NOT pass a volume outline from a different volume. Do NOT pass `outline_raw.md` to the writer (can be 300KB+).

**Do NOT inline**: satellite file content (characters, foreshadowing, threads, world). The writer reads these from paths listed in outline.md § File Index.

### Quality Verification

Gate before next batch. Orchestrator dispatches `quality_checker` subagent after each batch completes. The subagent runs:

```
python skills/general-writing/scripts/check_chapter_quality.py <chapter_file> --min-words {target} --lang auto
```

Output: JSON with word_count, em_dash density, english_leakage results. Exit code 0 = all PASS, 1 = any FAIL.

On FAIL: return chapter to writer with specific fix instructions before dispatching next batch.

### Post-Chapter Update Cycle (Writer's Responsibility)

The **fiction_writer** updates satellite files after writing each chapter. The orchestrator does NOT do this — a `satellite_reviewer` verifies correctness in parallel.

**Update satellite files that exist and were affected by the chapter.** Not every file will be present (some may not have been created yet) or need updating for every chapter. If the File Index lists additional files beyond this standard set, update those too when relevant. Common updates:

| Step | File | Action |
|------|------|--------|
| 1 | `outline_vol{NN}.md` — Chapter Status | Ch N: `WRITING` → `DONE` (word count). |
| 2 | `outline_vol{NN}.md` — Working Window | Slide forward: drop oldest DONE (if >2), move Ch N from WRITING to DONE (compact summary + hook-out), promote Ch N+1 to WRITING (copy spec from `outline_raw.md`), add next TODO from `outline_raw.md`. |
| 3 | `outline.md` — Progress | Increment completed count, word total. |
| 4 | `chapter_summaries.md` | Append Ch N full Done block (200-300w summary + all deltas). |
| 5 | `characters.md` | Update `Current State`, `Last Seen`, `Arc` for changed characters. |
| 6 | `world.md` | Update `Last Used`. Add new locations/rules/props. |
| 7 | `foreshadowing.md` + `threads.md` | Foreshadowing: new plants → OPEN, paid → CLOSED. Threads: new → ACTIVE, advanced → update Last Ch, resolved → RESOLVED. |

### Sliding Window Rules

- **Window size**: `2 DONE + B WRITING + 2 TODO` where B = current batch size (1 to 3). Single-chapter dispatch: 5 entries. Max batch of 3: 7 entries.
- **DONE entries in window**: compact (2-3 sentence summary + hook-out). Full details in `chapter_summaries.md`.
- **Batch-complete slide**: after the writer completes and updates all satellite files, the window reflects the new state. The next writer reads the updated window.
- **First chapters**: window starts with 0 DONE + B WRITING + 2 TODO. DONE entries accumulate until window reaches full size.
- **Final chapters**: window has more DONE than TODO as the novel ends.

### Integrity Rules

- **Writer updates first, reviewer verifies**: The fiction_writer updates the volume outline + satellite files. The satellite_reviewer (dispatched in parallel with the next writer) verifies correctness.
- **Self-contained context**: volume outline (Working Window) + master outline (File Index) + satellite files give a writer everything needed. No need to inline content in task prompts.
- **Correct volume outline**: The orchestrator must always pass the volume outline matching the chapters being written. At volume boundaries, create the new volume's outline file before dispatching the first writer for that volume.
- **Foreshadowing discipline**: `foreshadowing.md` always reflects true state.
- **Assembly gate**: Before Stage 3 — `foreshadowing.md` has no OPEN/DANGLING, `threads.md` has no ACTIVE (all RESOLVED or PARKED with justification), all Chapter Status entries are DONE.
