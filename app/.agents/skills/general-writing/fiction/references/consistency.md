# Consistency Guide

Rules and methods for maintaining narrative consistency across chapters and volumes. Used by orchestrator (update cycle), continuity_editor (Stage 3), and fiction_writer (self-check).

---

## Satellite File Discipline

Consistency in long-form fiction depends on the project's satellite files being accurate and current. Every consistency check traces back to these files.

| What to Verify | Source of Truth | How |
|---------------|----------------|-----|
| Character behavior, location, emotional state | `characters.md` → Current State, Last Seen | Compare character actions against last known state |
| Timeline — hours/days elapsed, event order | `chapter_summaries.md` → per-chapter summaries | Walk the timeline forward from last DONE chapter |
| World rules — magic, tech, physics, social customs | `world.md` → Rules table | Any rule invoked must exist in the table or be added |
| Objects — who has what, where things are | `world.md` → Props table | Track object handoffs and locations |
| Foreshadowing — plants and payoffs | `foreshadowing.md` → status column | No OPEN plant forgotten > 5 chapters without advancement |
| Plot threads — active, parked, resolved | `threads.md` → status column | No ACTIVE thread dormant > 3 chapters |

**Core rule**: If a fact isn't in the satellite files, it doesn't exist. Writers must not invent backstory or state that contradicts these files. If new information is introduced in a chapter, the **fiction_writer** adds it to the relevant satellite file as part of the Post-Chapter Update Cycle (the writer owns satellite updates; a satellite_reviewer verifies correctness in parallel).

---

## Character Consistency

### State Tracking

Every character has a `Current State` field (≤10 words: emotional + physical + situational). This field is the single source of truth for what a character is experiencing RIGHT NOW.

**Before writing a chapter**: read `characters.md` for every character who appears. Verify:
- **Physical state**: injuries, fatigue, appearance changes, location
- **Emotional state**: mood, unresolved feelings from prior events
- **Knowledge state**: what this character knows and doesn't know (information asymmetry)
- **Relationship state**: current stance toward other characters (check Relationships table)

### Behavioral Consistency

Characters must act within their established psychology:
- **Desire** drives what they pursue
- **Fear** drives what they avoid or overreact to
- **Contradiction** creates unpredictable-but-believable moments

**Deviation is allowed** when:
1. The story dramatizes the deviation as a character growth moment
2. External pressure forces the character beyond their normal behavior
3. The deviation is acknowledged by the character or narrator within the same/next chapter

**Deviation is NOT allowed** when:
- The writer simply forgot the character's established patterns
- The plot needs the character to act a certain way regardless of personality
- No in-story justification is provided

### Voice Consistency

Each character's speech pattern (in `characters.md` → Voice field) must persist across chapters:
- Vocabulary level and register
- Sentence length tendencies
- Verbal tics, catchphrases, topics avoided
- How they express (or suppress) emotion

**Test**: Cover character names in a dialogue scene. Can you identify each speaker from voice alone? If not, the voices need differentiation.

---

## Timeline Consistency

### Building the Timeline

The timeline lives implicitly in `chapter_summaries.md`. Each Done block records what happened and when. The orchestrator must be able to reconstruct a linear timeline from these summaries.

**Rules**:
- Time must always move forward within a chapter (unless an explicit flashback is marked)
- Elapsed time between chapters must be stated or clearly implied
- Simultaneous events across POV threads must not contradict each other
- Seasonal, lunar, and daylight references must align with the timeline
- Travel time between locations must be physically plausible (check `world.md` → Locations)

### Common Timeline Errors

| Error | How to Catch | Fix |
|-------|-------------|-----|
| Character arrives too fast | Map distance + travel speed from world.md | Add travel scene or adjust timing |
| Event order contradiction | Two chapters reference same event with different details | Align to whichever was published first |
| Day/night mismatch | Scene says "morning" but prior scene ended at noon same day | Adjust time markers |
| Healing too fast | Character injured in Ch 5, fully recovered in Ch 6 (next day) | Add recovery time or reduce injury severity |
| Simultaneous impossibility | Character appears in two places at the same time across POV threads | Adjust timeline or add travel transition |

---

## World Rule Consistency

### Rule Registry

All rules (magic systems, technology limits, social customs, physical laws) are tracked in `world.md` → Rules table. Every rule has an `Established In` field.

