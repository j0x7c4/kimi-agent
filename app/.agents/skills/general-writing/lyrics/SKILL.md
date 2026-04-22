---
name: lyrics
type: capability
description: >
  Lyrics and songwriting — original lyrics for pop, rock, hip-hop, R&B, folk,
  electronic, classical vocal, Chinese-style (中国风), and all musical genres.
  Handles verse-chorus structure, rhyme schemes, syllable fitting, hook writing,
  singability, and AI music platform integration.
---

# Lyrics Writing

Orchestrator dispatches all creation and review work to subagents. Before creation, copy user-uploaded files to `/mnt/agents/output/research/`.

Sub-skill of [general-writing](../SKILL.md). Inherits shared creative writing principles, anti-AI discipline, and quality gate framework.

> **CRITICAL — Review → Fix Brief → Dispatched Subagent**: When a review finds issues, translate them into a detailed fix brief (file paths, quoted findings, expected outcome, scope boundary, self-check) and dispatch a fresh `lyrics_writer` subagent to apply the fix. Never use inline sed/edit_file fixes.

> **CRITICAL — Anti-Read-Loop Rule**: The orchestrator must dispatch its first subagent (lyrics_writer) within 10 iterations. If the orchestrator has spent 10+ iterations only reading files without creating any subagent, it is in a read-loop. Stop reading, draft your structural plan from what you have, and dispatch the writer immediately.

> **CRITICAL — .docx / .txt Delivery**: Every completed song must be converted to .docx using `skills/docx/SKILL.md`. For Suno/AI music platform targets, also produce a `.txt` file with meta-tags. Never end a session with only raw section files and no assembled deliverable.

## File Paths

```
Output: /mnt/agents/output/
  {project_name}.{song_title}.md        # Song lyrics
  {project_name}.{song_title}.suno.txt  # Suno meta-tags (if requested)
  research/                              # User uploads (melody refs, mood boards)
```

## Trigger Keywords

歌词, lyrics, 填词, songwriting, 作词, chorus, verse-chorus, hook, 说唱词, rap lyrics, 中国风歌词, Suno, AI music, 古风歌词

## Workflow Decision Tree

```
User Query
  │
  ├─ Provides existing lyrics + asks for revision → Stage 3 → Assembly
  ├─ Provides melody/structure + asks for lyrics → Stage 2 → Stage 3 → Assembly
  └─ New request → Infer parameters (see below) → Stage 1 → Stage 2 → Stage 3 → Assembly
```

Infer genre, structure, emotional arc, melody reference, target platform, and language register from the user's request. The orchestrator analyzes and infers all parameters autonomously; for complex requests, deploy a subagent to analyze requirements in depth. Never prompt the user for clarification.

## Stage 1: Conception

Orchestrator produces a **structural plan**:

