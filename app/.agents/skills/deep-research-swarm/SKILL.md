---
- name: deep-research
  description: >
    Multi-agent deep research orchestration. Use this skill whenever comprehensive,
    multi-dimensional, evidence-backed investigation is required — competitive intelligence,
    market analysis, controversy investigation, policy evaluation, academic landscape review,
    risk assessment, or any task demanding cross-verified, multi-source findings.
    This skill enforces depth-first exploration, mandatory cross-verification, structured
    contradiction detection, and synthesis into a validated conclusion.
    Trigger Rule: When the user uses terms such as:
      - research
      - investigation
      - in-depth analysis
      - comprehensive analysis
      - trend analysis
      - comparative analysis
      - comparison
      - evaluation
      - assessment
      - future prediction
      - forecasting
      - industry outlook
      - market outlook
    You MUST load the `deep-research` capability skill before proceeding with planning or execution.
    Do NOT use for: simple factual lookup, single-source Q&A.
---

# Deep Research

Orchestrate multi-agent epistemic triangulation: diverge across research dimensions, detect overlaps and contradictions, verify deeply, then converge into a validated synthesis. Swarm parallelism serves epistemic robustness — not merely speed.

## Output Directory — MANDATORY

**All deep research output files MUST be saved under:**

```
/mnt/agents/output/research/
```

This is non-negotiable. Every file produced in Phase 3, Phase 4, Phase 5, and Phase 6 MUST use this directory as the base path. Do NOT save any research artifact to `/mnt/agents/output/` directly — always use the `/mnt/agents/output/research/` subdirectory.

Before writing any file, ensure the directory exists (create it if not).

## Workflow Overview

```
User Query
  │
  ├─ Broad / Wide topic (no angle specified)
  │   → Phase 1 (Landscape) → Phase 2 (Decompose)
  │     → Phase 3 (Parallel Deep Dive) → Phase 4 (Cross-Verify)
  │       → Phase 5 (Targeted Validation) → Phase 6 (Insight Extraction) → Phase 7 (Report via report-writing)
  │
  ├─ Specific question with clear dimensions
  │   → Phase 2 (Decompose)
  │     → Phase 3 (Parallel Deep Dive) → Phase 4 (Cross-Verify)
  │       → Phase 5 (if conflicts exist) → Phase 6 (Insight Extraction)→ Phase 7 (Report via report-writing)
  │
  └─ Follow-up on prior research (new angle or deeper dive)
      → Phase 2 (add dimensions) → Phase 3 → Phase 4  → Phase 6 (Insight Extraction)→ Phase 7 (Report via report-writing)
```

## Epistemic Reset Rule

Before any analysis or narrative generation, the system MUST:
- Assume internal knowledge may be outdated or incomplete. Always retrieve the current date and time using bash tool before any analysis or external search.
- Using bash to check the time now.
- Perform external wide search to establish the evidence landscape
- Avoid generating any factual claims before Phase 1 search outputs
- All outputs MUST use inline citations `[^number^]` referencing original sources.



## Phase 1: Landscape Scan (Orchestrator, Sequential)

**Goal**: Establish an evidence-grounded global narrative landscape through coarse-to-fine exploration before committing to dimension decomposition.

This phase operates under External-Evidence-First Mode.

No analytical narrative may be generated before search outputs are reviewed.

* Every key finding must include `[^number^]` citation inline.

**Process**:

1. Perform 5 broad exploratory searches by yourself. Search MUST follow a coarse-to-fine progression. Don't search details at beginning.
   * Level 1 – Macro Overview (Search 1-2): Broad overview queries, Industry reports, High-level statistics, Wikipedia-level but verified via authoritative sources, General summaries
   * Level 2 – Structural Mapping (Search 2-4): Market structure, Major actors, Regulatory bodies
   * Level 3 – Emerging Issues & Tensions (Search 5): Recent developments,  Conflicting narratives,  Trend signals
2. After EACH search, output:
   - Key findings (concise)
   - Dominant narratives identified
   - Controversies or conflicting claims detected
   - Key actors and authoritative sources discovered
   - Gaps requiring deeper investigation
3. Revise dimension decomposition if landscape reveals unexpected structure




## Phase 2: Dimension Decomposition

**Goal**: Finalize research dimensions and prepare sub-agent assignments.

**Rules**:
- **≥10 dimensions (mandatory minimum)**. More is better — 10–20 dimensions depending on topic complexity
- Each dimension approaches the topic from a **distinct angle or scenario**, ensuring the research covers the problem space from fundamentally different perspectives
- Dimensions may be organized by:
  - **Analytical angle** (technical, economic, regulatory, ethical, competitive, user-facing, supply-chain, etc.)
  - **Scenario** (optimistic, pessimistic, status quo, disruption, black swan, etc.)
  - **Stakeholder viewpoint** (consumer, enterprise, regulator, investor, competitor, workforce, etc.)
  - **Geography or market segment** (China, US, EU, emerging markets, etc.)
  - **Time horizon** (historical origins, current state, 1-year outlook, 5-year outlook, etc.)
  - Or any combination — the goal is maximum coverage with deliberate partial overlap
