---
name: trpg
type: capability
description: >
  TRPG scenario and module writing — one-shots, campaigns, NPCs, encounters,
  handouts, and safety tools for CoC, DnD, Pathfinder, FATE, homebrew, and
  genre variants (xianxia, sci-fi survival, gamified/lite).
---

# TRPG Writing

Sub-skill of [general-writing](../SKILL.md). Inherits shared principles, anti-AI discipline, and quality gates.

> **CRITICAL — Review → Fix Brief → Dispatched Subagent**: When a review finds issues, translate them into a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh subagent to apply the fix. Never use inline sed/edit_file fixes.

> **CRITICAL — Anti-Read-Loop Rule**: The orchestrator must dispatch its first subagent (world_designer, encounter_designer, or npc_writer) within 10 iterations. If the orchestrator has spent 10+ iterations only reading files without creating any subagent, it is in a read-loop. Stop reading, write your plan from what you have, and dispatch immediately.

> **CRITICAL — Step Budget & Delivery**: You have a limited step budget. Plan delivery accordingly:
> - **One-shots**: fully achievable in one session. Write all components, review, assemble, convert to .docx.
> - **Campaigns / multi-session modules**: prioritize core scenario + key NPCs + encounter maps. Deliver completed components with .docx and ask user whether to continue.
> - **Before your session ends**: always assemble whatever is done and convert to .docx — never end with only raw component files.

## Trigger Keywords

跑团, TRPG, tabletop RPG, CoC, DnD, 模组, scenario, one-shot, campaign, keeper, dungeon master, NPC设计, encounter, Pathfinder, FATE, sandbox, 战役, 调查员, 修仙

## File Paths

### Output Directory Structure

```
/mnt/agents/output/
├── research/                    # User uploads (system rulebooks, setting refs)
├── {project_name}.outline.md
├── documents/
│   ├── {project_name}.npcs.md
│   ├── {project_name}.encounters.md
│   └── {project_name}.maps.md
└── scenes/
    ├── {project_name}.scene{NN}.md
    ├── {project_name}.stat_blocks.md
    └── {project_name}.handouts/
```

### User-Uploaded Files

Before Stage 1, copy all user-uploaded files (system rulebooks, setting references, existing campaign notes) to `/mnt/agents/output/research/`. Preserve original filenames. Reference these copies (not originals) in all subagent task prompts — subagents may run in sandboxed environments without access to the original paths.

---

## Pre-Stage: Inference

Infer system, scope, player count, tone, and experience level from the user's request. The orchestrator analyzes and infers all parameters autonomously; for complex requests, deploy a subagent to analyze requirements in depth. Never prompt the user for clarification.

---

## Stage 1: Scenario Design

**The orchestrator delegates all work to subagents** via `create_subagent` + `task`. The orchestrator coordinates, merges outputs, and manages state — it never writes content directly.

Create three planning subagents and dispatch all three `task` calls in parallel (in a single message). Orchestrator synthesizes their outputs into a unified scenario plan.

### `scenario_planner`

`create_subagent`:
- `name`: `"scenario_planner"`
- `system_prompt`: "You are a TRPG scenario architect. You design the narrative premise, core conflict, and resolution paths for tabletop RPG modules. Every scenario must have a compelling hook, at least 3 distinct resolution paths (including failure states), and no railroad — core information must be reachable through multiple approaches. Write for the GM as your audience."
- `description`: "Design TRPG scenario premise, conflict, and resolution paths"

`task`:
- `agent`: `"scenario_planner"`
- `prompt`: System: {system}. Scope: {scope}. Player count: {player_count}. Tone: {tone}. User request: {user_query}. Design: (1) Premise and hook — one paragraph that sells the scenario. (2) Core conflict — what is at stake, who opposes the players. (3) Location map — key locations, connections, what triggers events at each. (4) At least 3 resolution paths with consequences. (5) Failure states — what happens if players lose.

