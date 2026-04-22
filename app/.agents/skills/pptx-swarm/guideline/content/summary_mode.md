# Summary Mode Workflow

When the user uploads a long document (such as a paper, report, article, etc.) and requests generating a presentation based on the content, it is necessary to deeply understand and distill the document, ultimately delivering a presentation outline.

## workflow

Based on the user requirements and audience analysis completed in generate_slides.md step1, proceed with content design.

### step1. Deep Document Understanding

Perform systematic reading and analysis of the document uploaded by the user:

1. **Structure analysis**: Identify the overall structure of the document — chapter divisions, argument hierarchy, reasoning logic
2. **Core extraction**: Mark the core arguments, key data, important conclusions, and innovative viewpoints in the document
3. **Audience adaptation**: Based on the target audience's expertise level, determine which content should retain original depth, which needs simplified explanation, and which can be omitted
   - For professional audiences: Retain technical details, data-driven arguments, methodology
   - For non-professional audiences: Highlight conclusions and insights, simplify process descriptions, supplement with background explanations

### step2. Content Reorganization and Narrative Design

Reorganize document content into a narrative structure suitable for presentations:

1. **Narrative logic selection**: Prioritize the original text's narrative logic. If the original narrative logic has flaws, choose an appropriate narrative approach based on document type and audience:
   - Papers/research reports: Background → Methods → Findings → Conclusions → Implications
   - Industry reports: Current state → Trends → Opportunities & Challenges → Recommendations
   - Business proposals: Problem → Analysis → Solution → Expected outcomes
   - Or other narrative structures that fit the content characteristics

2. **Content filtering and distillation**
   - Distill core viewpoints, with each page focusing on one clear information point
   - Retain key data, charts, and case studies from the original text as support; trim redundant arguments, repetitive content, and excessive details
   - Prioritize original text content; mark search-supplemented content with "[Supplemented]" in the outline

### step3. Outline Writing

Based on the content reorganization results, use the `write_file` tool to construct the presentation outline `outline.md`.

#### Outline Design Principles

1. **Faithful to original text**: The outline structure should reflect the core logic of the original text, without deviating from the document's main theme
2. **Information density**: Each page should have substantial, in-depth content, prioritizing analytical conclusions, core insights, and key data, rather than simple excerpts
3. **Page transitions**: Content between pages should be logically connected with smooth, natural transitions
4. **Page types**: Assign a type to each page (cover/table_of_contents/chapter/content/final)

#### Page Count Control

1. **User did not specify page count**: Design based on document content volume and information density at your discretion, recommended 12-18 pages; be sure to include cover, table of contents, chapter, content, and final pages
2. **User specified page count**: Design according to user requirements; encouraged to include cover, table of contents, chapter, content, and final pages. If the page count is small (e.g., within 5 pages), focus on content pages and increase information density

#### Outline Format

```markdown
# Presentation Outline

## Page 1 [cover]
- **Title**: Title of the presentation
- **Subtitle**: Subtitle of the presentation, may be empty
- **Other info**: Information to display on the cover such as speaker name, date, organization/company name, logo description, etc. May be empty

## Page 2 [table_of_contents]
- **Title**: Wording such as Table of Contents, Executive Overview, etc.
- **Chapter list**: List all chapter titles in full, which must match the titles of subsequent chapter pages. E.g.:
  1. Chapter One Title
  2. Chapter Two Title
  3. ...

## Page 3 [chapter]
- **Title**: Chapter number and chapter name. E.g.: chapter 1: xxx, 01: xxx, Chapter One: xxx
- **Subtitle**: Chapter subtitle, may be empty
- **Introduction**: Core introduction or overview description of this chapter, helping sub-agents understand the overall direction of the chapter. May be empty

## Page 4 [content]
- **Title**: Title of this page
- **Content**: Reference the original file name/chapter name/paragraph location, and summarize in one sentence the core content this page aims to convey and its intended purpose. Do not describe specific chart data, chart types, or other detailed content to be placed. Do not use bullet points. Recommended around 50 words
- **Sources**: Citation numbers or URLs referenced on this page. If prerequisite dependency files contain `[^N^]` citation markers (pointing to URLs in `.citation.jsonl`), annotate the corresponding numbers here; when generating PPTD, these should be converted to `<a href="url">` hyperlinks

......

## Page x [final]
- **Title**: Title of the final page
- **Core message**: Core viewpoint/insight/inspiration, or a thought-provoking question, or thank you for watching, etc.
- **Other info**: Information to display on the final page such as contact details, QR code description, acknowledgment recipients, etc. May be empty
```

#### Chapter Consistency

If the outline includes chapter transition pages (type=chapter), transition pages across different chapters must be set uniformly — either every chapter has one, or none do. It is strictly forbidden to have transition pages for only some chapters. If the outline includes a table_of_contents page, its chapter list must match the titles of all chapter pages.

## Writing Guidelines When Generating PPTD

1. **Faithful to original text**: Distill rather than rewrite; do not add viewpoints or data that do not exist in the original text. Page content must have corresponding evidence traceable in the original document
2. **Make good use of hyperlinks: When the PPT involves reference materials, further reading, or other external resources, use `<a href="url">` to add hyperlinks to relevant text, making it convenient for the audience to explore further**
3. **Per-page focus**: Each page should develop around the key points noted in the outline, supported by key data and case studies from the original text. It is acceptable to condense verbose original text into concise expressions suitable for presentations, but core information must not be lost

## NEXT STEP
1. If visual design has not been completed, complete visual design and generate `design.md` first
2. When both `design.md` and `outline.md` are completed, proceed to generate_slides.md step5 to generate the presentation
