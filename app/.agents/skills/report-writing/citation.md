# Citation Management Reference

## Citation Format

Two distinct formats for different contexts:

| Context | Format | Example |
|---------|--------|---------|
| In-text (outline and chapters) | Superscript with carets | `[^1^]`, `[^2^]` |
| Reference list (`_ref.md`) | Brackets, no carets | `[1]`, `[2]` |

**Placement rules**:
- Citation marker immediately follows the claim, no space: `market reached $50B[^3^]`
- In table cells: space before citation is acceptable for readability: `98.5% [^3^]`
- One citation can support multiple consecutive sentences from the same source, but each distinct data point should be individually cited

## Source Tier System

### T1 — Preferred
Government official sites, international organizations (UN, World Bank, IMF, WHO), top-tier peer-reviewed journals (Nature, Science, The Lancet, IEEE Transactions), official corporate filings (10-K, annual reports), authoritative technical documentation

### T2 — Acceptable
Major wire services (Reuters, Bloomberg, AP, AFP), newspapers of record (NYT, WSJ, FT), recognized think tanks and consulting firms (McKinsey Global Institute, Brookings, BCG), official company blogs and press releases

### Rejected — Never cite
Content farms, SEO aggregator sites, anonymous forum posts, unverified social media, self-published sources without peer review, vendor whitepapers with unsubstantiated product claims

**Conflict resolution**: Same fact, multiple sources → prefer T1. Multiple T1 → prefer most recent. T1 sources conflict → note the discrepancy in text.

## Automatic Citation Recording

MCP tools (WebSearch, Browser) automatically append citation records to `/mnt/agents/.store/citation.jsonl`. This is the primary citation database.

**Hard rule**: No sub-agent may directly read, write, or modify `.citation.jsonl`. Managed exclusively by MCP infrastructure.

Additionally, outline-stage sub-agents append references to `{filename}_outline_references_raw.md` as a supplementary source.

## Citation Manager

A specialized sub-agent created at the end of the review pipeline, after all chapters are finalized but before assembly.

### Input
- `/mnt/agents/.store/citation.jsonl` (read-only)
- `/mnt/agents/output/{filename}_outline_references_raw.md` (if exists, read-only)

### Process
1. Read both sources
2. Deduplicate: same URL or DOI = same reference
3. Assign sequential numbering: `[1]`, `[2]`, `[3]`...
4. Format following GB/T 7714-2015 (default) or user-specified style:
   - Journal articles: prefer DOI over URL
   - Web pages, databases, government reports: include URL
   - Books, theses: omit URL unless it's the only access path
5. Output to `/mnt/agents/output/{filename}_ref.md`

### Output Format

The `_ref.md` file contains ONLY the reference list — no headers, explanations, or metadata:

```
[1] OICA. World Motor Vehicle Production Statistics[DB/OL]. 2024. https://www.oica.net/production-statistics/
[2] Zhang, S., Li, W. Research on NEV Development[J]. Automotive Engineering, 2023, 45(3): 120-135.
[3] Ministry of Commerce. China Automotive Trade Quality Report[R/OL]. 2024. https://wms.mofcom.gov.cn/...
[4] Wang, J. Intelligent Manufacturing Technology[M]. Beijing: China Machine Press, 2022.
```

### Constraints
- Citation manager only reads — never modifies chapter files or `.citation.jsonl`
- If citation numbering in chapters doesn't perfectly match `_ref.md` ordering, this is expected and acceptable for markdown drafts
- The `_ref.md` file is the single source of truth for reference formatting
