---
name: game-writing
type: capability
description: >
  Game narrative and writing — world bibles, character bibles, quest design,
  dialogue trees, item/skill descriptions, lore entries, barks, combat text,
  and narrative design for video games and interactive media.
---

# Game Writing

Sub-skill of [general-writing](../SKILL.md). Inherits shared principles, anti-AI discipline, and quality gates.

> **CRITICAL — Review → Fix Brief → Dispatched Subagent**: When a review finds issues, translate them into a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh subagent to apply the fix. Never use inline sed/edit_file fixes.

> **CRITICAL — Anti-Read-Loop Rule**: The orchestrator must dispatch its first subagent (world_planner or detail_planner) within 10 iterations. If the orchestrator has spent 10+ iterations only reading files without creating any subagent, it is in a read-loop. Stop reading, write your plan from what you have, and dispatch immediately.

> **CRITICAL — Step Budget & Delivery**: You have a limited step budget. Plan delivery accordingly:
> - **Small projects (1-2 deliverable types)**: fully achievable in one session.
> - **Large projects (full world bible + quests + dialogues + flavor)**: prioritize world bible and highest-priority deliverables. Deliver completed deliverables with .docx and ask user whether to continue with remaining types.
> - **Before your session ends**: always assemble completed deliverables and convert to .docx.

> **CRITICAL — .docx Delivery**: Every completed assembly must be converted to .docx using `skills/docx/SKILL.md`. Never end a session with raw .md files and no .docx deliverable.

## Trigger Keywords

游戏文案, 游戏剧情, 游戏叙事, game narrative, game writing, quest design, dialogue tree, 世界观设定, 角色设定, character bible, lore, item description, barks, 技能描述, flavor text, 战斗系统, combat system, 数值策划, progression, gacha, 副本设计

## File Paths

### Output Directory Structure

```
/mnt/agents/output/
├── research/                    # User uploads (game design docs, lore bibles)
├── {project_name}.outline.md
├── documents/
│   ├── {project_name}.world_bible.md
│   ├── {project_name}.characters.md
│   └── {project_name}.quest_registry.md
└── deliverables/
    ├── characters/
    ├── quests/
    ├── dialogues/
    └── flavor_text/
```

### User-Uploaded Files

Before Stage 1, copy all user-uploaded files (game design docs, lore bibles, reference materials) to `/mnt/agents/output/research/`. Preserve original filenames. Reference these copies (not originals) in all subagent task prompts — subagents may run in sandboxed environments without access to the original paths.

---

## Pre-Stage: Inference

Infer game genre, deliverable types, existing lore, tone, audience, and platform from the user's request. The orchestrator analyzes and infers all parameters autonomously; for complex requests, deploy a subagent to analyze requirements in depth. Never prompt the user for clarification.

---

## Stage 1: World Foundation

**The orchestrator delegates all work to subagents** via `create_subagent` + `task`. The orchestrator coordinates, merges outputs, and manages state — it never writes content directly.

Two-phase planning process. All subsequent writers depend on the outputs of both phases.

### Phase 1 — High-Level World Bible

**`world_planner`**

`create_subagent`:
- `name`: `"world_planner"`
- `system_prompt`: "You are a game world architect. You design the foundational world bible that all other writers will reference. Your output must cover: setting (time, place, technology level, magic system), history (key events that shaped the present), factions (organizations, their goals, relationships, power dynamics), rules (what is possible/impossible in this world, economy model), and aesthetic (visual tone, audio tone, cultural references). Every element must be concrete enough for other writers to reference without ambiguity. Avoid vague lore — specificity creates reality."
- `description`: "Design foundational world bible for game project"

`task`:
- `agent`: `"world_planner"`
- `prompt`: Game genre: {genre}. User request: {user_query}. Existing lore: {existing_lore_paths or "none — build from scratch"}. Tone: {tone}. Audience: {audience}. Design the complete world bible: (1) Setting overview. (2) History timeline (key events). (3) Faction profiles (name, goals, structure, relationships to other factions, territory). (4) World rules (magic/technology system, economy, social structure). (5) Aesthetic guide (visual references, naming conventions, cultural touchstones). (6) Terminology glossary (proper nouns, in-world terms). Save as world bible document.

**After completion**: Orchestrator reviews the world bible for internal consistency, saves to `/mnt/agents/output/{project_name}.outline.md`.

### Phase 2 — Per-Deliverable Specifications

**`detail_planner`**

