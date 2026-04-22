# Citation Management Reference (Academic Papers)

## Citation Format

### In-Text (during writing)

All sections use superscript format during writing: `[^1^]`, `[^2^]`

This is a universal intermediate format. The citation_manager converts to the target style in the final `_ref.md`.

### Reference List (final output)

The target citation style depends on the venue. The Orchestrator determines this from the user's query (e.g., "IEEE format," "APA style," "NeurIPS submission") and passes it to the citation_manager.

| Style | Typical Venues | In-Text Convention | Reference Format |
|-------|---------------|-------------------|-----------------|
| IEEE | IEEE transactions, most CS conferences | `[1]`, `[2]` numbered | `[1] A. Author, "Title," *Journal*, vol. X, pp. Y-Z, Year.` |
| APA 7th | Psychology, social sciences, some interdisciplinary | `(Author, Year)` | `Author, A. B. (Year). Title. *Journal*, *volume*(issue), pages. DOI` |
| ACM | ACM conferences and journals | `[Author Year]` or numbered | ACM Reference Format |
| Chicago Author-Date | Humanities, some social sciences | `(Author Year)` | Author. Year. "Title." *Journal* Volume(Issue): Pages. |
| GB/T 7714-2015 | Chinese academic journals | `[1]`, `[2]` numbered | `[1] Author. Title[J]. Journal, Year, Vol(Issue): Pages.` |
| Vancouver | Medical and biomedical journals | `(1)`, `(2)` numbered | `1. Author. Title. Journal. Year;Vol(Issue):Pages.` |

**Default**: If the user doesn't specify a venue or style, use IEEE numbered format. Chinese-language papers default to GB/T 7714-2015.

## Source Tier System

### T1 — Preferred
Peer-reviewed journals (Nature, Science, IEEE Transactions, ACL Anthology, etc.), top-tier conference proceedings (NeurIPS, ICML, CVPR, ACL, AAAI, etc.), official datasets with published papers, textbooks from established publishers

### T2 — Acceptable
Preprints with significant citations (arXiv papers with 50+ citations), established technical blogs from research labs (Google AI Blog, Meta AI), well-cited survey papers, official documentation for tools and frameworks

### Rejected — Never cite
Unreviewed preprints with zero citations (unless the user's own work), content farms, anonymous forums, unverified social media, vendor marketing materials

**Academic-specific notes**:
- Prefer the published version over the preprint when available
- For concurrent/recent work, citing preprints is acceptable with a note
- Self-citation: acceptable when genuinely relevant, but flag if >20% of references are self-citations

## Automatic Citation Recording

MCP tools auto-record to `/mnt/agents/.store/citation.jsonl`. Hard rule: no sub-agent touches this file.

Outline-stage sub-agents append to `{filename}_outline_references_raw.md`.

## Citation Manager

Created after all sections finalized, before assembly.

### Input
- `/mnt/agents/.store/citation.jsonl` (read-only)
- `/mnt/agents/output/{filename}_outline_references_raw.md` (if exists, read-only)
- **Target citation style** (from Orchestrator)

### Process
1. Read both sources
2. Deduplicate: same DOI, same URL, or same author+title+year = same reference
3. Assign sequential numbering per target style convention
4. Format each entry following the target style:
   - Include DOI for journal papers when available
   - Include URL for web resources, technical reports, datasets
   - Conference papers: include proceedings name, pages, year
5. Output to `/mnt/agents/output/{filename}_ref.md`

### Output Format

`_ref.md` contains ONLY the formatted reference list. Example (IEEE style):

```
[1] A. Vaswani et al., "Attention is all you need," in Proc. NeurIPS, 2017, pp. 5998-6008.
[2] J. Devlin, M. Chang, K. Lee, and K. Toutanova, "BERT: Pre-training of deep bidirectional transformers for language understanding," in Proc. NAACL-HLT, 2019, pp. 4171-4186.
[3] T. Brown et al., "Language models are few-shot learners," in Proc. NeurIPS, 2020, pp. 1877-1901.
```

### Constraints
- Read-only: never modifies section files or `.citation.jsonl`
- Numbering mismatch between sections and `_ref.md` is expected in markdown drafts
- `_ref.md` is the single source of truth
