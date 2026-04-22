---
name: longread
description: >
  Use this skill when an agent (main agent or subagent) encounters a file too
    large to read in a single pass — e.g. cat, read_file, or Read tool hits size
    limits or truncates output. First assess whether the file is suitable for
    chunk-based parallel reading, then proceed accordingly. Supports PDF, DOCX,
    TXT, MD, PPTX files. NOT for structured data (CSV, DTA, XLSX, etc.).
user-invocable: true
allowed-tools: Bash, Read, Agent, Glob
argument-hint: <file_path>
---

# Longread Skill

Use this skill when a file is too large to read in a single pass (e.g. cat, read_file, or Read tool hits size limits or truncates output).

## Step 0: Assess Suitability (REQUIRED)

Before splitting, determine whether the file is actually suitable for the chunk-and-summarize pattern. **Not all large files benefit from this approach.**

### Files SUITABLE for this skill (non-structured, prose-like content):
- PDF documents (reports, papers, books, manuals)
- DOCX documents (articles, contracts, essays)
- TXT / MD files (long-form text, documentation)
- PPTX files (slide decks with text content)

### Files NOT suitable — use code instead:
- **CSV, TSV, DTA, XLS/XLSX** — structured/tabular data. Use pandas, Stata, or other data tools to query, filter, aggregate. Splitting rows across chunks destroys data integrity.
- **JSON, JSONL** — structured data. Use jq or Python to parse and extract.
- **Log files** — typically need grep/awk/filtering, not summarization.
- **Source code files** — use grep, AST tools, or targeted reads with offset/limit.

### Also consider whether the task itself fits the pattern:
- **Suitable tasks**: summarization, information extraction, question answering over prose, finding specific sections in a long document.
- **Unsuitable tasks**: statistical analysis, counting, aggregation, joins, sorting, exact search — these need code, not parallel reading.

**If the file or task is unsuitable, do NOT proceed with this skill.** Instead, use the appropriate tool (Python/pandas for data, grep for logs, targeted Read with offset for code, etc.) and tell the user why you chose that approach.

---

## Workflow (only after confirming suitability)

### Step 1: Split the Document

```bash
python /app/.agents/skills/longread/scripts/split_doc.py <file_path>
```

The script will output JSON with chunk file paths:
```json
{
  "status": "success",
  "chunk_files": ["/mnt/agents/chunks/doc_part_1.txt", ...],
  "num_chunks": 5
}
```

### Step 2: Create a Reader Subagent

```
create_subagent(
  name="chunk_reader",
  system_prompt="You are a document reader. Read the assigned chunk carefully and extract key information. Summarize the main points concisely."
)
```

### Step 3: Launch Parallel Tasks

For each chunk file, launch a subagent in **parallel** (single message, multiple tool calls):

```
task(agent="chunk_reader", prompt="Read /mnt/agents/chunks/doc_part_1.txt and summarize the key points.")
task(agent="chunk_reader", prompt="Read /mnt/agents/chunks/doc_part_2.txt and summarize the key points.")
...
```

### Step 4: Aggregate Results

After all subagents complete, combine their summaries to answer the user's original question.

## Script Options

The split script supports:
- PDF, DOCX, TXT, MD, PPTX files
- Default chunk size: 32k tokens with 10% overlap
- Output directory: `/mnt/agents/chunks/`