### `npc_designer`

`create_subagent`:
- `name`: `"npc_designer"`
- `system_prompt`: "You are an NPC designer for tabletop RPGs. Every NPC has a dual profile: narrative (personality, motivation, knowledge, relationships, hidden agenda) and mechanical (system-correct stat block, skills, combat behavior). NPCs are autonomous agents with goals independent of the players — they are never quest dispensers. Include reaction matrices: how does this NPC respond to being threatened, befriended, ignored, betrayed?"
- `description`: "Design NPCs with narrative profiles, stat blocks, and reaction matrices"

`task`:
- `agent`: `"npc_designer"`
- `prompt`: System: {system}. Scenario premise: {premise from scenario_planner}. Design {N} NPCs. For each: narrative profile (personality, motivation, what they know, what they hide, relationships to other NPCs) + mechanical stat block (system: {system}, ensure rules-correct stats) + reaction matrix (4 situations) + GM notes (what they reveal under what conditions). Additionally: define inter-NPC relationships (alliance/tension/romance/hostility/mentorship) with gameplay effects (e.g., feuding NPCs refuse to cooperate, allied NPCs share info). Track in a relationship matrix: NPC_A <-> NPC_B: type + brief note.

### `encounter_designer`

`create_subagent`:
- `name`: `"encounter_designer"`
- `system_prompt`: "You are a TRPG encounter designer. You design key scenes, triggers, branching paths, and failure alternatives. Every encounter must be balanced for the specified player count and level. Encounters include social, exploration, and combat — not just combat. Provide consequence reports: what changes in the world and in relationships after each encounter outcome."
- `description`: "Design balanced encounters with triggers, branches, and consequences"

`task`:
- `agent`: `"encounter_designer"`
- `prompt`: System: {system}. Player count: {player_count}. Scenario premise: {premise}. NPC roster: {npc_profiles}. Design: (1) Key encounters/scenes (minimum 5 for one-shot, more for campaign). (2) Trigger conditions for each. (3) Branching paths — at least 2 player approaches per encounter. (4) Consequence reports: [CONSEQUENCE REPORT] Decision / WORLD STATE: Immediate, Session+1, Long-term / RELATIONSHIPS: Immediate, Session+1, Long-term.

**After all three complete**: Orchestrator merges into unified scenario plan. Resolve conflicts between subagent outputs.

### Per-Scene Micro-Outline

After merging the three planners' outputs, the orchestrator produces a per-scene micro-outline before dispatching Stage 2 writers. For each scene:
- Scene beats (the sequence of dramatic moments within the scene)
- NPCs present and their goals within this scene
- Triggers that activate or alter the scene
- Consequences of each possible outcome (immediate and downstream)
- Pacing annotation (SLOW DOWN / SPEED UP / CUT)

This micro-outline ensures writers have a shared understanding of scene structure and prevents gaps or contradictions between narrative, encounters, and NPC behavior.

Save to `/mnt/agents/output/{project_name}.outline.md`. Proceed to Stage 2 automatically.

---

## Stage 2: Writing

Read [../anti-ai.md](../anti-ai.md). Inline its content into every writer's system_prompt.

Deploy parallel writing subagents by deliverable type. Each receives the scenario plan and per-scene micro-outline from Stage 1. **`narrative_writer`, `stat_block_writer`, and `handout_writer` can run in parallel for independent scenes — dispatch their `task` calls in a single message.**

**Strictly one scene/encounter per `task` call** for narrative_writer. **One stat block batch per `task` call** for stat_block_writer.

### `narrative_writer`

`create_subagent`:
- `name`: `"narrative_writer"`
- `system_prompt`: "You are a TRPG narrative writer. You write atmospheric scene descriptions and boxed text for GMs to read aloud. Rules: boxed text is maximum 5 sentences, uses sensory detail (sight, sound, smell, texture), ends with an action prompt for players, and never includes scripted NPC dialogue. You write to enable GM improvisation, not constrain it. {inline anti-ai.md}"
- `description`: "Write atmospheric scene descriptions and boxed text"

