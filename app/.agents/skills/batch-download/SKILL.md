---
name: batch-download
type: capability
description: >
  Multi-agent batch download and data collection orchestration. Use this skill whenever
  the task requires discovering, validating, and downloading multiple files or datasets
  from the web — batch report downloads, multi-source data collection, structured web
  scraping, file archival, or any task demanding parallel discovery and retrieval with
  verification. This skill enforces plan-first decomposition, parallel sub-agent delegation,
  evidence-based URL discovery, strict output validation, and structured result integration.
  Do NOT use for: single file download, simple API calls, tasks that don't involve
  web discovery or file retrieval.
---

# Batch Download

Orchestrate multi-agent batch discovery and retrieval: plan the task decomposition, delegate atomic subtasks to parallel sub-agents, gather and verify evidence, then integrate and validate all results into a structured deliverable. The Orchestrator coordinates — sub-agents execute.

## Workflow Decision Tree

Determine the entry point based on user input:

```
User Query
  │
  ├─ Type A — Targets unknown (must search first)
  │   → Phase 1 (Plan) → Phase 2 (Search & Discovery)
  │     → Phase 3 (Parallel Download) → Phase 4 (Integrate & Validate)
  │
  ├─ Type B — Targets already provided (URLs / file list given)
  │   → Phase 1 (Plan) → Phase 2 (URL Validation & Pattern Discovery)
  │     → Phase 3 (Parallel Download) → Phase 4 (Integrate & Validate)
  │
  └─ Hybrid — Some targets known, some must be discovered
      → Phase 1 (Plan) → Phase 2 (Partial Search + Validation)
        → Phase 3 (Parallel Download) → Phase 4 (Integrate & Validate)
```

All types follow the same 1→2→3→4 sequence. The difference is Phase 2's scope: Type A performs full search, Type B validates known URLs and discovers patterns, Hybrid does both.

## Phase 1: Task Decomposition (Orchestrator Only)

**Goal**: Break the user request into clear, atomic, verifiable subtasks before any execution.

**Process**:
1. Restate the user's request in operational terms
2. Identify the task type (Type A / Type B / Hybrid) based on whether target URLs are known
3. Decompose into atomic subtasks:
   - Each subtask has **one well-defined goal** (e.g., "download report for 2021 from URL X")
   - Each subtask is **independent** where possible (to enable parallelization)
   - Each subtask has **explicit success criteria** (file type, size, content validation)
4. For multi-dimensional requests (different years / regions / categories / file types / data sources), create **one subtask per dimension**
5. Plan search subtasks explicitly (if Type A or Hybrid):
   - Do NOT assign "all search" to a single agent when multiple independent searches are possible
   - **Parallelize partitionable search spaces**: by year, by site, by category, by alphabet range, by region — each partition gets its own search sub-agent
   - Plan **retry strategies**: if a search attempt fails, plan alternative queries, sites, or filters as new subtasks rather than giving up
6. If the search task is complex, split into multiple sequential stages (e.g., find index page → extract file links → validate → download)

No execution in this phase — planning only.

## Phase 2: Evidence Gathering & Pattern Discovery

**Goal**: Discover target URLs, validate them, and identify download patterns before batch execution. **All task types execute this phase** — the scope varies by type.

### Pattern Discovery (Critical)

Before delegating downloads, actively look for **URL patterns and structural regularities** in the download targets:
- **Numeric patterns**: URLs with incrementing page/year/ID numbers (e.g., `report_2020.pdf`, `report_2021.pdf`, ... or `page=1`, `page=2`, ...)
- **Directory patterns**: files organized in predictable folder structures (e.g., `/data/2023/Q1/`, `/data/2023/Q2/`)
- **Naming conventions**: consistent filename templates across a site (e.g., `{company}_annual_{year}.pdf`)
- **Pagination patterns**: API or page parameters that follow arithmetic sequences (e.g., `offset=0,10,20,...`)
- **Site structure**: index pages, sitemap.xml, or listing pages that enumerate all downloadable resources

