# Outline Mode Workflow

When the user provides a pre-planned outline (per-page content planning, structured outline, hierarchical tree-structured outline, etc.) and requests generating a PPT based on it, enter outline mode.

## workflow

Based on the user requirements and audience analysis completed in generate_slides.md step2, proceed with content design.

### step1. Outline Parsing and Understanding

Identify the type of outline the user has provided:
- **Complete outline**: Page-by-page planning with titles, content points, and page types for each page
- **Semi-structured outline**: Provides chapter divisions and key points, but does not explicitly specify page types or per-page allocation
- **Hierarchical tree outline**: Only provides hierarchical topics and subtopics

Understand the following information from the outline:
- Total page count or content volume
- Content allocation per page/section
- Implicit requirements (e.g., whether cover, table of contents, chapter transition pages are needed)

### step2. User Intent Assessment and Outline Completion

First assess the user's attitude toward content modifications, then adopt a strategy based on the outline type:

#### User Intent Assessment

- **Explicitly requests no content changes** (e.g., "follow my outline exactly", "don't add or remove content", "strictly follow the outline"): **Strictly follow the content provided by the user** -- do not add, remove, expand, or rephrase. Only perform necessary page allocation and page type mapping. When cover/ending pages are missing, ask the user whether they want them added rather than adding them on your own.
- **Explicitly requests content expansion** (e.g., "help me enrich this", "there's too little content, add more", "expand the details"): While maintaining the user's outline structure, proactively supplement supporting arguments, data, case studies, etc., and clearly mark which content was supplemented.
- **No explicit statement** (most cases): **Default to conservative** -- faithfully present the user's provided content, only suggest adding obviously missing structural pages (cover, ending page, etc.), and do not proactively expand body content.

### step3. Information Supplementation (Optional)

**Only execute this step when the user explicitly requests content expansion, or when a page in the outline requires factual content that the AI does not possess.** If the user requires strict adherence to the outline, skip this step.

If information supplementation is needed (data, case studies, citations, etc.):
- Refer to guideline/search/text_search.md for text supplementation strategies

### step4. Outline Writing

Based on the user's outline and completion results, use the `write_file` tool to construct the presentation outline `outline.md`.

1. **Faithful to user outline**: The outline structure should align as closely as possible with the user's provided outline content, or reflect the user's content planning, without deviating from the user's intent
2. **Information density**: Plan each page's content reasonably, ensuring natural transitions and substantive, in-depth content on each page.
3. **Page types**: Set a type for each page (cover/table_of_contents/chapter/content/final)
4. **Page count requirements**:
  - When the user's outline already has page count requirements, or content is strictly planned per page: Design according to the user's outline page count
  - When the user's outline does not explicitly require page count, but the outline is highly structured: Page count should match the structured design of the outline
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
- **Content**: Directly retain the user's original wording, or quote the original points from the corresponding section of the user's outline. If search supplementation was performed, mark supplemented content with "[supplemented]" in the outline
- **Source**: Search information source for supplemented content on this page (annotated with URL), e.g., https://example.com/report-2025

......

## Page x [final]
- **Title**: Title of the ending page
- **Content**: Core viewpoints/insights/inspirations, or thought-provoking questions, or thank-you messages, etc. Determine based on the user's scenario
```

## Writing Guidance for PPTD Generation

1. **Make good use of hyperlinks: When the PPT involves reference materials, further reading, or other external resources, use `<a href="url">` to add hyperlinks to related text, making it convenient for the audience to explore further**
1. Faithful to user outline: Strictly build upon the user's original points cited in the outline, without adding viewpoints not mentioned by the user or deviating from the outline direction
2. Preserve user wording: Key terms, titles, and expressions from the user's outline should retain the original wording as much as possible, without arbitrary rewording
3. Moderate expansion: Transform key points into visual presentation suitable for slides -- neither copying the original text verbatim nor extensively expanding it
4. If required to fully follow the user's outline, strictly organize page content based on the user's original points, ensuring every point is presented without adding extra content; for pages supplemented through search, the user's points should remain the main body with search-supplemented content serving as supporting arguments, maintaining clear prioritization

## NEXT STEP
1. If visual design has not been completed, complete visual design and generate `design.md` first
2. When both `design.md` and `outline.md` are complete, proceed to generate_slides.md step6 to generate the presentation