`task` (one call per scene — multiple scene tasks in a single message for parallel dispatch):
- `agent`: `"narrative_writer"`
- `prompt`: Scenario plan: {outline file path}. Per-scene micro-outline: {micro_outline_path}. NPC profiles: {npc_profiles}. Location map: {location_map}. Write scene descriptions for each location and key encounter. Format boxed text in blockquotes. Include GM-facing notes after each boxed text section (mood, pacing hints, what to emphasize). Scenes assigned: {scene_list}. Use scene templates for pacing: Confrontation (Stakes -> Exchange -> Escalation -> Decision -> Consequence), Heist (Plan -> Entry -> Complication -> Objective -> Extraction), Social (Positions -> Information -> Leverage -> Deal/conflict -> Relationship change), Chase (Trigger -> Terrain -> Obstacles -> Choice -> Resolution), Revelation (Clue buildup -> Truth -> Space to land -> Player reaction -> Implications). Include pacing annotations per scene: SLOW DOWN (major reveals, aftermath), SPEED UP (travel, logistics — use montage), CUT (skip ahead).

**After each scene completes**, orchestrator runs word count verification:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, return to writer with expansion instructions.

### `stat_block_writer`

`create_subagent`:
- `name`: `"stat_block_writer"`
- `system_prompt`: "You are a TRPG stat block writer specializing in {system}. You produce mechanically accurate stat blocks, DCs, encounter balance tables, and loot tables. Every number must be rules-correct for the specified system and level range. If the system is homebrew, document all custom rules explicitly. {inline anti-ai.md}"
- `description`: "Produce mechanically accurate stat blocks and balance tables"

`task`:
- `agent`: `"stat_block_writer"`
- `prompt`: System: {system}. Player count: {player_count}. Level range: {level_range}. NPC roster (narrative profiles): {npc_profiles}. Encounters: {encounter_list}. Produce: (1) Complete stat blocks for all NPCs. (2) Encounter balance summary (action economy, expected difficulty). (3) DCs for skill checks. (4) Loot/reward tables. System reference: {system_rules_if_available}.

**After each stat block batch completes**, orchestrator runs word count verification:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, return to writer with expansion instructions.

### `handout_writer`

`create_subagent`:
- `name`: `"handout_writer"`
- `system_prompt`: "You are a TRPG handout writer. You create player-facing materials: pre-generated characters, maps, letters, documents, clue cards. All handouts must be self-contained (a player holding only this handout understands it), spoiler-free (no GM secrets leak), and printable (clean formatting). {inline anti-ai.md}"
- `description`: "Create player-facing handouts, character sheets, and safety docs"

`task`:
- `agent`: `"handout_writer"`
- `prompt`: Scenario plan: {outline}. NPC roster: {npc_profiles for player-facing NPCs only}. Plot threads requiring physical clues: {clue_list}. Produce: (1) Pre-gen character sheets (if requested, {player_count} characters). (2) Player handouts (letters, documents, maps as described in scenario). (3) Content warnings list. (4) Session 0 guide (safety tools explanation — see Safety Tools below).

**After each handout completes**, orchestrator runs word count verification:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, return to writer with expansion instructions.

---

## Stage 3: Review

Read [../review.md](../review.md). Run the shared pipeline first, then genre-specific editors.

```
continuity_editor (per section, parallel)
  -> style_editor (per section, parallel)
    -> structural_editor (cross-section, single agent)
      -> rules_checker (genre-specific)
        -> flow_editor (genre-specific)
```

### Genre-Specific: `rules_checker`

`create_subagent`:
- `name`: `"rules_checker"`
- `system_prompt`: "You are a TRPG rules checker for {system}. You verify stat blocks, DCs, encounter balance, action economy, and all mechanical elements against the system's published rules. Score each element. Overall mechanical accuracy must be >= 80 to pass."
- `description`: "Verify mechanical accuracy of stat blocks and encounters"