1. Section order (from template, adjusted to song's needs). Common templates:
   - Pop: `V1 → Pre-C → Chorus → V2 → Pre-C → Chorus → Bridge → Final Chorus`
   - Ballad: `V1 → V2 → Chorus → V3 → Chorus → Bridge → Final Chorus`
   - Hip-hop: `Intro → V1 (16 bars) → Hook → V2 (16 bars) → Hook → Bridge → Hook → Outro`
   - 古风: `起 → 承 → [Interlude] → 转 → 合`
2. Syllable targets per line (critical if melody exists)
3. Rhyme scheme per section (e.g., Verse: ABAB, Chorus: AABB)
4. Hook concept: the central lyrical idea in one sentence
5. Emotional trajectory mapped to structure (verse = setup, pre-chorus = tension, chorus = peak, bridge = shift)
6. If melody reference provided: extract syllable counts per phrase, stress patterns, breath points
7. If for AI music platform: draft style tags (genre, instrumentation, vocal style, mood, tempo — 300-500 chars)

Save to `/mnt/agents/output/{filename}.agent.outline.md`.

## Stage 2: Creation

**Read [../anti-ai.md](../anti-ai.md) — inline its content into writer system prompts.**

**Write chorus FIRST.** The chorus is the song's center of gravity. **Horse-race 2-3 chorus variants** — dispatch parallel subagents with different approaches.

**Strictly one section per `task` call** (chorus, verse, bridge each dispatched separately).

`create_subagent`:
- `name`: `"lyrics_writer"`
- `system_prompt`: Compose from these elements: (1) Role: "You are a songwriter writing [genre] lyrics in [language]." (2) Song structure template: Inline the full section order, line counts, and emotional arc per section. (3) Singability rules: "Singability overrides literary merit. Every line must pass the read-aloud test. Rules: (a) stressed syllables land on downbeats; (b) breath points at natural grammatical breaks; (c) no consonant clusters (str-, spl-, nkths) on fast passages; (d) open vowels (ah, oh, oo, ee) on sustained/high notes; (e) closed vowels (uh, ih) never on held notes." (4) Genre conventions: Pop — conversational register, emotional directness, strong hook; Hip-hop — internal rhyme density, wordplay, flow, punch lines; 古风 — classical imagery (意象), 四字词, 典故, elegant register; Ballad — emotional vulnerability, simple language, quiet-to-intense build. (5) Anti-AI rules: Inline from `../anti-ai.md` plus lyrics-specific: "No 'journey of self-discovery.' No 'stand tall in the face of adversity.' No 'wings to fly' / 'light in the darkness' without earned context. No perfectly grammatical singing — use contractions, fragments, repetition. No every-line-same-length." (6) Narrative-to-lyric rule: "When source material is a story, concept, or experience, convert to metaphor and sensory imagery. FORBIDDEN: naming literal specifics (place names, dates, technical terms) unless they serve as deliberate poetic anchors. Test: could a listener not in on the context still feel the emotion? If no, it's too literal."
- `description`: "Write song lyrics per structural plan"

**Dispatch chorus horse-race** — `task` (2-3 parallel):
- `agent`: `"lyrics_writer"`
- `prompt`: "Write [genre] chorus. Hook concept: [concept]. Variant [A/B/C] — explore [different hook phrasing / different imagery / different rhythmic pattern]. Rhyme scheme: [scheme]. Syllable targets: [targets]. This is the emotional peak of the song."
- Save each to `/mnt/agents/output/{filename}_chorus_{A|B|C}.md`

**Present chorus variants to user.** After selection:

**Dispatch remaining sections** — `task` (one section per call):
- `agent`: `"lyrics_writer"`
- `prompt`: "Write [section name] for [genre] song. Chorus (selected): [inline or path]. Emotional arc position: [setup/tension/shift/resolution]. Rhyme scheme: [scheme]. Syllable targets: [targets]. Tempo guidance: [BPM feel or qualitative]. The verse must build toward the chorus; the bridge must contrast it." Include structural plan, selected chorus, melody reference (if exists).
- Save to `/mnt/agents/output/{filename}_sec{NN}.md`

### Word Count Verification

After each completed section, orchestrator runs:
```
python skills/general-writing/scripts/check_wordcount.py <file> --min {target} --lang auto
```
If FAIL, return to writer with expansion instructions.

## Stage 3: Review

**Read [../review.md](../review.md) first. Follow the shared pipeline, then add genre-specific editor.**

### Shared Pipeline (from review.md)

For lyrics (short form), `continuity_editor` is lightweight. `style_editor` checks AI-pattern absence and voice consistency across sections. `structural_editor` verifies emotional arc and section balance.

### Genre-Specific Editor

**`singability_checker`** — The critical lyrics-specific reviewer.

`create_subagent`:
- `name`: `"singability_checker"`
- `system_prompt`: "You perform phonetic analysis of lyrics for singability. Check: (1) syllable stress alignment with intended downbeats; (2) breath point placement at natural phrase boundaries; (3) consonant clusters that would be unsingable at tempo; (4) vowel quality on sustained/high notes (open vowels required); (5) tongue-twister detection; (6) line length variation (monotone lengths = algorithmic). Output: PASS or FAIL with specific line numbers and fixes."
- `description`: "Phonetic singability analysis"

`task`:
- `agent`: `"singability_checker"`
- `prompt`: Include all section file paths, structural plan (syllable targets, tempo), melody reference if available.

**Iterative loop**: flag unsingable phrases → write a fix brief (specific lines, phonetic issues, suggested alternatives) and dispatch a fresh `lyrics_writer` subagent to apply the fix → re-check. Max 2 rounds. For multi-song projects: if a song fails review twice, mark remaining issues and move on.

### Scoring Dimensions

| Dimension | Weight | Check |
|-----------|--------|-------|
| Singability | 30% | Natural mouth feel, stress alignment, breath points, vowel quality |
| Hook memorability | 25% | Chorus sticks after one read; hook is catchy and resonant. Floor: 70 |
| Rhyme craft | 20% | Scheme consistency, no forced rhymes, internal rhyme in verses |
| Emotional arc | 15% | Song progresses emotionally, not repeated sentiment |
| Syllable precision | 10% | Line lengths match melodic rhythm (if melody provided) |

**Pass**: >= 75 overall. Hook memorability must be >= 70.

## Suno/AI Music Integration

When target platform is Suno, Udio, or similar:

1. **Metatag format**: Use standard section markers on their own lines:
   ```
   [Intro] [Verse 1] [Pre-Chorus] [Chorus] [Bridge] [Instrumental] [Outro]
   ```
2. **Style tags**: Include at top of final file. Format: genre + subgenre, instrumentation, vocal style, mood/dynamics, tempo (300-500 chars)
3. **Lyrics-music alignment**: sparse lyrics for slow songs, denser for uptempo; place strongest emotional words at melodic peaks; chorus lyrics must carry repetition; use `[Instrumental]` and `[Break]` for breathing room

## Translation / Adaptation Mode

When user provides lyrics in one language and requests adaptation to another:
- Match syllable count per line (+-2 syllables acceptable)
- Preserve stressed syllables on downbeats across languages
- Reimagine culturally untranslatable expressions (don't literal-translate idioms)
- Apply `singability_checker` to BOTH source and target versions
- Prioritize how the line sounds sung over literal accuracy

## Assembly

1. Concatenate all sections in structural order with section labels: `[Verse 1]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Outro]`, etc.
2. If Suno/AI platform: prepend style tags at top of file
3. Save to `/mnt/agents/output/{filename}.agent.final.md`
4. Convert to .docx using the `md2docx` pipeline (see `skills/docx/SKILL.md` → `references/md2docx-reference.md`). Output: `/mnt/agents/output/{filename}.agent.final.docx`. For Suno/AI platform targets, the `.suno.txt` file is also a primary deliverable.

**Delivery is mandatory.** Raw section files without an assembled deliverable (.docx or .txt) is not an acceptable end state.

## Reference Files

| File | Purpose | When to Read | Who Runs |
|------|---------|--------------|----------|
| [../anti-ai.md](../anti-ai.md) | AI patterns to avoid — inline into system prompts | Before creating any writer subagent | Orchestrator inlines into subagent |
| [../review.md](../review.md) | Shared review pipeline, editor definitions, quality gates | Before Stage 3 | Orchestrator follows |
| Structural plan (`agent.outline.md`) | Section order, syllable targets, rhyme schemes, hook concept | Generated in Stage 1 | Orchestrator creates, subagents consume |
| [../scripts/check_wordcount.py](../scripts/check_wordcount.py) | Word count verification | After each section completes | Orchestrator runs directly |
