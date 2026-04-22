# Search Mode Workflow

When the user provides no outline or long document, only a topic and related requirements, requiring you to search and supplement content on your own, enter search mode.

## workflow

Based on the user requirements and audience analysis completed in generate_slides.md step2, proceed with content design.

### step1. Information Gathering

- Refer to guideline/search/text_search.md for text search strategies

Notes during searching:
- Prioritize data and viewpoints from authoritative sources
- Focus on the latest industry trends and data
- Collect specific case studies as supporting arguments
- Record information sources for subsequent annotation

### step2. Content Reorganization and Narrative Design

Reorganize the gathered information into a narrative structure suitable for presentations:

1. **Narrative logic selection**: Select an appropriate narrative approach based on the topic and audience
   - Industry analysis: Current state -> Trends -> Opportunities and challenges -> Recommendations
   - Knowledge overview: Background -> Core concepts -> Case studies -> Summary
   - Business proposal: Problem -> Analysis -> Solution -> Expected outcomes
   - Or other narrative structures that suit the content characteristics

2. **Content filtering and distillation**
   - Each page should focus on one clear information point, distilling all useful information from the search results
   - Support viewpoints with key data and case studies
   - Ensure accuracy and timeliness of information

### step3. Outline Writing

Based on the content reorganization results, use the `write_file` tool to construct the presentation outline `outline.md`.

1. **Substantive content**: Reference multiple sources, cluster and filter useful information. Each page should have substantive content and data support, prioritizing analytical conclusions, core insights, and key data rather than staying at a surface level
2. **Page transitions**: Content between pages should be interconnected with natural, smooth transitions
3. **Page types**: Set a type for each page (cover/table_of_contents/chapter/content/final)
4. **Page count requirements**:
  - When the user already has page count requirements: Design according to the user's outline page count
  - When the user does not explicitly require page count but provides a structured outline: Page count should match the structured design of the outline
  - No page count requirements or structure: Design based on content volume, recommended 12-18 pages; encouraged to include cover, table of contents, chapters, content, and ending pages
5. Chapter consistency: Either set chapter pages for all chapters or for none -- it is strictly forbidden to have transition pages for some chapters but not others

#### Outline Format

```markdown
# Presentation Outline

## Page 1 [cover]
- **Title**: Title of the presentation
- **Content**: Subtitle of the presentation, may be empty

## Page 2 [table_of_contents]
- **Title**: Table of contents heading. e.g., Table of Contents, Executive Overview, etc.
- **Content**: Chapter plan of the presentation. e.g., 1. Chapter One Title; 2. Chapter Two Title, ...

## Page 3 [chapter]
- **Title**: Chapter number and name. e.g., Chapter 1: xxx, 01: xxx
- **Content**: Chapter subtitle or other content to be presented on the page. Ensure the chapter title accurately summarizes all content within that chapter without being overly narrow

## Page 4 [content]
- **Title**: Title of the page
- **Content**: Core viewpoints distilled from search findings, summarizing in one or two sentences the key message this page should convey
- **Source**: Search information sources referenced for this page (annotated with URL), e.g., https://example.com/report-2025

......

## Page x [final]
- **Title**: Title of the ending page
- **Content**: Core viewpoints/insights/inspirations, or thought-provoking questions, or thank-you messages, etc. Determine based on the user's scenario
```

## Writing Guidance for PPTD Generation

1. **Information reliability**: Based on the search sources annotated in the outline, ensure that cited data and viewpoints come from reliable sources. Key data should be attributed on the page (e.g., "According to IDC's 2025 report"), and use `<a href="url">` hyperlinks to point to the original source page, enabling the audience to directly trace and verify
2. **Post-search distillation**: Distill and organize information from search findings before presenting, rather than simply piling up search results
4. **Per-page focus**: Each page should develop around the key points annotated in the outline, supported by data and case studies from the corresponding search findings. Ensure each page has substantive data, case studies, or analysis, rather than staying at a surface-level overview

## NEXT STEP
1. If visual design has not been completed, complete visual design and generate `design.md` first
2. When both `design.md` and `outline.md` are complete, proceed to generate_slides.md step6 to generate the presentation