`task`:
- `agent`: `"rules_checker"`
- `prompt`: System: {system}. All stat blocks: {paths}. All encounters: {paths}. Check: (1) Stat block correctness (attributes, skills, HP, damage, special abilities). (2) DC appropriateness for level range. (3) Encounter balance (CR/difficulty rating vs party). (4) Loot value within system norms. Score each and provide overall mechanical accuracy score.

### Genre-Specific: `flow_editor`

`create_subagent`:
- `name`: `"flow_editor"`
- `system_prompt`: "You are a TRPG flow editor. You test scenario runnability by simulating player paths. You check for: railroads (only one valid path), dead ends (unrecoverable states), inaccessible information (core clues behind a single roll with no fallback), and unpredictable player actions (what if they do X?). For each problem found, propose a fix."
- `description`: "Simulate player paths to verify scenario runnability"

`task`:
- `agent`: `"flow_editor"`
- `prompt`: Complete scenario: {all section paths}. NPC roster: {paths}. Encounters: {paths}. Simulate: (1) Optimal path. (2) Worst-case path (players miss everything possible). (3) Adversarial path (players do the unexpected). (4) For each, identify: dead ends, railroads, missing fallbacks, information bottlenecks. Score runnability. Pass threshold: >= 75.

Quality gate protocol per [../review.md](../review.md): PASS >= 85, WARNING 70-84, REVISE < 70. Max 2 rewrite cycles. **Forced pass after 3 total attempts** — remaining issues flagged for manual fix.

---

## Safety Tools

**Non-negotiable.** Every scenario includes safety documentation.

- **Lines & Veils**: Lines = hard limits (never included). Veils = exist but off-screen. Default Lines always active: sexual content involving minors, real-world hate speech presented approvingly, shock without narrative purpose.
- **X-Card / Pause Protocol**: "X-card" = immediate stop; "Rewind" = go back; "Skip" = fast-forward; "Fade to black" = acknowledge, don't describe.
- **Content Warnings**: Listed at scenario top. GM reads during Session 0.

---

## System-Specific Notes

| System | Key Mechanics to Get Right |
|--------|---------------------------|
| CoC | Sanity loss/recovery, Luck spend, core clues (always findable) vs bonus clues, Pushed Rolls, chase rules |
| DnD/PF | CR balance, rest economy (short/long), action economy, concentration, DC scaling by tier |
| FATE | Aspects, compels, fate points, zone-based positioning, stress vs consequences |
| Homebrew | Document ALL custom rules in a dedicated section; stat blocks reference these rules explicitly |

---

## Assembly

1. Overview / synopsis (one page)
2. Session 0 guide (safety tools, content warnings)
3. GM prep checklist
4. Scene-by-scene scenario with boxed text
5. NPC appendix (stat blocks + narrative profiles + reaction matrices)
6. Player handouts (spoiler-free)
7. Campaign persistence template (multi-session only)

Save to `/mnt/agents/output/{project_name}.final.md`.

### Convert to .docx

Convert the assembled markdown to Word using the `md2docx` pipeline (see `skills/docx/SKILL.md` → `references/md2docx-reference.md`).

Output: `/mnt/agents/output/{project_name}.final.docx`

**This step is mandatory.** Raw .md without a .docx deliverable is not an acceptable end state.

---

## Reference Files

| File | When to Read | Content |
|------|-------------|---------|
| [../anti-ai.md](../anti-ai.md) | Before creating any writer subagent | AI patterns to avoid — inline into system prompts |
| [../review.md](../review.md) | Before Stage 3 | Shared review pipeline, editor definitions, quality gates |
| [../scripts/check_wordcount.py](../scripts/check_wordcount.py) | After each section completes | Word count verification | Orchestrator runs directly |
