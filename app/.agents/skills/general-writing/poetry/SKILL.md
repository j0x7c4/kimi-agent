---
name: poetry
type: capability
description: >
  Poetry writing — free verse, formal verse, classical Chinese poetry, modern poetry,
  prose poetry, and all poetic forms. Handles meter, rhyme, imagery, compression,
  line breaks, and the music of language.
---

# Poetry Writing

Orchestrator dispatches all creation and review work to subagents. Before creation, copy user-uploaded files to `/mnt/agents/output/research/`.

Sub-skill of [general-writing](../SKILL.md). Inherits shared creative writing principles, anti-AI discipline, and quality gate framework.

> **CRITICAL — Review → Fix Brief → Dispatched Subagent**: When a review finds issues, translate them into a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh `poetry_writer` subagent to apply the fix. Never use inline sed/edit_file fixes.

> **CRITICAL — Anti-Read-Loop Rule**: The orchestrator must dispatch its first subagent (poetry_writer) within 10 iterations. If the orchestrator has spent 10+ iterations only reading files without creating any subagent, it is in a read-loop. Stop reading, draft your poetic blueprint from what you have, and dispatch the writer immediately.

> **CRITICAL — .docx Delivery**: Every completed poem or collection must be converted to .docx using `skills/docx/SKILL.md`. Never end a session with raw draft files and no .docx deliverable.

## File Paths

```
Output: /mnt/agents/output/
  {project_name}.{poem_title}.md        # Individual poems
  {project_name}.collection.md          # Collection assembly (if applicable)
  research/                              # User uploads (reference poems, prompts)
```

## Trigger Keywords

诗, 词, poem, poetry, sonnet, haiku, 律诗, 绝句, 自由诗, verse, ode, 现代诗, 散文诗, 古诗, 打油诗, limerick, villanelle, 赋, 古体诗, 近体诗

## Workflow Decision Tree

```
User Query
  │
  ├─ Provides draft + asks for revision → Stage 3 → Stage 4
  ├─ Specifies form/theme clearly → Stage 1 → Stage 2 → Stage 3 → Stage 4
  └─ Vague request → Infer parameters (see below) → Stage 1 → Stage 2 → Stage 3 → Stage 4
```

Infer form category, language, theme, tone, length, and poet persona from the user's request. The orchestrator analyzes and infers all parameters autonomously; for complex requests, deploy a subagent to analyze requirements in depth. Never prompt the user for clarification.

### Persona Categories (for system prompt construction)

| Category | Example Voices | Key Traits to Inline |
|----------|---------------|---------------------|
| Classical Chinese | 李白 (豪放), 杜甫 (沉郁), 苏轼 (旷达), 李清照 (婉约) | Li Bai: landscape scale, wine/moon, hyperbole. Du Fu: social suffering, dense allusion, strict form. |
| English Romantic | Keats, Shelley, Wordsworth | Keats: lush sensory, ode form, mortality-beauty. Shelley: political fire. |
| Modernist | Eliot, Pound, Stevens | Eliot: fragmented collage, allusion density. Pound: sharp image. |
| Contemporary | Ocean Vuong, 余秀华, 北岛 | Vuong: body-as-landscape. 余秀华: raw rural voice. 北岛: political compression. |
| Prose-Poetry / Fabulist | Calvino, Borges, Lightman, Ted Chiang | Calvino: structural play, deceptive simplicity. Borges: labyrinthine ideas, casual profundity. Lightman: physics-as-metaphor. Chiang: speculative premise → human truth. Shared: concrete imagery, philosophical undercurrent without didacticism, dreamy-but-precise. |

Inline the selected persona's voice traits into the writer system prompt — not just the name.

## Stage 1: Conception

Orchestrator produces a **poetic blueprint** containing:

1. **Form constraints** (explicit, not by reference):
   - Free verse: line break strategy, rhythm approach
   - Formal verse: meter, rhyme scheme, structural rules (e.g., sonnet: 14 lines, iambic pentameter, ABAB CDCD EFEF GG, volta at line 9)
   - Classical Chinese 律诗: 8 lines, 5 or 7 chars/line, 平仄 pattern, 对仗 in 颔联/颈联, 韵脚
   - Classical Chinese 绝句: 4 lines, 5 or 7 chars/line, 平仄, 韵脚
   - 词: by 词牌 — specific pattern of line lengths, tonal patterns, rhyme positions
2. **Central image/metaphor** and emotional arc
3. **Key imagery field**: 5-10 concrete images around the theme
4. **Sonic texture goals**: harsh consonants for tension? Flowing vowels for peace?
5. **Poet persona voice traits** (if activated)

Save to `/mnt/agents/output/{filename}.agent.outline.md`.

## Stage 2: Creation

**Read [../anti-ai.md](../anti-ai.md) — inline its content into writer system prompts.**

**ALWAYS horse-race 2-3 drafts** for short poems (< 30 lines). Each draft explores a different axis:
- Draft A: different structural approach (couplets vs. tercets, linear vs. fragmented)
- Draft B: different imagery system (botanical vs. architectural vs. bodily)
- Draft C: different tonal register (intimate whisper vs. public declaration vs. ironic detachment)

For poems > 30 lines: horse-race the opening stanza and closing stanza rather than the entire poem.

For collections: **strictly one poem per `task` call.** One subagent per poem, with a master theme guide passed to all. Sequence poems for a reading arc.