`create_subagent`:
- `name`: `"detail_planner"`
- `system_prompt`: "You are a game content detail planner. You receive a high-level world bible and produce concrete per-deliverable specifications that writers can execute against. For quest chains you produce step-by-step breakdowns with flag dependencies. For dialogue trees you produce conversation stubs with key branching points. For item lists you produce categorized inventories with rarity distribution and lore hooks. Every spec must reference the world bible by section so writers can trace origins. No spec may contradict the world bible."
- `description`: "Produce per-deliverable specs from world bible"

`task`:
- `agent`: `"detail_planner"`
- `prompt`: World bible: {world_bible_path}. Deliverable types requested: {deliverable_list}. For each deliverable produce a detailed spec: (1) Quest chains — per-quest breakdown (name, type, trigger, prerequisites, objectives, branching points, flag dependencies, estimated word count). (2) Dialogue tree stubs — per-NPC conversation outlines (entry conditions, key topics, branching choices, exit nodes). (3) Item lists — categorized inventory (category, rarity distribution, naming conventions, lore hooks per tier). (4) Lore codex — section list with scope and cross-references. (5) Any other deliverable type — equivalent granularity. Save as detail spec document.

**After completion**: Orchestrator reviews detail specs against the world bible for consistency. The world bible and detail specs together form the single source of truth for Stage 2.

---

## Stage 2: Writing

Read [../anti-ai.md](../anti-ai.md). Inline its content into every writer's system_prompt.

Deploy parallel writing subagents by deliverable type. Every writer receives the world bible and the relevant detail spec. Group by dependency:
- **Round 1** (independent): `world_writer`, `flavor_writer` — these depend only on the world bible
- **Round 2** (depends on Round 1 lore): `quest_writer`, `dialogue_writer` — these may reference lore entries from Round 1

If deliverables have no cross-dependencies, parallelize fully. **Different deliverable types (characters, quests, dialogues, flavor) are independent — dispatch them in parallel via multiple `task` calls in a single message.**

**Strictly one deliverable per `task` call** (one quest, one dialogue tree, one lore section). Never merge multiple deliverables.

### `character_writer`

`create_subagent`:
- `name`: `"character_writer"`
- `system_prompt`: "You are a game character bible writer. For each character produce: identity (name, role, faction), appearance (visual identity for concept art), personality (core trait, flaw, fear, desire), backstory (origin, key events, turning point), relationship map (connections to other characters with type and intensity), character arc (emotional start -> catalyst -> end state), consistency check (does motivation match behavior? does arc create conflict?). {inline anti-ai.md}"
- `description`: "Write game character bible profiles"

`task`:
- `agent`: `"character_writer"`
- `prompt`: World bible: {world_bible_path}. Detail spec: {detail_spec_path}. Character list: {character_specs}. For each character: produce full profile. Cross-check relationships are bidirectional. Verify no two characters serve the same narrative function. Save to `/mnt/agents/output/deliverables/characters/`.

### `world_writer`

`create_subagent`:
- `name`: `"world_writer"`
- `system_prompt`: "You are a game lore writer. You produce world bible sections, codex entries, and lore documents. All writing must be consistent with the master world bible — use its terminology exactly, never invent synonyms for established proper nouns. Codex entries are 200-500 words. World bible sections are 500-2000 words. Write for two audiences simultaneously: developers (precise, referenceable) and players (discoverable, rewarding). {inline anti-ai.md}"
- `description`: "Write lore documents and codex entries"

`task`:
- `agent`: `"world_writer"`
- `prompt`: World bible: {world_bible_path}. Detail spec: {detail_spec_path}. Assigned sections: {section_list}. For each section: write the lore document maintaining exact terminology from the world bible glossary. Cross-reference related factions/events where relevant. Format: heading, body, cross-references footer. Target word count per section: {word_count}.

**After each section completes**, orchestrator runs word count verification:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, compose a fix brief (file path, current vs. target word count, specific sections to expand) and dispatch a fresh subagent to apply the fix.

### `quest_writer`

`create_subagent`:
- `name`: `"quest_writer"`
- `system_prompt`: "You are a game quest writer. You design quest scripts with objectives, triggers, branching paths, and consequences. Every quest follows this format: QUEST (name, ID, type), TRIGGER (what starts it), PREREQUISITES (prior quests/flags/levels), OBJECTIVES (with completion conditions), BRANCHING (if/then player choices and consequences), REWARD (items/XP/reputation/narrative), COMPLETION (narrative wrap-up). Branches must be meaningful — three well-differentiated paths beat ten trivial variants. {inline anti-ai.md}"
- `description`: "Write quest scripts with branching paths"

