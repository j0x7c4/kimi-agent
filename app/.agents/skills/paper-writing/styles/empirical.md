# Empirical Research Paper Style

## Voice and Tone
- Rigorous and evidence-driven. Every claim backed by experimental evidence
- Methodologically transparent: decisions are justified, not asserted
- Precise: exact numbers, confidence intervals, reproducible specifications
- Modest: claim only what the evidence supports, hedge appropriately

## Structure Conventions
- Standard flow: Introduction → Related Work → Method → Experiments → Discussion → Conclusion
- Methodology section must be self-contained for reproduction
- Results: tables with baselines, bold best results, include ± std dev
- Ablation study for multi-component methods is expected, not optional
- Error analysis / failure cases section strongly encouraged

## Language Patterns
- Prefer: "Our method achieves 92.3% ± 0.4 F1 (p < 0.01 vs. baseline)" over "Our method significantly outperforms baselines"
- Prefer: "We chose architecture X over Y because of property Z[^1^]" over "We used architecture X"
- Report negative results honestly: "While effective on dataset A, performance degrades on B due to..."

## Prohibited Patterns
- Unreproducible claims: results without full experimental specification
- Cherry-picked comparisons: omitting strong baselines or favorable-only datasets
- Overclaiming: "state-of-the-art" without comprehensive comparison against current leaders
- Missing variance: single-run results for stochastic methods without justification
