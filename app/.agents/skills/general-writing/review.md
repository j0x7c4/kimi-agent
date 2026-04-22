# Creative Writing Review Pipeline

> **Usage**: Orchestrator reads this file before Stage 3. It defines the shared review pipeline for all creative genres. Sub-skills may add genre-specific editors (listed in their own SKILL.md) but must not skip the shared editors.

## Pipeline Architecture

Review runs sequentially — each stage gates the next.

```
continuity_editor (per section, parallelizable)
  ↓ all sections pass
style_editor (per section, parallelizable)
  ↓ all sections pass
structural_editor (cross-section, single agent reads all)
  ↓ pass
[genre-specific editors — defined in sub-skill SKILL.md]
```

## Continuity Editor

**Scope**: One section at a time. Multiple editors can run in parallel.

**Create via** `create_subagent`:
```
system: "You are a continuity editor for creative writing. Your job is to verify
internal consistency. You receive state panels (characters, timeline, world rules)
and check the section against them. Output: PASS or FAIL with specific issues."
name: "continuity_editor"
```

**Task prompt must include**:
- File path of the section/chapter to review
- Path to the working outline (`outline.md`) — editor reads File Index to locate satellite files (characters, foreshadowing, threads, world, chapter_summaries) and reads them directly
- For fiction: do NOT inline satellite content — pass the outline.md path and let the editor read files from the shared workspace

**Review dimensions**:
1. Character name/trait consistency across sections
2. Timeline coherence (no contradictory sequences)
3. World-rule adherence (no violations of established logic)
4. POV discipline (no unintentional head-hopping or tense shifts)
5. Foreshadowing tracking (no setup without payoff, no payoff without setup)

**Decision**: PASS → proceed. FAIL → remediation brief → writer rewrite → re-review.

## Style Editor

**Scope**: One section at a time. Parallelizable.

**Create via** `create_subagent`:
```
system: "You are a style editor for creative writing. You check prose quality,
voice consistency, and AI-pattern absence. You receive anti-AI rules and the
genre's voice guidelines. Output: PASS or FAIL with line-level feedback."
name: "style_editor"
```

**Task prompt must include**:
- File path of the section
- Anti-AI rules (inline from `anti-ai.md` or pass path)
- Genre voice guidelines (from sub-skill)

**Review dimensions**:
1. AI-pattern scan (check against anti-ai.md checklist)
2. Voice consistency (each character sounds like themselves)
3. Rhythm and sentence variety
4. Word choice: concrete over abstract, precise over vague
5. Minimum depth test: if removing a paragraph doesn't weaken the piece, it's padding

## Structural Editor

**Scope**: Cross-section. Single agent reads all section files.

**Create via** `create_subagent`:
```
system: "You are a structural editor. You read the complete work and assess
pacing, transitions, arc completeness, and balance. Output: PASS or FAIL
with specific issues and locations."
name: "structural_editor"
```

**Task prompt must include**:
- Paths to all section files in order
- Outline for global structure reference

**Review dimensions**:
1. Pacing: dead zones or rushed sections?
2. Transitions between sections: natural or jarring?
3. Arc completeness: does the work deliver on its promise?
4. Redundancy: same points in multiple sections?
5. Balance: word counts proportional to importance?

## Quality Gate Protocol

Each stage produces a result: **PASS**, **WARNING**, or **REVISE**. For non-PASS results, the coordinator's job is to translate the review's findings into a detailed fix brief and dispatch a fresh subagent to apply the fix. A dispatched subagent with a good brief (file paths, quoted issues, expected outcome, scope boundary) produces much higher quality than inline edits, because the subagent can re-read context, verify state, and run its own self-checks.

**Scoring thresholds** (when quantitative scoring applies):

| Score | Status | Response |
|-------|--------|----------|
| ≥ 85 | PASS | Proceed |
| 75–84 | WARNING | Write a fix brief, dispatch a fresh writer subagent, re-score once |
| < 75 | REVISE | Write a detailed brief, dispatch a fresh writer subagent, re-review |

**Fix brief** must contain: (1) exact file paths, (2) quoted findings with line/paragraph refs, (3) expected outcome or target metrics, (4) scope boundary (what NOT to touch), (5) self-check to run before returning.

**Rewrite cycles**: max 2 per section. After the third attempt, FORCED PASS and add to backpatch queue with severity tags.

**Cross-section fixes**: when structural_editor flags inconsistency between Section 3 and Section 1, the brief for Section 3 must include the relevant excerpt from Section 1.

**Why dispatch rather than inline-edit**: a dispatched subagent re-reads full context, runs self-checks (em-dash/AI vocab/English scan), and preserves prose voice. Inline sed/edit_file commands miss edge cases, create broken fragments, and desync satellite files.

## Genre-Specific Editors

Sub-skills add these after the shared pipeline:

| Genre | Additional Editors |
|-------|-------------------|
| Fiction | `pacing_editor` (chapter rhythm, hooks) |
| Fanfiction | `canon_checker` (voice fidelity, canon facts) |
| Poetry | `form_checker` (meter, rhyme), `sound_editor` (phonetics) |
| Lyrics | `singability_checker` (syllable stress, breath points) |
| Drama | `performability_editor` (cast, staging, timing) |
| Screenplay | `format_checker` (industry standard), `visual_editor` (sound-off test) |
| Essay | `voice_editor` (distinctiveness, authenticity) |
| Murder Mystery | `logic_checker` (forward/backward pass), `spoiler_checker`, `balance_checker` |
| TRPG | `rules_checker` (stat blocks, DCs), `flow_editor` (dead ends, railroads) |
| Game Writing | `lore_consistency_editor`, `implementation_editor` (no orphaned nodes) |
| Letter | `tone_editor`, `authenticity_editor` (template test) |

---

## Backpatch Protocol

Run after all chapters/sections complete, if any items are queued. Executed by a dedicated `backpatch_agent` subagent — orchestrator dispatches but does not perform fixes.

### Queue Entry Conditions

Items enter the backpatch queue when:
- A chapter received FORCED pass after 3 review attempts (max rewrite cycles exceeded)
- Cross-chapter continuity issues found during structural review
- Foreshadowing registry has unresolved OPEN items after all chapters complete
- Volume boundary review flags cross-volume inconsistencies

### Processing Protocol

1. **Collect** all backpatch items from the queue.
2. **Sort by severity**:
   - CONTINUITY_BREAK (highest — factual contradictions)
   - CHARACTER_INCONSISTENCY (behavioral/state conflicts)
   - FORESHADOW_DANGLING (OPEN items never paid off)
   - STYLE_ISSUE (lowest — prose quality issues that passed FORCED)
3. **Per item**: identify minimal text span → generate fix → verify fix against satellite files → apply in-place → update `chapter_summaries.md` with the change.
4. **Re-verify**: dispatch `continuity_editor` on all modified chapters to confirm fixes don't introduce new issues.
5. **Final check**: verify foreshadowing registry — all items CLOSED or INTENTIONAL.

### Constraints

- **Max 2 paragraphs per fix.** If a fix requires more than 2 paragraphs of changes, escalate to user.
- **No cascading rewrites.** Each fix is local. If a fix implies changes to other chapters, those become separate backpatch items.
- **Satellite files updated.** Every backpatch fix that changes character state, timeline, or world facts must also update the relevant satellite file.
