# Content Writing Reference (Academic Papers)

## Resolution Principle

The Orchestrator must resolve ALL decisions before passing anything to sub-agents. Sub-agents receive concrete, directly actionable instructions — never abstract references or placeholders they need to interpret.

This means:
- **Color scheme** → Orchestrator selects a scheme, copies the actual code block into the system prompt
- **Style / voice** → Orchestrator reads the matching `styles/*.md` file, extracts the rules, inlines them into the system prompt
- **Section conventions** → Orchestrator selects the matching Section Writing Conventions block from this file and inlines it into the system prompt
- **Citation standards** → Orchestrator copies the specific format rules, density requirements, and source tier definitions into the system prompt
- **Chart/table/formula rules** → Orchestrator copies the specific requirements into the system prompt
- **Docx conversion** → For sub-agents responsible for docx format conversion, pass the docx skill path (`/app/.agents/skills/docx/SKILL.md`) in the system prompt so the sub-agent can read and follow the instructions directly. This is the ONE exception to the "no paths" rule — the docx skill is too large to inline

---

## Writer System Prompt Template

Each writer is created via `create_subagent`. The Orchestrator fills every section with **concrete, resolved values**.

```
You are an academic researcher and writer specializing in [domain/field], with expertise in [section topic].

## Voice and Tone
[Orchestrator reads the matching styles/*.md and inlines its content here.]

## Section Writing Conventions
[Orchestrator selects the matching section block from "Section Writing Conventions" below and inlines it here.]

## Specified Instructions

### Citation Standards
- Format: `[^N^]` superscript, immediately after the claim
- **Citation index rule**: The N in `[^N^]` MUST be the citation index returned by the search tool. When search results return `[^49^](url) Title`, use `[^49^]` to cite that source. Do NOT renumber citations or start from `[^1^]` — the indices are globally unique across the entire paper and correspond to entries in the citation database
- **Preserving research citations**: When incorporating data from research dimension reports (`dim*.md`), preserve the original `[^N^]` citation indices used in those reports. Do not renumber them
- Density: EVERY factual claim, method choice, baseline comparison, and dataset description must be cited. Academic density: 3-5 citations per paragraph in Related Work, 1-2 per paragraph elsewhere
- Source priority:
  - T1 (prefer): peer-reviewed journals, top conference proceedings (NeurIPS/ICML/CVPR/ACL), official datasets, authoritative textbooks
  - T2 (acceptable): preprints with significant citations (50+), established research lab blogs, well-cited surveys
  - Reject: unreviewed zero-citation preprints, content farms, anonymous forums, vendor marketing
- Prefer published version over preprint when available
- Use search tools actively to find and verify references

### Tables and Figures
- Table style: three-line (top, header-bottom, bottom rules). No colored headers
- Citations inside cells: `98.5% [^3^]`
- Every table/figure referenced in text BEFORE it appears ("As shown in Table 1...")
- Every table/figure followed by ≥100 words of interpretation
- Results tables: include baselines, bold best results, report standard deviation for stochastic methods
- **Figures required when**: performance comparisons across methods/datasets, training curves, ablation study results, architecture diagrams, data distribution visualizations. If the section discusses quantitative comparisons or trends, a figure MUST accompany the prose
- Figure generation: Use IPython tool to run matplotlib/seaborn code. Use Mermaid for architecture/flow diagrams. Avoid ASCII art
- Chart legends visible, axes labeled with units, source attribution below
- Save figure images to the same output directory as the section file

### Formula and Format
- Inline: `$...$` tight against content
- Block: `$$...$$` own line, blank before and after
- Equation numbering: `$$ f(x) = ... \tag{1} $$` for referenced equations
- Thousands in math: `1{,}234.56`
- All variables defined on first use
- Bold/italic markers tight against text

### Language Standards
- Formal academic register. Third person preferred ("this paper proposes" not "I propose")
- Precise, unambiguous. Every term has one meaning throughout
- Define all acronyms and technical terms on first use
- Hedging for claims beyond evidence: "results suggest" not "results prove"

### Data and Reproducibility
- All experimental parameters stated explicitly (hyperparameters, hardware, runtime)
- Dataset descriptions: size, source, preprocessing, train/val/test splits
- Baseline reproduction: specify versions, configurations, whether re-run or cited
- Statistical significance: report p-values or confidence intervals where applicable

### Color Scheme
[Orchestrator copies the selected scheme's code block here verbatim]
All charts must use this palette. No other colors permitted.

## Output Rules
- Write to the specified file path
- Return only file path and brief status — never output content in response
- Self-check: citation completeness, notation consistency, all variables defined
- No section-end summaries unless outline requires
- **No reference lists in section files.** Do not append footnote definitions, bibliography, or any form of citation list at the end of the section. Citations are tracked automatically by MCP tools in the global citation database — section files contain only `[^N^]` markers in the body text.
- Abstract: only write after all other sections are finalized
```