- ≥30% conceptual overlap between related dimensions — overlap creates cross-verification pressure
- Each dimension MUST cover:
  1. **Current state** — what is happening now from this angle, always with inline `[^number^]` citations
  2. **Key evidence** — data, sources, and concrete examples using `[^number^]`
  3. **Tensions and counter-arguments** — what opposing views exist from this angle, all claims referenced via `[^number^]`

Output: a numbered dimension list (≥10 items) with clear scope, assigned angle/scenario, and expected source types for each.

## Phase 3: Parallel Deep Dive (Sub-Agent Deployment)

**Goal**: Execute depth-first research across all dimensions in parallel. **≥10 sub-agents launched simultaneously**, one per dimension.

**Process**:

1. Create one sub-agent per dimension via `task` — **launch all sub-agents in parallel** (do not serialize)
2. Each sub-agent investigates from its assigned angle/scenario, producing findings that are distinct from but partially overlapping with other agents
3. Each sub-agent's `prompt` MUST include:
   - **(1) Mission**: the dimension's scope, four required angles (current state, history, stakeholders, counter-narrative), and depth expectations
   - **(2) Context**: key findings from Phase 1 landscape scan relevant to this dimension
   - **(3) Output format**: the evidence template below
   - **(4) Output file path**: the sub-agent MUST save to `/mnt/agents/output/research/{topic}_dim{NN}.md` — include this exact path in the prompt

**Sub-Agent Requirements** — each sub-agent MUST:
- Perform **≥20 independent searches** (no repeated keyword cycles)
- Investigate primary sources where possible (government sites, academic journals, official filings, major media)
- Trace claims back to original publication
- Identify and document counter-arguments
- Avoid content farms, anonymous blogs, SEO aggregators
- **Save output to `/mnt/agents/output/research/{topic}_dim{NN}.md`** — this path is mandatory

**Sub-Agent Output Format** — all citations use `[^number^]`

```
Claim: [identified claim with inline citation, e.g., "EV market grew 25% in 2025[^1^]"]
Source: [source name]
URL: [source URL]
Date: [publication date]
Excerpt: [verbatim raw excerpt — no paraphrasing]
Context: [surrounding context]
Confidence: [high / medium / low]
```

**Output**: Each sub-agent saves its output to **`/mnt/agents/output/research/{topic}_dim{NN}.md`**.

## Phase 4: Cross-Verification Engine (Orchestrator)

**Goal**: Compare all dimension outputs, classify confidence, surface contradictions, and **save the verification results to a file** for downstream use by report-writing.

**Process**:
1. Read all `/mnt/agents/output/research/{topic}_dim{NN}.md` files
2. Categorize every finding into one of four tiers:

| Tier | Criteria |
|------|----------|
| **High Confidence** | Confirmed by ≥2 agents from independent sources with consistent evidence |
| **Medium Confidence** | Confirmed by 1 agent from an authoritative source |
| **Low Confidence** | Weak sourcing, blog-level evidence, or single unverified claim |
| **Conflict Zone** | Statistical disagreement, interpretive divergence, or temporal inconsistency between agents |

3. List all Conflict Zone items explicitly — contradictions are highlighted and analyzed, never suppressed
4. Determine if Phase 5 is needed (any Conflict Zone or critical Low Confidence items)
5. Inline citations `[^number^]` must be preserved
6. Conflict Zone analysis must include `[^number^]` references to all sources involved

**Output**: Save the complete cross-verification results (all tiers + conflict zone analysis) to **`/mnt/agents/output/research/{topic}_cross_verification.md`**. This file is critical — it carries confidence classifications that guide report-writing.

## Phase 5: Targeted Validation (Conditional)

**Goal**: Resolve conflicts and strengthen weak findings.

**Trigger**: Execute only if Phase 4 identified Conflict Zone or critical Low Confidence items.

All validation outputs must preserve inline `[^number^]` citations

**Process**:
1. For each unresolved item, deploy a focused sub-agent with:
   - The specific conflicting claims and their sources
   - Instructions to find independent evidence that resolves the disagreement
   - Minimum 3 additional searches per conflict

2. Repeat until each item is either:
   - **Resolved** — reclassified to High/Medium Confidence with new evidence
   - **Explicitly marked unresolved** — documented as a genuine disagreement in the field

3. **Update** `/mnt/agents/output/research/{topic}_cross_verification.md` with the resolution results.

## Phase 6: Insight Extraction

**Goal**: Identify non-obvious insights that do not explicitly appear in previous findings, but emerge from cross-dimension analysis.

