# Outline Design Reference

## Sub-agent Strategy

Decompose outline design into parallel specialist tasks, then synthesize:

| Agent | Mission | Output |
|-------|---------|--------|
| requirement_analyst | Extract all explicit and implicit requirements from user query + uploaded files | Structured requirements doc |
| structure_designer | Design chapter hierarchy, weight distribution, word count allocation | Skeleton with numbering and word targets |
| artifact_analyst | Read and synthesize research artifacts from `/mnt/agents/output/research/` (`{topic}_insight.md`, `{topic}_cross_verification.md`, key `{topic}_dim{NN}.md` files) to identify themes, data points, and source structure | Research synthesis with citations |
| content_planner | For each chapter, define specific content points, required elements (tables, cases), and presentation approach | Detailed chapter specs |

Run requirement_analyst and artifact_analyst in parallel first. Feed their outputs to structure_designer and content_planner. Finally, the Orchestrator synthesizes all outputs into the unified outline.

**Uploaded files**: Check `/mnt/agents/upload/` for user-provided materials. If present, include a file_analyst agent to extract useful information. If the path doesn't exist or is empty, skip.

## Sub-agent Output Rules

Sub-agents output only their analysis content. They must NOT include:
- Summary tables, overview charts, or "chapter structure recap"
- Logic relationship diagrams or ASCII art
- Team assignment suggestions or division of labor
- Emoji, decorative separators, or "design highlights"

The Orchestrator filters these out during synthesis even if they leak through.

## 4-Level Heading Format

This is non-negotiable. The outline is the contract that writers execute against.

```
# Title (H1, no number — only for main title and "References" section)

## 1. Chapter Title (H2 — numbered, maps to a chapter file)
### 1.1 Section Title (H3 — numbered subsection)
#### 1.1.1 Point Summary (H4 — the atomic content unit, a concise actionable statement)

## 2. Another Chapter
### 2.1 Section
#### 2.1.1 Point
#### 2.1.2 Point

# References
## File Name
- **Type**: file type
- **Description**: purpose
- **Path**: /mnt/agents/output/...
```

**Why this structure matters**: Writers receive their chapter's outline excerpt and execute it literally. H4 headings are their task list — each one becomes a paragraph or content block. If H4s are vague ("discuss trends"), writers produce vague content. If H4s are specific ("Global EV battery costs dropped 14% YoY in 2024, driven by LFP adoption in China"), writers produce substantive content.

### Rules

- **H5 is forbidden.** Never use `#####` or 4-digit numbering (1.1.1.1). If logic needs more depth, flatten: promote sub-points to siblings (1.1.2, 1.1.3) or merge into the parent H4's description
- **H1**: main title + "References" section only. No numbering
- **H2**: chapters. Numbered: `## 1. Title`
- **H3**: sections within chapters. Numbered: `### 1.1 Title`
- **H4**: content points. Numbered: `#### 1.1.1 Title`. Concise but specific enough to be executable
- **Abstracts/Executive Summaries**: only for formal research reports. Placed before `## 1.` with no numbering. Most reports don't need them
- All H2/H3/H4 must have sequential numbering. H1 never has numbering

### Quantification

Every chapter-level (H2) entry should specify:
- Target word count
- Required elements (number of tables, case studies, data points)
- Key sources or data to incorporate

This turns the outline from a "table of contents" into an "execution spec."

## Citations in Outlines

Even at the outline stage, specific facts and data points need citations:

- Use inline superscript: `[^1^]`, `[^2^]` in the outline text
- All sub-agents append references to `/mnt/agents/output/{filename}_outline_references_raw.md` (append-only, no dedup required, disorder is expected)
- The outline file itself contains only `[^N^]` markers — no reference list at the bottom
- Citation numbering may be inconsistent across sub-agents; the citation_manager resolves this later

**Source priority**: T1 (government, international orgs, top journals, official filings) > T2 (Reuters, Bloomberg, major think tanks) > Reject (content farms, anonymous forums, unverified social media)

## Validation Checklist

Before saving the outline, verify:

- [ ] Every user requirement has a corresponding section
- [ ] 4-level hierarchy only — no H5, no 4-digit numbering
- [ ] All H2/H3/H4 are numbered; H1 is not
- [ ] H4 titles are specific and executable, not vague
- [ ] Word counts and required elements specified per chapter
- [ ] "References" section lists all intermediate files (outline, references_raw, uploaded files)
- [ ] No extraneous content: no summary tables, no structure overviews, no emoji
- [ ] Citations use `[^N^]` format where specific data appears

## Format Example

```markdown
# 2025 Global AI Chip Market Analysis

## Executive Summary
### Key Findings
#### Market projected to reach $XX billion by 2028[^1^], driven by data center demand
#### NVIDIA maintains 70%+ market share[^2^] but faces rising competition from custom silicon

## 1. Market Overview (~3000 words, 2 tables)
### 1.1 Market Size and Growth
#### 1.1.1 Global market valued at $XX billion in 2024, XX% CAGR since 2020[^3^]
#### 1.1.2 Segmentation by application: data center (60%), edge (25%), automotive (15%)[^4^]
### 1.2 Demand Drivers
#### 1.2.1 LLM training compute requirements doubling every 6 months
#### 1.2.2 Sovereign AI initiatives creating new demand pools (table: top 10 national programs)

## 2. Competitive Landscape (~4000 words, 3 tables, 2 case studies)
### 2.1 Major Players
#### 2.1.1 NVIDIA: product roadmap from H100 to B200, pricing power analysis
#### 2.1.2 AMD: MI300X positioning and hyperscaler adoption status
### 2.2 Emerging Challengers
#### 2.2.1 Custom silicon: Google TPU, Amazon Trainium, Microsoft Maia
#### 2.2.2 Chinese ecosystem: Huawei Ascend, Cambricon — impact of export controls

# References
## ai_chip_outline_references_raw.md
- **Type**: Citation collection
- **Description**: All T1/T2 sources gathered by sub-agents during outline design
- **Path**: /mnt/agents/output/ai_chip_outline_references_raw.md

## ai_chip.agent.outline.md
- **Type**: Report outline
- **Description**: This outline file
- **Path**: /mnt/agents/output/ai_chip.agent.outline.md
```

This example demonstrates format only. Do not copy its structure — every report's chapter design should emerge from the specific topic and user requirements.

## Output

Save outline to: `/mnt/agents/output/{filename}.agent.outline.md`

After saving, do NOT call any more tools. Provide download link and (if full report is intended) a one-sentence prompt asking whether to proceed to writing.