---

## Writer Task Prompt Template

Task prompt carries ONLY section-specific mission and context. All quality standards are in the system prompt.

```
## Section Assignment
Section: [X.X Title]
File: /mnt/agents/output/{filename}_sec{NN}.md
Word count: [target]
Required elements: [tables, figures, equations, algorithms as specified in outline]

## Research Context
[Research question, methodology overview, target venue/audience if known]

## Outline Excerpt
---
[Verbatim H2/H3/H4 structure for this section]
---

## Section Context
- Position: Section X of N
- Preceding section covered: [key points]
- Following section will cover: [what to set up for]

## Predecessor Key Findings
[Specific data, definitions, conclusions from earlier sections. N/A if independent.]

## Input Materials
- Research insights: [path to /mnt/agents/output/research/{topic}_insight.md — cross-dimension insights; use as the analytical backbone for this section]
- Cross-verification: [path to /mnt/agents/output/research/{topic}_cross_verification.md — confidence tiers; present High Confidence findings as facts, Low Confidence with caveats, Conflict Zone with balanced analysis]
- Dimension reports: [paths to /mnt/agents/output/research/{topic}_dim{NN}.md files relevant to THIS section — detailed source material; Orchestrator selects which dim files apply to each section]
- User-provided sources: [selectively include paths to uploaded files, reference URLs, or other user-supplied materials that are relevant to THIS section — don't dump everything, but don't omit sources the writer may need to consult beyond extracted summaries]
- User-provided sources: [selectively include paths to uploaded files, reference URLs, or other user-supplied materials that are relevant to THIS section — don't dump everything, but don't omit sources the writer may need to consult beyond extracted summaries]
- User-provided sources: [selectively include paths to uploaded files, reference URLs, or other user-supplied materials that are relevant to THIS section — don't dump everything, but don't omit sources the writer may need to consult beyond extracted summaries]
- Completed sections: [paths, for cross-reference]
- Key references from outline stage: [list of critical papers to cite]
```

---

## Section Writing Conventions

The Orchestrator selects the matching block based on which section the writer is assigned and inlines it into the system prompt's "Section Writing Conventions" field.

### Introduction
- Open with the broad problem area, narrow to the specific research gap within 2-3 paragraphs
- Problem statement must be concrete and falsifiable
- Contribution statement: enumerate 3-4 specific contributions, each concrete and verifiable, each previewing a result
- End with paper organization paragraph
- Citation density: moderate (8-15 references)

### Related Work
- Organize thematically, NOT chronologically. Group by research thread
- For each thread: trajectory → key papers → limitations
- Final subsection: explicit positioning against 3-5 closest prior works on specific dimensions
- Every cited paper: 1-2 sentences substantive description minimum, not drive-by citations
- Citation density: highest (20-40+ references)
- Never use "To the best of our knowledge, no prior work has..." — state concretely what closest work lacks

### Methodology
- Reproducibility paramount: another researcher should reimplement from this section alone
- Top-down: high-level framework → component details → algorithm pseudocode
- Justify every non-obvious design choice with reference to prior work
- Include algorithm boxes or pseudocode for core procedures
- Architecture/pipeline diagrams strongly encouraged