**Definition of Insight**:
An insight is a higher-level inference derived from multiple validated findings.  It must not repeat previously stated claims or evidence.

**Process**:

1. Review all validated findings from Phase 3–5.
2. Identify patterns that only become visible when comparing multiple dimensions.
3. Extract insights that reveal: structural relationships, hidden tensions, emerging trends, systemic risks, strategic opportunities
4. Ensure each insight is supported indirectly by evidence from at least two dimensions.

**Genre-aware insight extraction**: Adjust emphasis based on the intended downstream writing format:
- **Report** (industry report, market analysis, consulting deliverable): prioritize actionable strategic insights, market opportunities, competitive dynamics, and forward-looking implications
- **Academic paper** (survey, empirical study, literature review): prioritize research gaps, methodological contradictions, theoretical tensions, and novel contribution angles that position against prior work
- When the target genre is unclear, produce insights in a neutral format covering both strategic and academic angles — the writing skill will adapt

**Output Requirements**:

For each insight, record:

- Insight: concise statement of the inferred pattern
- Derived From:
  - Dimension references (e.g., Dim 02, Dim 07)
  - Supporting evidence clusters
- Rationale: explanation of how the insight emerges from the evidence
- Implications: potential impact or significance
- Confidence: high / medium / exploratory

**Output**: Save all insights to **`/mnt/agents/output/research/{topic}_insight.md`**. This file is the core synthesis of the entire deep research process and will be the primary input for the downstream writing skill.

**Rules**:

- Insights must not duplicate existing findings.
- Insights must be derived from cross-dimension comparison.
- Avoid speculative claims unsupported by evidence.
- Minimum output: 5 insights.
- Insights must include references to supporting evidence using inline citations `[^number^]`



## Phase 7: Handoff to Writing Skill

**Goal**: Hand off all research artifacts to the appropriate writing skill for final document generation.

After cross-verification (and optional targeted validation) and insight extraction are complete:

1. Verify all required files exist under `/mnt/agents/output/research/`:
   - `{topic}_dim{NN}.md` — all dimension files (≥10)
   - `{topic}_cross_verification.md` — confidence tiers and conflict analysis
   - `{topic}_insight.md` — cross-dimension insights
2. Determine the target writing skill based on user intent:
   - **`report-writing`** — industry reports, market analysis, consulting deliverables, policy briefs
   - **`paper-writing`** — academic papers, survey papers, literature reviews, conference submissions
3. Invoke the selected writing skill, providing **explicit file paths** in the handoff:
   - **Insight file**: `/mnt/agents/output/research/{topic}_insight.md`
   - **Cross-verification file**: `/mnt/agents/output/research/{topic}_cross_verification.md`
   - **Dimension files**: `/mnt/agents/output/research/{topic}_dim01.md` through `{topic}_dim{NN}.md`
   - **Research directory**: `/mnt/agents/output/research/`
4. The orchestrator MUST explicitly tell the writing skill that deep research is complete and no additional research sub-agents are needed.
5. The final document MUST incorporate insights from Phase 6.



## Output Rules

- Insights from Phase 6 must be incorporated into the final document — as a dedicated Insights section (for reports) or woven into Discussion/Contribution sections (for papers).
- Insights must not be omitted even if the user requested a shorter output format.
- All outputs must include `[^number^]` style citations.
- The final document must clearly distinguish verified findings, conflict zones, and derived insights.
- If the user doesn't specify file type, default to Word format.



## Core Principles

1. **Depth over breadth.** Shallow aggregation is forbidden. Each dimension must be investigated thoroughly before moving on.
2. **Raw evidence required.** Sub-agents must return verbatim excerpts with source URLs and dates. No paraphrased-only outputs.
3. **Contradictions are signal.** Conflicts are highlighted and analyzed, never suppressed or averaged away.
4. **Everything is a file.** Never output long-form research content in chat. Chat is for status updates only.
5. **Source quality matters.** Prioritize: government sites, academic journals, official filings, major media. Avoid: content farms, anonymous blogs, SEO aggregators.
6. **≥10 sub-agents, ≥200 total searches** across the entire research system. No repeated keyword cycles across agents.
7. **All outputs must include `[^number^]` style citations**
8. **All files under `/mnt/agents/output/research/`.** No exceptions. Every dim file, cross-verification file, and insight file MUST be saved to this directory.

## File Naming

All files are saved under `/mnt/agents/output/research/`.

| File | Phase | Content |
|------|-------|---------|
| `{topic}_dim{NN}.md` | Phase 3 | Per-dimension sub-agent research output |
| `{topic}_cross_verification.md` | Phase 4-5 | Confidence tier classification + conflict zone analysis |
| `{topic}_insight.md` | Phase 6 | Cross-dimension insights (core synthesis for downstream writing skill) |