**Rules**:
- Once established, a rule cannot be broken without in-story justification
- New rules must be established BEFORE they matter to the plot (no deus ex machina)
- If a character discovers a rule exception, record it in the Rules table with the chapter reference
- Rules apply equally to all characters — no selective enforcement for plot convenience

### Object Tracking

Objects (weapons, letters, keys, artifacts) are tracked in `world.md` → Props table.

**Rules**:
- If an object is important enough to describe, track its location and last seen chapter
- Objects don't teleport — handoffs must be shown or implied
- Chekhov's gun: objects introduced with emphasis must serve a purpose later
- Objects consumed or destroyed should be marked in the Props table

---

## Cross-Chapter Continuity

### Hook Chain

Every chapter's hook-out must be addressed by the next chapter's hook-in. The Working Window enforces this by showing adjacent chapters side by side.

**Rules**:
- Hook-out → hook-in connection must be direct (not skipped or contradicted)
- If a POV switch delays resolution, the delay must be acknowledged when the thread resumes
- No hook can be permanently dropped — every opened tension must eventually resolve or be explicitly subsumed into a larger tension

### Foreshadowing Discipline

Managed via `foreshadowing.md`. Rules:
- Plants must be CONCRETE ("the cracked mirror", "the unsigned letter") — never abstract ("symbolism of self")
- Every OPEN plant must be paid off (CLOSED) or marked INTENTIONAL before assembly
- No plant stays OPEN for more than 1 volume without at least one advancement
- DANGLING status = bug. Must be fixed in backpatch or resolved in upcoming chapters
- Payoff must be proportional to the emphasis of the plant — a heavily emphasized plant demands a significant payoff

### Thread Management

Managed via `threads.md`. Rules:
- ACTIVE threads must show visible progress every 2-3 chapters
- PARKED threads require a narrative reason (character is separated, subplot is deliberately suspended)
- PARKED threads must resume before the volume ends or be marked RESOLVED
- Thread resolution should feel earned — not abrupt or convenient

---

## Cross-Volume Continuity

When the last chapter in a volume completes, the orchestrator triggers a **Volume Boundary Review** via subagent. This is a critical gate before the next volume begins writing.

### Volume Boundary Review Protocol

**Step 1**: Dispatch `structural_editor` across all chapters in the completed volume. The task prompt passes paths to all chapter files for that volume + the path to `outline.md` (editor reads Volume Structure and satellite files via File Index).

**Step 2**: Verify against satellite files:
- All volume-scoped foreshadowing CLOSED (check `foreshadowing.md` — no OPEN items tagged to this volume)
- Character arcs hit volume milestone (check `characters.md` → Arc field: current state matches volume-end projection)
- No ACTIVE threads abandoned across volume boundary without PARKED justification (check `threads.md`)
- Volume end state matches next volume's start state (check `outline.md` → Volume Structure)
- Timeline coherence within volume (walk `chapter_summaries.md` for this volume's range)
- Tone/style transitions between volumes are deliberate, not accidental

**Step 3**: Generate volume summary (500-800 words) covering:
- Major events in order
- Character states at volume end (emotional, physical, relational)
- Open threads carrying into next volume
- Unresolved foreshadowing items (with expected payoff volume)

**Step 4**: Write volume summary to `/mnt/agents/output/documents/{project_name}.vol{N}_summary.md`. The fiction_writer reads this file (referenced in outline.md or task prompt path) as additional context when starting the next volume. Do NOT inline the volume summary into the task prompt — pass the file path.

**All 4 steps are executed by subagents** — the orchestrator dispatches and coordinates but does not perform the analysis.

---

## Pre-Write Checklist (for fiction_writer)

Before writing Ch N, verify (all file paths found via `outline.md` → File Index):

1. Read `outline.md` → **Working Window** — Ch N spec (POV, conflict, beats, hooks, foreshadowing IDs), Ch N-1 summary + hook-out, Ch N+1 preview
2. Read `outline.md` → **File Index** to locate satellite file paths
3. Read `characters.md` — current state of every character appearing in Ch N
4. Read `foreshadowing.md` — any items to plant or pay in Ch N (per spec)
5. Read `threads.md` — status of threads that Ch N touches
6. Read relevant `world.md` sections — locations and rules for Ch N's setting
7. Read previous chapter file (path from task prompt) for continuity + hook-in
8. Confirm: Ch N's opening addresses Ch N-1's hook-out
9. Confirm: no character state contradicts their Last Seen entry