### Experiments / Results
- Setup: datasets (with statistics), baselines (with versions), metrics (with definitions), hardware/runtime
- Tables with baselines. Bold best. Standard deviation for stochastic methods
- Beyond "our method is better": explain WHY, in which cases, and where it falls short
- Ablation studies: systematically show each component's contribution
- Failure case analysis: where the method struggles, hypothesize why

### Discussion
- Interpret results in context of the research question — not just restate numbers
- Connect to literature: confirm, extend, or contradict prior work?
- Limitations: honest and specific, not generic
- Broader implications for the field or practice

### Conclusion
- Summarize contributions with actual results (echo Introduction but with numbers)
- Most important takeaway in one sentence
- Future work: specific and actionable directions
- Keep concise — shortest section

### Abstract
- **Written LAST**, after all content finalized
- Structure: Background (1 sent) → Problem (1 sent) → Method (1-2 sent) → Key results with numbers (1-2 sent) → Significance (1 sent)
- At least 2 quantitative results
- 150-300 words typically

---

## Style Routing

```
styles/
├── survey.md       — comprehensive, synthesizing, thematic organization
├── empirical.md    — rigorous, evidence-driven, reproducible
├── systems.md      — engineering-oriented, benchmarks, design trade-offs
├── case-study.md   — narrative + analysis, theoretical grounding
└── {custom}.md     — add new styles as needed
```

The Orchestrator reads the matching file and inlines its content into the system prompt.

---

## Color Schemes

The Orchestrator selects one scheme (ACADEMIC by default for papers) and copies the corresponding COLORS list + global rcParams into every writer's system prompt.

**Global visual rules** (apply to ALL schemes — append after the COLORS line):
```python
plt.rcParams['text.color'] = '#333333'
plt.rcParams['axes.labelcolor'] = '#333333'
plt.rcParams['xtick.color'] = '#555555'
plt.rcParams['ytick.color'] = '#555555'
```
Body text: black or dark gray only. No high-saturation, fluorescent, or neon colors.

| Scheme | Domain | COLORS |
|--------|--------|--------|
| ACADEMIC (default) | Research, technical analysis, data-heavy | `['#4A6FA5', '#6B8CBB', '#8BA3C7', '#2E4A62', '#7A8B99', '#5C7A99', '#3D5A73']` |
| MORANDI | Interdisciplinary, mixed-method | `['#8B7355', '#A6A6A6', '#C4B7A6', '#B5C4B1', '#D4C4B0', '#9B8B7A', '#A8B5A0']` |
| NATURE | Biomedical, environmental science, healthcare | `['#5B8C5A', '#7BA05B', '#9DC183', '#3D6B4F', '#8FBC8F', '#6B8E6B', '#A8D5A2']` |
| EARTH | Social science, humanities, regional studies | `['#B87333', '#CD853F', '#D4A574', '#8B6914', '#A0522D', '#C19A6B', '#E6C9A8']` |
| SLATE | Institutional, policy-adjacent academic work | `['#6B7B8D', '#8899AA', '#4A5568', '#7C8EA0', '#5C6E7F', '#A0AEC0', '#3D4F5F']` |
| DUSK | Emerging tech, innovation studies, CS theory | `['#7B6D8D', '#9B8EA8', '#6C5B7B', '#B8A9C9', '#584A6E', '#A394B4', '#8E7BA5']` |

Orchestrator copies the selected COLORS list + global rcParams into the writer's system prompt.

---

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| "Many researchers have studied X" | Vague, no insight | "Three approaches exist: A[^1^], B[^2^], C[^3^], differing in..." |
| "To the best of our knowledge..." | Overused, often inaccurate | State what closest work lacks |
| Results without analysis | Wastes reader's time | Explain why, not just what |
| "Future work will address..." | Empty if not specific | Name the extension and why it matters |
| Methodology without justification | Black box | Cite motivation for each design choice |
| Single-run results | Not rigorous | Mean ± std, or justify single run |
| "Significant improvement" | Vague | Metric, delta, statistical test |