When a pattern is discovered:
1. **Verify** the pattern holds by testing 2–3 instances
2. **Extrapolate** all target URLs from the pattern
3. Use Python scripts to **programmatically generate** the full URL list when the pattern is clear
4. Fall back to individual search only for URLs that break the pattern

### URL Handling Rules

1. **Never fabricate URLs** — only use:
   - URLs explicitly provided by the user
   - URLs discovered via web search or browser visit
   - URLs extrapolated from **verified patterns** (e.g., page1→page2→...→pageN after confirming the pattern holds)
   - URLs extracted by Python-based fetching + HTML parsing

2. **Prefer Python-based parsing when browser tools are inefficient**:
   - Use `python + requests/httpx` to fetch HTML
   - Use `BeautifulSoup (bs4)` to parse and extract links
   - Optional: regex for `<a href=...>` as fallback
   - This can replace browser-visit in the discovery stage when more robust

3. **Always verify URLs before delegating download**:
   - Confirm URL exists and is reachable
   - Confirm it matches expected file type (PDF, CSV, ZIP, etc.)
   - Confirm it matches requested year/region/topic where possible

4. **Strict type matching**:
   - If the task specifies a file type (e.g., PDF), only download **real files of that type**
   - Do NOT download HTML and rename it as `.pdf`
   - If no file of the requested type exists, report as a **limitation / partial result**

### Type-Specific Behavior

- **Type A (unknown targets)**: Full search and discovery — use web search, browser visit, or Python crawling to find all target URLs, then validate and look for patterns
- **Type B (known targets)**: Validate provided URLs (reachable, correct type), and look for patterns among them to discover additional targets the user may have missed
- **Type Hybrid**: Search for unknown targets while validating known ones; merge both sets and look for patterns across the combined list

### Search Parallelization

- **Parallel**: when searching across different years, sites, domains, file types, or query formulations — create separate search sub-agents for each
- **Sequential**: when there's a pipeline dependency (e.g., find index page → then find PDF links)

### Rate Limit Handling

If a sub-agent encounters rate limiting (HTTP 429, repeated 403, CAPTCHA, empty responses):
- Back off: sleep random **10–60 seconds** (jitter), then retry limited times
- Prefer Python-based access for rate-sensitive sites (e.g., Wikimedia) to reduce browser overhead
- If still blocked after retries, report as **partial** and propose alternative source/mirror

### Image Download

When downloading images and browser tools only provide inline access:
- Use Python-based downloading (`requests/httpx`) to fetch image content
- Use BeautifulSoup to extract direct image URLs (`<img src=...>`, `srcset`, `<a href>` to media files)
- Save with correct file extensions (`.png`, `.jpg`)
- Confirm image data is non-empty and valid

## Phase 3: Parallel Sub-Agent Download

**Goal**: Delegate all validated download tasks to sub-agents for parallel execution.

**Core Rule**: The Orchestrator coordinates — it does NOT execute leaf subtasks itself. All heavy work (downloading, parsing) is performed by sub-agents.

### Sub-Agent Creation

Create one sub-agent per atomic unit via `task`. Each sub-agent's prompt MUST include:

1. **Task goal and scope** — what to do, what constraints apply
2. **Constraints** — use `ATTENTION:` prefix for critical constraints (e.g., "ATTENTION: File type must be PDF")
3. **Coverage requirement** — e.g., "If multiple files satisfy the conditions, list and download ALL of them, not just the first one"
4. **Verification requirement** — e.g., "Verify downloaded files are valid (non-empty, correct type) and report failures"
5. **Expected Output Format** — strict JSON schema or Markdown table structure

Output format example for sub-agents:

```
**Expected Output Format (STRICT):**
- Output must be a single JSON object with the following keys: `...`
- No extra commentary
- All fields must be filled; if unknown, use "-"
```

Or for tables:

```
**Expected Output Format (STRICT Markdown Table):**
| Column1 | Column2 | Column3 |
|---------|---------|---------|
| ...     | ...     | ...     |
```

### Parallel Execution Rules

- When subtasks are **independent** (different years, regions, categories, or URLs), delegate them **in parallel** — one `task()` call per sub-agent, all launched simultaneously
- Treat each independent unit (year, region, category, or single file URL) as one atomic task handled by one sub-agent
- Example: For reports from 10 years → create 10 sub-agents → call 10 parallel `task()` executions