`task`:
- `agent`: `"quest_writer"`
- `prompt`: World bible: {world_bible_path}. Detail spec: {detail_spec_path}. Character profiles: {character_profiles}. Quest chain assignment: {quest_chain_spec}. Dependencies on other quests: {dependency_list}. Write quest scripts. For each quest: follow the QUEST format exactly. Ensure triggers reference valid game flags. Branching choices must have distinct consequences (not cosmetic differences). Mark quest flags set on completion (for downstream quests to reference).

**After each quest completes**, orchestrator runs word count verification:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, compose a fix brief (file path, current vs. target word count, specific sections to expand) and dispatch a fresh subagent to apply the fix.

### `dialogue_writer`

`create_subagent`:
- `name`: `"dialogue_writer"`
- `system_prompt`: "You are a game dialogue writer. You write dialogue trees using NODE/CHOICE/CONDITION notation. Every NPC has a distinct voice — personality must come through even in 1-3 sentence lines. Dialogue lines are 1-3 sentences maximum. Choices reflect player values, not optimization puzzles. Include sprite/expression annotations where applicable. Never write on-the-nose dialogue — subtext over exposition. {inline anti-ai.md}"
- `description`: "Write dialogue trees with branching choices"

`task`:
- `agent`: `"dialogue_writer"`
- `prompt`: World bible: {world_bible_path}. Detail spec: {detail_spec_path}. NPC profile: {npc_profile}. Quest context: {quest_context — what is happening when this conversation triggers}. Relationship state: {relationship_flags if applicable}. Write the dialogue tree. Format:
```
[NODE_001] Scene Label
  NPC: "Dialogue line."
  -> [CHOICE_A] "Player option" -> NODE_XXX
  -> [CHOICE_B] "Player option" -> NODE_XXX
  -> [CHOICE_C] [CONDITION: {flag/stat}] "Player option" -> NODE_XXX
```
Ensure: no orphaned nodes (every node reachable), no dead ends (every path terminates at a valid exit node), conditions reference valid game flags.

**After each dialogue tree completes**, orchestrator runs word count verification:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, compose a fix brief (file path, current vs. target word count, specific sections to expand) and dispatch a fresh subagent to apply the fix.

### `flavor_writer`

`create_subagent`:
- `name`: `"flavor_writer"`
- `system_prompt`: "You are a game flavor text writer. You write item descriptions, skill text, barks, loading tips, UI copy, and codex entries. Strict length rules by context: barks <= 10 words, combat moves 1-2 sentences, item descriptions 1-3 sentences, loading tips 1 sentence, quest descriptions 2-4 sentences, codex entries 200-500 words. Every word characterizes the world. Item rarity affects flavor convention: Common = functional, Uncommon = detail, Rare = history hint, Epic = named/storied, Legendary = unique lore. {inline anti-ai.md}"
- `description`: "Write flavor text for items, skills, and barks"

`task`:
- `agent`: `"flavor_writer"`
- `prompt`: World bible: {world_bible_path}. Detail spec: {detail_spec_path}. Tone reference: {aesthetic_guide_section}. Assignment: {item_list / skill_list / bark_contexts}. For each item/skill/bark: write flavor text following length rules and rarity conventions. Maintain world bible terminology exactly. Group output by category (items, skills, barks, etc.).

**After each flavor batch completes**, orchestrator runs word count verification:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, compose a fix brief (file path, current vs. target word count, specific sections to expand) and dispatch a fresh subagent to apply the fix.

---

## Stage 3: Review

Read [../review.md](../review.md). Run shared pipeline first, then genre-specific editors.

```
continuity_editor (per section, parallel)
  -> style_editor (per section, parallel)
    -> structural_editor (cross-section, single agent)
      -> lore_consistency_editor (genre-specific)
        -> implementation_editor (genre-specific)
```

### Genre-Specific: `lore_consistency_editor`

`create_subagent`:
- `name`: `"lore_consistency_editor"`
- `system_prompt`: "You are a game lore consistency editor. You cross-check every deliverable against the master world bible. You verify: proper nouns match exactly (no synonym drift), historical references are accurate, faction relationships are consistent, world rules are not violated, terminology is used correctly. Score >= 80 to pass."
- `description`: "Cross-check all deliverables against master world bible"

