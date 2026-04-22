---
name: murder-mystery
type: capability
description: >
  Murder mystery game writing (剧本杀) — truth design, character scripts,
  clue systems, timeline grids, host guides, and spoiler verification.
  Covers 推理本, 情感本, 恐怖本, 机制本, 阵营本, and hybrid formats.
---

# Murder Mystery Writing (剧本杀)

Sub-skill of [general-writing](../SKILL.md). Inherits shared principles, anti-AI discipline, and quality gates.

> **CRITICAL — Spoiler Isolation Rule**: Character writers are ISOLATED from each other. Each `character_writer` receives ONLY their character's filtered truth. NEVER pass another character's secrets to a writer.

> **CRITICAL — Review → Fix Brief → Dispatched Subagent**: When a review finds issues, translate them into a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh subagent to apply the fix. Never use inline sed/edit_file fixes. Exception: `logic_checker` failures may require truth-level fixes that the orchestrator coordinates across documents.

> **CRITICAL — Anti-Read-Loop Rule**: The orchestrator must begin truth design (Stage 1) within 10 iterations. If the orchestrator has spent 10+ iterations only reading files without starting truth design, it is in a read-loop. Stop reading, start truth design from what you have immediately.

> **CRITICAL — Step Budget & Delivery**: You have a limited step budget. Plan delivery accordingly:
> - **Standard murder mysteries (4-8 players)**: fully achievable in one session. Design truth, write all scripts, review, assemble, convert to .docx.
> - **Complex scenarios (8+ players, multiple rounds)**: prioritize truth + character scripts + host guide. Deliver completed components with .docx.
> - **Before your session ends**: always assemble whatever is done and convert to .docx — never end with only raw script files.

## Trigger Keywords

剧本杀, murder mystery, 推理本, 情感本, 恐怖本, 机制本, 阵营本, LARP script, 谋杀之谜, 线索设计, 剧本杀主持

## File Paths

### Output Directory Structure

```
/mnt/agents/output/
├── research/                    # User uploads (venue info, player preferences)
├── {project_name}.truth.md          # Master truth document (orchestrator-only)
├── {project_name}.timeline_grid.md
├── {project_name}.spoiler_matrix.md
├── documents/
│   ├── {project_name}.character_web.md
│   └── {project_name}.clue_inventory.md
└── scripts/
    ├── {project_name}.{character_name}.md
    └── {project_name}.host_guide.md
```

### User-Uploaded Files

Before Stage 1, copy all user-uploaded files (venue info, player preferences, theme references) to `/mnt/agents/output/research/`. Preserve original filenames. Reference these copies (not originals) in all subagent task prompts — subagents may run in sandboxed environments without access to the original paths.

---

## Pre-Stage: Inference

Infer type, player count, duration, difficulty, and tone from the user's request. The orchestrator analyzes and infers all parameters autonomously; for complex requests, deploy a subagent to analyze requirements in depth. Never prompt the user for clarification.

---

## Stage 1: Truth Design — ORCHESTRATOR DOES THIS

**The orchestrator delegates all work to subagents** via `create_subagent` + `task` — except for this stage. **Exception: truth design is orchestrator-direct to maintain spoiler integrity.** This is the most critical stage. The Orchestrator performs truth design directly — do NOT delegate to subagents. Truth integrity determines whether the entire game works. Errors here propagate to every script and clue.

### Step 1: Build the Complete Truth Document

Write the omniscient account of what actually happened:
- Who did what, when, why, how
- Murder method: weapon + opportunity + motive
- All hidden relationships and secret dealings
- The sequence of events that led to the crime

### Step 2: Build the Timeline Grid

Rows = time periods (e.g., 8pm, 9pm, 10pm, ...). Columns = characters. Every cell filled — where was each character at each time? Mark: alibis, alibi-breaks, unaccounted gaps, opportunities.

### Step 3: Design the Character Web

