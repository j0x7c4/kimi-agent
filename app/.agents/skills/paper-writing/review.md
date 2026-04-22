# Review Pipeline Reference (Academic Papers)

## Pipeline Architecture

Academic papers require an additional methodology review stage compared to reports. Sequential, each stage gates the next.

```
section_editor (per section, parallelizable)
  ↓ all sections pass
methodology_reviewer (rigor and reproducibility)
  ↓ pass
coherence_editor (cross-section consistency, argument thread)
  ↓ pass
abstract_reviewer (accuracy against finalized content)
  ↓ pass
citation_manager (reference consolidation — see citation.md)
```

## Section Editor

**Scope**: One section at a time. Parallelizable across sections.

**Task prompt must include**: file path, the outline section it was written against, and review criteria below.

**Review dimensions**:

1. **Completeness**: Every H4 point from outline covered? Word count met? Required elements (tables, figures, equations) present?

2. **Citation density**: Academic papers demand high citation density. Related Work: 3-5 citations per paragraph. Methodology: every method choice justified with reference. Results: all baselines cited. Flag any factual claim, comparison, or dataset mention without citation.

3. **Analytical depth**: Does the section explain "why" beyond stating results? Flag bare result reporting without interpretation.

4. **Academic register**: Formal, precise, third-person. Flag AI-isms, casual language, promotional adjectives, vague hedging ("some researchers").

5. **Notation consistency**: Variables, acronyms, and terminology consistent with definitions established in earlier sections.

6. **Table/figure compliance**: Three-line tables, inline citations, ≥100 words interpretation. All tables/figures referenced in text before appearing.

**Decision**: Pass → proceed. Fail → specific remediation brief → Writer rewrite in-place → re-review.

## Methodology Reviewer

**Scope**: Methodology and Experiments/Results sections together. Single agent reads both.

**This is the academic-specific addition.** Reports don't need this; papers do because reviewers at venues will scrutinize reproducibility and rigor.

**Review dimensions**:

1. **Reproducibility**: Could another researcher reimplement from the methodology section alone? Are all hyperparameters, configurations, data preprocessing steps stated? Flag any "we used standard settings" without specifying what those settings are.

2. **Experimental validity**: Are baselines appropriate and fairly compared? Same data splits, same evaluation metrics? Flag cherry-picked comparisons or missing obvious baselines.

3. **Statistical rigor**: Are results reported with variance (mean ± std)? For stochastic methods, are multiple runs reported? Are statistical significance tests used where appropriate? Flag single-run results without justification.

4. **Design justification**: Is every non-obvious design choice motivated? Why this loss function? Why this architecture? Why this dataset? Flag unjustified choices.

5. **Ablation completeness**: If the method has multiple components, are ablation studies present showing each component's contribution? Flag methods with 3+ components but no ablation.

6. **Limitation honesty**: Are failure cases and limitations discussed? Flag papers that claim universal superiority without acknowledging weaknesses.

**Decision**: Pass → proceed. Fail → remediation brief specifying which claims need evidence, which parameters are missing, which baselines to add → Writer rewrite → re-review.

## Coherence Editor

**Scope**: All sections read in sequence. Single agent.

**Must receive**: All section file paths in order, plus the outline.

**Review dimensions**:

1. **Argument thread**: Does Introduction's problem statement flow into Related Work's gap → Methodology's solution → Results' validation → Discussion's interpretation → Conclusion's summary? Flag breaks in this chain.

2. **Notation consistency**: Same symbol means the same thing throughout. $n$ in Methodology matches $n$ in Results. Flag redefined symbols.

3. **Cross-reference accuracy**: "As described in Section 3.2" — does Section 3.2 actually describe that? "Table 1 shows..." — is it actually Table 1? Flag mismatches.

4. **Claim consistency**: Introduction claims "34% improvement" — does Results section show exactly 34%? Flag any discrepancy between preview claims and actual results.

5. **Terminology stability**: Same concept, same word, throughout. Flag drift (e.g., "framework" in Section 1, "system" in Section 3, "pipeline" in Section 4 for the same thing).

6. **Redundancy**: Same explanation in multiple sections? Flag and recommend consolidation.

**Output**: Issue list with file/section locations, delegate targeted rewrites.

## Abstract Reviewer

**Scope**: Abstract section only. Runs AFTER coherence_editor because it must verify against finalized content.

**Why separate and last**: The abstract must accurately reflect what the paper actually contains, not what it planned to contain. Claims, numbers, and methodology descriptions must exactly match the body.

**Review criteria**:

1. **Factual accuracy**: Every number in the abstract appears in the Results section. Every method claim matches Methodology.

2. **Self-containment**: A reader should understand the contribution from the abstract alone. Does it cover background, problem, method, results, significance?

3. **Quantitative content**: At least 2 specific quantitative results present. Flag abstracts with only qualitative claims.

4. **Length compliance**: Typically 150-300 words. Flag if outside range (unless user specified venue requirements).

5. **No overclaiming**: Claims in abstract are supported by evidence in the paper. Flag superlatives or generalizations beyond what results show.

## Quality Gate Protocol

Binary pass/fail at each stage.

**On failure**:
1. Editor produces remediation brief: file, section, problem, fix
2. Orchestrator dispatches Writer to rewrite in-place
3. Same editor re-reviews affected sections
4. Maximum 2 rewrite cycles per section per stage
5. After 2 failures: flag and proceed with a note

**Context maintenance**: When coherence_editor identifies inconsistency between Section 2 and Section 4, the writer for Section 4 receives the relevant excerpt from Section 2 — not just "be consistent."