`create_subagent`:
- `name`: `"poetry_writer"`
- `system_prompt`: Compose from these elements: (1) Role: "You are a poet writing [form] poetry." (2) Form constraints: Inline the full form rules from the blueprint (meter, rhyme, line count, 平仄 grid if classical). (3) Poet persona voice (if activated): Inline specific voice traits — rhythm tendencies, preferred imagery, thematic obsessions, signature techniques. (4) Anti-AI poetry patterns: Inline from `../anti-ai.md` plus poetry-specific rules: "No 'tapestry of emotions.' No 'dance of light and shadow.' No abstract noun + abstract noun. No cliche nature imagery without subversion. No explaining the metaphor. Trust the image. Concrete over abstract. Every word earns its place." (5) Sound awareness: "Attend to vowel music, consonant texture, line breaks as meaning-makers. Enjambment is a tool for surprise and emphasis, not laziness."
- `description`: "Write poetry drafts per blueprint constraints"

`task`:
- `agent`: `"poetry_writer"`
- `prompt`: "Write [form] poem on [theme/subject]. Draft [A/B/C] — explore [specific axis for this draft]. Length: [target lines]. Central image: [image]. Emotional arc: [arc]. Sonic texture: [goals]." Include blueprint file path, any reference poems or style models the user provided.

Save each draft to `/mnt/agents/output/{filename}_draft_{A|B|C}.md`.

### Word Count Verification

After each completed poem, orchestrator runs:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, return to writer with expansion instructions.

## Stage 3: Review

**Read [../review.md](../review.md) first. Follow the shared pipeline, then add genre-specific editors.**

### Shared Pipeline (from review.md)

For single poems, `continuity_editor` and `structural_editor` are lightweight (skip if poem < 20 lines). `style_editor` runs on all drafts.

### Genre-Specific Editors (after shared pipeline)

**1. `form_checker`** — Formal verse and classical Chinese only. Skip for free verse.

`create_subagent`:
- `name`: `"form_checker"`
- `system_prompt`: "You verify formal poetry constraints. For sonnets: scan iambic pentameter, check volta placement, verify rhyme scheme. For classical Chinese: verify 平仄 pattern, 对仗 quality in required couplets, 韵脚 consistency. For haiku: 5-7-5 syllable/mora count, season word (kigo), cutting word (kireji). For villanelle/sestina: verify refrain and word-repetition rules. Output: PASS or FAIL with specific violations."
- `description`: "Verify formal verse constraints"

`task`:
- `agent`: `"form_checker"`
- `prompt`: Include poem file path, form constraints from blueprint.

**Iterative loop**: flag violations → writer revises → re-check. Max 2 rounds. Form compliance must be >= 80 for formal verse. For collections: if a poem fails review twice, mark remaining issues and move on.

**2. `sound_editor`** — Runs on all forms including free verse.

`create_subagent`:
- `name`: `"sound_editor"`
- `system_prompt`: "You assess the phonetic quality of poetry. Check: (1) euphony/cacophony matches emotional content; (2) internal rhyme, alliteration, assonance are purposeful; (3) line-break placement makes meaning (not arbitrary); (4) enjambment used for effect; (5) read-aloud test — natural rhythm when spoken; (6) opening strength — first line must arrest (sensory immersion, immediate declaration, or temporal dislocation — not throat-clearing); (7) closing resonance — final line/image must land with transformed echo, unanswered question, or open possibility — not summary or restatement. Flag monotone line lengths as algorithmic."
- `description`: "Assess phonetic quality and sound craft"

`task`:
- `agent`: `"sound_editor"`
- `prompt`: Include poem file path, sonic texture goals from blueprint.

### Scoring Dimensions

| Dimension | Weight | Check |
|-----------|--------|-------|
| Image precision | 30% | Concrete, original images; central metaphor coherence |
| Sound craft | 25% | Euphony, rhythm, line-break intention, enjambment |
| Form compliance | 20% | Meter, rhyme, 平仄/对仗 (0% for free verse — redistribute to image and sound) |
| Emotional resonance | 15% | Evokes feeling through image and sound, not statement |
| Compression | 10% | Every word earns its place; no padding |

**Pass**: >= 75 overall. Form compliance >= 80 for formal verse.

## Stage 4: Selection and Assembly

1. Present all draft variants to the user with brief notes on each draft's approach
2. User selects or requests synthesis of elements from multiple drafts
3. If synthesis requested: dispatch `poetry_writer` with selected elements as constraints
4. Save final poem(s) to `/mnt/agents/output/{filename}.agent.final.md`
5. Convert to .docx using the `md2docx` pipeline (see `skills/docx/SKILL.md` → `references/md2docx-reference.md`). Output: `/mnt/agents/output/{filename}.agent.final.docx`. **This step is mandatory.** Raw .md without a .docx deliverable is not an acceptable end state.
6. For collections: include table of contents and reading arc notes

## Reference Files

| File | Purpose | When to Read | Who Runs |
|------|---------|--------------|----------|
| [../anti-ai.md](../anti-ai.md) | AI patterns to avoid — inline into system prompts | Before creating any writer subagent | Orchestrator inlines into subagent |
| [../review.md](../review.md) | Shared review pipeline, editor definitions, quality gates | Before Stage 3 | Orchestrator follows |
| Blueprint (`agent.outline.md`) | Form constraints, central image, sonic goals, persona traits | Generated in Stage 1 | Orchestrator creates, subagents consume |
| [../scripts/check_wordcount.py](../scripts/check_wordcount.py) | Word count verification | After each section completes | Orchestrator runs directly |