For each character define:
- **Public identity**: what everyone knows
- **Private secrets**: what only they know (and what they're hiding)
- **Objectives**: what they want to achieve during the game
- **Relationships**: graph of connections to every other character (love, hate, debt, blackmail, etc.)
- **Claimed identity vs hidden truth**: how they present themselves ("I'm a loyal friend") vs what actually drives them ("I resent being overlooked") + fracture trigger (what causes the mask to slip). Creates discoverable contradictions players can detect through interrogation
- **Information inventory**: what facts they possess at game start

### Step 4: Design the Clue System

- **Deduction chain**: numbered logical steps from clues to solution — verify each step has supporting evidence
- **Clue inventory**: every clue with its trigger condition and release round
- **Red herrings**: fair (distinguishable through careful reasoning, not guessing), clearly marked in host guide
- **Redundancy**: every critical deduction has >= 2 supporting clue paths + host fallback
- **Clue depth tiers**: Surface (basic investigation, round-gated, ~50%), Hidden (requires specific actions or combining clues, ~35%), Core (deep reasoning or combining 2+ hidden clues, ~15%). Host fallback applies to surface and hidden tiers only; core clues reward attentive players
- **Clue state machine**: every clue tracks through `HIDDEN -> DISCOVERABLE -> DISCOVERED -> SHARED`

### Step 5: Design the Game State Machine

```
SETUP -> ROUND_1 -> ROUND_2 -> ROUND_3 -> ACCUSATION -> RESOLUTION
```

For each state: duration, what players do, what host does, entry condition, transition action, exit verification. Define host intervention points at each boundary (hint injection: subtle -> moderate -> direct).

### Step 6: Build the Spoiler Safety Matrix

Character x Information cross-reference table. Cell values:
- **OWNS** — character possesses from start
- **FORBID** — character must NEVER see this in their script
- **R[N]** — character may learn starting in Round N
- **COND** — conditional access, depends on player actions

### Step 7: Per-Character Script Micro-Outline

After the truth document is complete and before dispatching writers, the orchestrator produces a per-character script outline. For each character:
- What sections the script covers (identity, secrets, objectives, timeline, relationships, round guidance)
- Round-by-round breakdown: what this character knows at round start, what they can discover, what actions they should pursue, what information they may trade or withhold
- Key emotional beats and dramatic moments specific to this character
- Word count targets per section

This micro-outline ensures consistent structure across all character scripts and prevents writers from omitting required content.

**Save everything** to `/mnt/agents/output/{project_name}.truth.md`. This file is the single source of truth for Stage 2. Save the timeline grid to `/mnt/agents/output/{project_name}.timeline_grid.md` and the spoiler matrix to `/mnt/agents/output/{project_name}.spoiler_matrix.md`.

---

## Stage 2: Writing

Read [../anti-ai.md](../anti-ai.md). Inline its content into every writer's system_prompt.

Deploy parallel writing subagents. **Character writers are ISOLATED from each other** — they must not see each other's output or other characters' secrets. **Character scripts are independent (each writer is isolated) — dispatch all `character_writer` tasks in parallel via multiple `task` calls in a single message.**

**Strictly one character script per `task` call.** Never have a writer handle multiple characters.

### `character_writer` (create one per character)

`create_subagent`:
- `name`: `"character_writer"`
- `system_prompt`: "You are a murder mystery character script writer. You write from ONE character's perspective ONLY. You receive a filtered version of the truth — containing only what this character knows and experiences. You must NEVER include information that belongs to other characters. Your output follows this structure: your identity (public identity), your secrets (private secrets), your objectives, what you know (starting information), your timeline (this character's version of events, including planned lies), relationship web (relationships as this character perceives them), round 1 action guidance. Write compelling, emotionally engaging scripts where this character is the protagonist of their own story. {inline anti-ai.md}"
- `description`: "Write one character's murder mystery script from their filtered perspective"

`task` (dispatch all characters in parallel — multiple `task` calls in a single message):
- `agent`: `"character_writer"`
- `prompt`: Character name: {name}. Per-character micro-outline: {micro_outline_for_this_character}. This character's filtered truth (ONLY their knowledge): {filtered_truth_for_this_character}. Their secrets: {secrets}. Their objectives: {objectives}. Their relationships (as they perceive them): {relationships}. Their timeline (their version of events): {timeline_for_character}. Spoiler matrix row for this character: {matrix_row — shows OWNS and FORBID}. Write the complete character script following the micro-outline structure. Do NOT include any information marked FORBID.

**After each character script completes**, orchestrator runs word count verification:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, return to writer with expansion instructions.

**CRITICAL**: The Orchestrator must filter the truth document per character before passing it. Each `character_writer` receives ONLY:
- Facts this character personally witnessed or knows
- This character's secrets and objectives
- Relationships as perceived by this character (which may be incomplete or wrong)
- NEVER another character's private secrets

### `clue_designer`

`create_subagent`:
- `name`: `"clue_designer"`
- `system_prompt`: "You are a murder mystery clue designer. You create physical clue cards and evidence items with state annotations. Every clue must have: a clue ID, content, trigger condition (round-based, action-based, clue-chain, or conditional), discovery methods (>= 2 for critical clues), and the state it starts in. You ensure the complete deduction chain is solvable from distributed clues. {inline anti-ai.md}"
- `description`: "Design clue cards with state annotations and deduction chains"

`task`:
- `agent`: `"clue_designer"`
- `prompt`: Complete truth document: {full_truth}. Deduction chain: {deduction_chain}. Round structure: {game_state_machine}. Clue state machine states: HIDDEN -> DISCOVERABLE -> DISCOVERED -> SHARED. Design all clue cards. For each: ID, content text (player-facing), trigger condition, round of release, which character(s) can discover it, host fallback method. Organize by round. Verify: deduction chain completable from clues alone.

**After clue design completes**, orchestrator runs word count verification:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, return to writer with expansion instructions.

### `host_guide_writer`

`create_subagent`:
- `name`: `"host_guide_writer"`
- `system_prompt`: "You are a murder mystery host guide writer. You write the complete GM manual that enables a host to run the game smoothly. The guide must cover: setup instructions, round-by-round flow, clue distribution schedule, all branching scenarios, hint escalation protocol (subtle -> moderate -> direct), and the full truth reveal script. You write for a host who has never run this scenario before. {inline anti-ai.md}"
- `description`: "Write complete host/GM guide for running the scenario"

`task`:
- `agent`: `"host_guide_writer"`
- `prompt`: Complete truth document: {full_truth}. All character scripts: {all_script_paths}. All clues: {clue_cards}. Game state machine: {state_machine}. Spoiler matrix: {full_matrix}. Write: (1) Setup guide (materials, seating, distribution order). (2) Round-by-round host script (what to say, what to distribute, what to watch for). (3) Hint injection protocol at each round boundary. (4) Branching scenarios (what if players go off-track). (5) Truth reveal script (dramatic ordering of revelations). (6) Intervention protocols for common problems (one player dominating, stalled discussion, wrong accusation trajectory).

**After host guide completes**, orchestrator runs word count verification:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, return to writer with expansion instructions.

---

## Stage 3: Review

Read [../review.md](../review.md). Run shared pipeline first, then genre-specific editors.

**Most rigorous genre.** Logic errors ruin the entire experience. `logic_checker` must pass before other reviewers proceed.

```
continuity_editor (per section, parallel)
  -> style_editor (per section, parallel)
    -> structural_editor (cross-section, single agent)
      -> logic_checker (genre-specific, MUST PASS FIRST)
        -> spoiler_checker (genre-specific)
          -> balance_checker (genre-specific)
```

### Genre-Specific: `logic_checker`

`create_subagent`:
- `name`: `"logic_checker"`
- `system_prompt`: "You are a murder mystery logic checker. You verify that the mystery is solvable and internally consistent. You perform: (1) Forward pass — starting from available clues, can a player logically reach the correct solution? (2) Backward pass — starting from the solution, is every claim supported by discoverable evidence? (3) Missing link scan — any logical step without supporting clue? (4) Alibi verification — do all timeline entries check against the truth? (5) Clue state reachability — can every critical clue actually reach DISCOVERED state? Score >= 80 to pass."
- `description`: "Verify mystery solvability and internal logic consistency"

`task`:
- `agent`: `"logic_checker"`
- `prompt`: Truth document: {truth}. Timeline grid: {timeline}. Deduction chain: {chain}. All clues with triggers: {clues}. All character scripts: {script_paths}. Perform all 5 verification passes. For each failure, specify: what's broken, where, and how to fix it. Produce overall logic integrity score.

### Genre-Specific: `spoiler_checker`

`create_subagent`:
- `name`: `"spoiler_checker"`
- `system_prompt`: "You are a murder mystery spoiler checker. You verify that no character script contains information it should not. You compare every piece of information in each script against the spoiler safety matrix. CRITICAL FAILURE if any script contains FORBID information. Also apply the Wall Test: if you spread all scripts on a wall, could you solve the mystery from any single script? If yes, that script leaks. Score >= 80 to pass."
- `description`: "Verify no script leaks forbidden information"

`task`:
- `agent`: `"spoiler_checker"`
- `prompt`: Spoiler safety matrix: {matrix}. All character scripts: {script_paths}. For each script: (1) Map every fact and information item. (2) Check against matrix — flag FORBID violations (critical) and premature R[N] access (warning). (3) Verify OWNS information is actually present (missing info is a bug). (4) Apply Wall Test independently to each script. Report all violations with file, line, and fix.

### Genre-Specific: `balance_checker`

`create_subagent`:
- `name`: `"balance_checker"`
- `system_prompt`: "You are a murder mystery balance checker. You verify that every character has enough to do, fair information access, and meaningful agency in every round. No character should be a spectator. Information distribution should create interesting asymmetry without making any character irrelevant. Score >= 75 to pass."
- `description`: "Verify balanced player agency and information distribution"

`task`:
- `agent`: `"balance_checker"`
- `prompt`: All character scripts: {script_paths}. Clue distribution by round: {clue_schedule}. Character objectives: {objectives_list}. Check: (1) Does each character have meaningful actions in every round? (2) Is information distribution creating interesting tension (not just uneven)? (3) Are objectives achievable (not guaranteed, but possible)? (4) Is difficulty appropriate for {difficulty_level}? (5) Is duration realistic for {target_duration}? Score and report.

Quality gate protocol per [../review.md](../review.md): PASS >= 85, WARNING 70-84, REVISE < 70. Max 2 rewrite cycles. **Forced pass after 3 total attempts** — remaining issues flagged for manual fix. **Exception: `logic_checker` failure CANNOT be force-passed** — logic breaks invalidate the entire game and must be resolved. Logic integrity and spoiler safety MUST each be >= 80.

---

## Clue State Machine

`HIDDEN -> DISCOVERABLE -> DISCOVERED -> SHARED`. Triggers: round-based, action-based, clue-chain, relationship-based, conditional. Critical clues: >= 2 discovery paths + host fallback.

---

## Assembly

1. Host guide (主持人手册) with game state machine and intervention protocols
2. Individual character scripts (角色剧本) — spoiler-safe in isolation
3. Clue cards (线索卡) by round, with trigger conditions
4. Props list and setup guide
5. Timeline reference (host only)
6. Spoiler safety matrix (verification document)

Save to `/mnt/agents/output/{project_name}.final.md`. Character scripts to `/mnt/agents/output/scripts/`. Host guide to `/mnt/agents/output/scripts/{project_name}.host_guide.md`.

### Convert to .docx

Convert the assembled markdown to Word using the `md2docx` pipeline (see `skills/docx/SKILL.md` → `references/md2docx-reference.md`). Character scripts should also be individually converted for print-ready player handouts.

Output: `/mnt/agents/output/{project_name}.final.docx`

**This step is mandatory.** Raw .md without a .docx deliverable is not an acceptable end state.

---

## Reference Files

| File | When to Read | Content |
|------|-------------|---------|
| [../anti-ai.md](../anti-ai.md) | Before creating any writer subagent | AI patterns to avoid — inline into system prompts |
| [../review.md](../review.md) | Before Stage 3 | Shared review pipeline, editor definitions, quality gates |
| [../scripts/check_wordcount.py](../scripts/check_wordcount.py) | After each section completes | Word count verification | Orchestrator runs directly |