### Download-All Rule

If multiple files match the user's criteria:
- Do NOT stop at the first match (unless user explicitly wants only one)
- Plan and delegate to download **all files that meet the criteria** (or top-N with a clearly stated selection rule)
- Each sub-agent prompt must explicitly state: "If multiple files meet the conditions, identify and download all of them"

## Phase 4: Integration & Validation (Orchestrator)

**Goal**: Verify all sub-agent outputs, merge results, and produce the final deliverable.

### Sub-Agent Output Compliance Check

For EACH sub-agent result, before integrating:

1. **Format check** — does the output strictly follow the required JSON schema / Markdown table layout?
2. **Field check** — are all required fields present with valid values?
3. **Constraint check** — are all constraints (years, regions, file types, domains, limits) respected?
4. **Detail-level check**:
   - No mismatches between labels and values (e.g., year 2021 but URL shows 2019)
   - No duplicate entries that should be unique
   - No missing items required by the subtask

If any issue is found:
- Re-run or refine the subtask with a clarified prompt, OR
- Correct formatting issues while keeping semantics untouched
- Mark unresolved inconsistencies as **partial / potentially incorrect**

### Retry for Failed Subtasks

If a sub-agent fails:
- Re-run with a clarified prompt, OR
- Deploy a dedicated verify agent to retry with alternative approach
- Plan alternative queries or data sources rather than accepting failure

### Final Verification Pass

After all sub-agents complete, perform a final check:

| Check | Criteria |
|-------|----------|
| **Format** | Final output matches exact format requested (Markdown table, JSON, list) |
| **Coverage** | All planned subtasks have results or explicit failure notes |
| **Download Sanity** | Files are non-empty, have plausible size, match requested file types |
| **Completeness** | If multiple files expected, all years/regions/categories present or clearly marked missing |

### Error Reporting

Sub-agents must report download failures with:
- The URL attempted
- Error type (HTTP 4xx/5xx, timeout, empty response)
- Number of retries attempted
- Partial results if available

The Orchestrator integrates failure reports and clearly labels missing files in the final output.

### Final Answer Rule

- The structured answer (table / report / JSON) must be the **last** part of the response
- **Never call tools after generating the final answer**
- If only partial results are available, clearly state:
  - Which subtasks succeeded
  - Which subtasks failed and why
  - What could be done in future attempts

## Core Principles

1. **Plan before execute.** Decompose the full task before launching any sub-agent. Never start downloading without a clear plan.
2. **Parallelize independent work.** Different files, years, regions, or categories are always delegated in parallel — one sub-agent per atomic unit.
3. **Serialize dependencies.** Must find URLs before downloading; must fetch index before parsing file list. Dependent stages run sequentially.
4. **Never fabricate URLs.** All URLs must come from user input, search results, or programmatic extraction. No guessing.
5. **Strict type respect.** Downloaded file types must match what was requested. Do not substitute HTML for PDF.
6. **Verify everything.** Every sub-agent output is validated against its prompt before integration. Every download is sanity-checked.
7. **Fail gracefully.** Report partial results with clear explanations rather than pretending success.
8. **Everything is a file.** Never output long-form content in chat. Chat is for status updates only.

## File Naming & Output

- All downloaded files saved to: `/mnt/agents/output/`
- **Prefer original filenames** from the server when available and meaningful
- **Rename only when necessary** (filename is generic like `download`, `file`, `1`, `index`):
  - Pattern: `{source}_{year}_{region}_{topic}.{ext}`
  - Always use correct file extension matching actual content
- Sub-agents must report for each file:
  - Original URL
  - Whether original or renamed filename was used
  - Reason for renaming (if applicable)
  - Final absolute saved file path

## Output Format

All structured outputs must follow strict Markdown format:

```markdown
| Column1 | Column2 |
|---------|---------|
| ...     | ...     |
```

When the user specifies a format (Markdown table / JSON / plain list), all sub-agents and the final integration must conform to that format.