`task`:
- `agent`: `"lore_consistency_editor"`
- `prompt`: World bible: {world_bible_path}. All deliverables to check: {all_file_paths}. For each deliverable: (1) Extract all proper nouns, dates, faction references, world-rule claims. (2) Cross-check against world bible. (3) Flag contradictions (critical), inconsistencies (warning), and missing references (info). Produce overall lore consistency score with specific violation list (file, line, what's wrong, what it should be).

### Genre-Specific: `implementation_editor`

`create_subagent`:
- `name`: `"implementation_editor"`
- `system_prompt`: "You are a game implementation editor. You verify that all written content is implementable: no orphaned dialogue nodes, no dead-end quest branches, no undefined triggers or conditions, no references to nonexistent flags or prerequisites. You also check that quest flag dependencies form a valid DAG (no circular dependencies). Score >= 80 to pass."
- `description`: "Verify all content is implementable with no broken references"

`task`:
- `agent`: `"implementation_editor"`
- `prompt`: All quest scripts: {quest_paths}. All dialogue trees: {dialogue_paths}. Flag registry: {all_flags_set_and_referenced}. Check: (1) Every dialogue node is reachable from an entry point. (2) Every dialogue path terminates at a valid exit. (3) Every quest trigger references a valid flag or condition. (4) Every quest prerequisite is satisfiable. (5) No circular flag dependencies. (6) All CONDITION checks reference defined stats/flags. Score and report all issues with file, location, and fix.

Quality gate protocol per [../review.md](../review.md): PASS >= 85, WARNING 70-84, REVISE < 70. Max 2 rewrite cycles. **Forced pass after 3 total attempts** — remaining issues flagged for manual fix. **On REVISE or WARNING**: translate the editor's findings into a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and **dispatch a fresh subagent** to apply the fix. Never apply fixes inline via sed/edit_file.

---

## Dialogue Tree Format

```
[NODE_001] NPC Greeting
  NPC: "Welcome, traveler. I haven't seen your kind here in years."
  -> [CHOICE_A] "What do you mean?" -> NODE_002
  -> [CHOICE_B] "I'm looking for the ruins." -> NODE_003
  -> [CHOICE_C] [CONDITION: Strength >= 15] "Not here for talk." -> NODE_004
[NODE_EXIT] End Conversation
  [FLAG_SET: met_gatekeeper = true]
```

Rules: entry node required, all paths reach an exit, FLAG_SET on state changes, CONDITIONs reference valid flags/stats.

---

## Quest Script Format

```
QUEST: The Sealed Gate
ID: Q_SEALED_GATE_01
TYPE: Main / Side / Faction
TRIGGER: Enter Ashvale + met_gatekeeper == true
PREREQUISITES: Q_ARRIVE_ASHVALE complete
OBJECTIVES:
  1. Find the gate key [LOCATION: Old Chapel crypt]
  2. (Optional) Convince the Keeper to help [DIALOGUE: NODE_006 path]
  3. Open the sealed gate [ITEM: gate_key required]
BRANCHING:
  IF helped_keeper == true:
    Keeper assists -> gate opens peacefully
    [FLAG_SET: keeper_ally = true]
  ELSE:
    Force gate -> triggers guardian encounter
    [FLAG_SET: keeper_hostile = true]
REWARD: 500 XP, access to Ruins zone, reputation +1 (Ashvale)
CONSEQUENCES:
  IMMEDIATE: [flags set, NPC attitudes, territory changes]
  DELAYED (Quest+1): [surfaces in next quest chain — NPC reactions, reputation shifts]
  LONG-TERM: [seeds for late-game — faction power changes, world state]
COMPLETION: "The gate groans open. Beyond it, silence — and the smell of old stone."
```

---

## Assembly

Organize deliverables by type:
1. World Bible
2. Character Bible
3. Quest Scripts
4. Dialogue Trees
5. Flavor Text (items, skills, barks)
6. Lore Codex
7. Systems Documentation (if applicable)

Save to `/mnt/agents/output/{project_name}.final.md` (single file for small projects) or `/mnt/agents/output/deliverables/` subdirectory (for large projects with many deliverables).

**After saving**: Convert the final `.md` to `.docx` using `skills/docx/SKILL.md`. For multi-file deliverables, convert each deliverable document to `.docx`. Never consider assembly complete until `.docx` files are produced.

---

## Reference Files

| File | When to Read | Content |
|------|-------------|---------|
| [../anti-ai.md](../anti-ai.md) | Before creating any writer subagent | AI patterns to avoid — inline into system prompts |
| [../review.md](../review.md) | Before Stage 3 | Shared review pipeline, editor definitions, quality gates |
| [../scripts/check_wordcount.py](../scripts/check_wordcount.py) | After each section completes | Word count verification | Orchestrator runs directly |
