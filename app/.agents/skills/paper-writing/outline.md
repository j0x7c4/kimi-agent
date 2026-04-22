# Outline Design Reference (Academic Papers)

## Sub-agent Strategy

| Agent | Mission | Output |
|-------|---------|--------|
| requirement_analyst | Extract research questions, scope, constraints, target venue from user query + files | Requirements doc |
| artifact_analyst | Synthesize research artifacts from `/mnt/agents/output/research/` to identify prior work, research gaps, and positioning opportunities | Literature landscape map with citations |
| structure_designer | Design section hierarchy, allocate word budgets per section | Skeleton with numbering |
| methodology_planner | Outline the research approach, data sources, analytical framework, evaluation criteria | Methodology spec |

Run requirement_analyst and artifact_analyst in parallel first. Feed their outputs to structure_designer and methodology_planner. Orchestrator synthesizes.

**Uploaded files**: Check `/mnt/agents/upload/` for user materials (data, prior drafts, reference papers). If present, include a file_analyst agent. If empty, skip.

## Standard Academic Structure

Most papers follow a canonical structure. The outline should map to this unless the user or target venue requires otherwise:

```
# Paper Title

## Abstract
### Research Summary
#### Background and motivation (1-2 sentences)
#### Research question / objective
#### Methodology overview
#### Key findings with quantitative highlights
#### Significance and implications

## 1. Introduction (~15-20% of total)
### 1.1 Background and Motivation
### 1.2 Research Gap and Problem Statement
### 1.3 Contribution Statement
### 1.4 Paper Organization

## 2. Related Work (~15-20% of total)
### 2.1 [Thematic Group A]
### 2.2 [Thematic Group B]
### 2.3 Positioning Against Prior Work

## 3. Methodology (~20-25% of total)
### 3.1 Problem Formulation
### 3.2 Proposed Approach / Framework
### 3.3 Implementation Details

## 4. Experiments / Results (~20-25% of total)
### 4.1 Experimental Setup
### 4.2 Results and Analysis
### 4.3 Ablation Studies / Sensitivity Analysis (if applicable)

## 5. Discussion (~10-15% of total)
### 5.1 Interpretation of Results
### 5.2 Limitations
### 5.3 Implications

## 6. Conclusion (~5% of total)
### 6.1 Summary of Contributions
### 6.2 Future Work

# References
```

**This is a template, not a mandate.** Survey papers replace Methodology/Results with thematic analysis sections. Case studies have different flows. Adapt to the actual research.

## Contribution Statement

Every paper outline MUST include a clear contribution statement in the Introduction section (typically at H4 level under "1.3 Contribution Statement"). This answers three questions:
1. **What is new?** — the specific novel element (method, finding, framework, dataset)
2. **How does it differ from prior work?** — explicit contrast with closest existing work
3. **Why does it matter?** — the practical or theoretical significance

Weak: "This paper makes several contributions to the field."
Strong: "We propose X, which differs from Y[^1^] by addressing Z, achieving N% improvement on benchmark B."

## 4-Level Heading Format

Same rules as report-writing — non-negotiable:

- **H1**: paper title + "References" section. No numbering
- **H2**: major sections. Numbered: `## 1. Title`
- **H3**: subsections. Numbered: `### 1.1 Title`
- **H4**: content points. Numbered: `#### 1.1.1 Title` — specific, executable
- **H5 forbidden.** Flatten if logic needs more depth
- **Abstract**: before `## 1.`, no numbering
- All H2/H3/H4 sequentially numbered

### Quantification

Each H2 section should specify:
- Target word count (with percentage of total)
- Required elements (tables, figures, equations, algorithms)
- Key references to incorporate

## Citations in Outlines

- Inline superscript: `[^1^]`, `[^2^]` for specific claims
- Sub-agents append to `/mnt/agents/output/{filename}_outline_references_raw.md`
- Outline file contains only `[^N^]` markers — no reference list
- **Academic citation density is high**: artifact analyst should extract 20+ relevant works from research artifacts at the outline stage

**Source priority**: T1 (peer-reviewed journals, top conferences, official datasets) > T2 (preprints with significant citations, established technical blogs, reputable surveys) > Reject (unreviewed preprints with no citations, content farms, anonymous sources)

## Validation Checklist

- [ ] Contribution statement is explicit and specific
- [ ] All canonical sections present (or justified if omitted)
- [ ] Related Work covers the major relevant research threads
- [ ] Methodology section has enough detail to be executable
- [ ] 4-level hierarchy only — no H5
- [ ] Word budgets specified per section
- [ ] Required figures, tables, equations noted per section
- [ ] "References" section lists all intermediate files
- [ ] Literature scanner identified sufficient prior work for positioning

## Format Example

```markdown
# Efficient Multi-Agent Orchestration for Complex Document Generation

## Abstract
### Research Summary
#### LLM-based document generation faces quality degradation in long-form outputs[^1^]
#### Propose a skill-based orchestration framework decomposing tasks into Capability × Artifact
#### Evaluate on 50 report-generation tasks across 4 domains
#### Achieves 34% improvement in coherence score and 2.1x throughput vs single-agent baseline

## 1. Introduction (~2000 words)
### 1.1 Background and Motivation
#### 1.1.1 Growing demand for automated long-form content generation[^2^]
#### 1.1.2 Single-agent approaches degrade beyond 5000 tokens[^3^]
### 1.2 Research Gap
#### 1.2.1 Existing multi-agent frameworks lack domain-specific quality control
#### 1.2.2 No principled method for task decomposition in document generation
### 1.3 Contributions
#### 1.3.1 A Capability × Artifact taxonomy for document generation task decomposition
#### 1.3.2 Progressive skill loading mechanism reducing context pollution by 60%
#### 1.3.3 Quality-gated review pipeline with specialized editor agents
### 1.4 Paper Organization
#### 1.4.1 Section structure overview

## 2. Related Work (~2500 words, 1 comparison table)
### 2.1 LLM-based Document Generation
#### 2.1.1 Single-agent approaches: GPT-4 long-form, Claude artifacts[^4^]
#### 2.1.2 Template-driven generation: limitations in flexibility
### 2.2 Multi-Agent LLM Systems
#### 2.2.1 AutoGen, CrewAI, MetaGPT — general frameworks[^5^][^6^]
#### 2.2.2 Specialized vs. general agent design trade-offs
### 2.3 Positioning
#### 2.3.1 Comparison table: our approach vs 5 existing systems on 6 dimensions

## 3. Methodology (~3000 words, 2 figures, 3 algorithms)
### 3.1 Problem Formulation
#### 3.1.1 Formal definition of document generation as Capability × Artifact composition
### 3.2 Skill-Based Orchestration Framework
#### 3.2.1 Skill taxonomy design and progressive loading mechanism
#### 3.2.2 Dynamic workflow composition algorithm
### 3.3 Quality-Gated Review Pipeline
#### 3.3.1 Editor agent specialization and gate criteria

# References
## efficient_multiagent_outline_references_raw.md
- **Type**: Citation collection
- **Description**: All sources from outline-stage literature scanning
- **Path**: /mnt/agents/output/efficient_multiagent_outline_references_raw.md
```

## Output

Save to: `/mnt/agents/output/{filename}.agent.outline.md`

After saving, provide download link. If full paper intended, one-sentence prompt to proceed.
