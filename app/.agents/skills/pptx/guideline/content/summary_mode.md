# Summary Mode Workflow

When the user uploads a long document (such as a paper, report, article, etc.) and requests generating a presentation based on its content, in-depth understanding and distillation of the document is required, ultimately delivering a presentation outline.

## workflow

Based on the user requirements and audience analysis completed in generate_slides.md step2, proceed with content design.

### step1. In-Depth Document Understanding

Perform systematic reading and analysis of the user's uploaded document:

1. **Structure mapping**: Identify the document's overall structure -- chapter divisions, argument hierarchy, reasoning logic
2. **Core extraction**: Mark the document's core arguments, key data, important conclusions, and innovative viewpoints
3. **Audience adaptation**: Based on the target audience's expertise level, determine which content needs to retain its original depth, which needs simplified explanation, and which can be omitted
   - For professional audiences: Retain technical details, data-driven arguments, methodology
   - For non-professional audiences: Highlight conclusions and implications, simplify process descriptions, add background explanations

### step2. Supplementary Search (Optional)
- If the document content requires additional background information, data support, or the latest developments to enhance the presentation, conduct targeted searches
- Supplemented content must be clearly annotated with information sources (with URLs) to distinguish it from the original content

### step3. Content Reorganization and Narrative Design

Reorganize the document content into a narrative structure suitable for presentations:

1. **Narrative logic selection**: Prioritize the original text's narrative logic. If the original narrative logic has shortcomings, select an appropriate narrative approach based on the document type and audience:
   - Papers/research reports: Background -> Methods -> Findings -> Conclusions -> Implications
   - Industry reports: Current state -> Trends -> Opportunities and challenges -> Recommendations
   - Business proposals: Problem -> Analysis -> Solution -> Expected outcomes
   - Or other narrative structures that suit the content characteristics

2. **Content filtering and distillation**
   - Distill core viewpoints, with each page focusing on one clear information point
   - Retain key data, charts, and case studies from the original text as support; trim redundant arguments, repetitive content, and excessive details
   - Prioritize original content; mark search-supplemented content with "[supplemented]" in the outline

### step4. Outline Writing

Based on the content reorganization results, use the `write_file` tool to construct the presentation outline `outline.md`.

#### Outline Design Principles

1. **Faithful to the original**: The outline structure should reflect the core logic of the original text without deviating from the document's main thesis
2. **Information density**: Each page should have substantive, in-depth content, prioritizing analytical conclusions, core insights, and key data over simple excerpts
3. **Page transitions**: Content between pages should be interconnected with natural, smooth transitions
4. **Page types**: Set a type for each page (cover/table_of_contents/chapter/content/final)

#### Page Count Control

1. **User did not specify page count**: Design based on document content volume and information density, recommended 12-18 pages; be sure to include cover, table of contents, chapters, content, and ending pages
2. **User specified a page count**: Design according to the user's requirement; encouraged to include cover, table of contents, chapters, content, and ending pages. If the page count is small (e.g., 5 or fewer), focus on content pages to increase information density

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
- **Content**: Chapter subtitle or other content to be presented on the page. Ensure the chapter title accurately summarizes all content within that chapter without being overly narrow!

## Page 4 [content]
- **Title**: Title of the page
- **Content**: Reference the original text's "chapter name/paragraph location" (e.g., Chapter 3 "Market Analysis", Section 2.1 "Experimental Methods"), and distill core information points from that section, summarizing in one or two sentences the key message this page should convey. If search supplementation was performed, mark supplemented content with "[supplemented]" in the outline
- **Source**: Search information source for supplemented content on this page (annotated with URL), e.g., https://example.com/report-2025

......

## Page x [final]
- **Title**: Title of the ending page
- **Content**: Core viewpoints/insights/inspirations, or thought-provoking questions, or thank-you messages, etc. Determine based on the user's scenario
```

#### Chapter Consistency

If the outline includes chapter transition pages (type=chapter), the transition pages across different chapters must be set uniformly -- either every chapter has one or none do. It is strictly forbidden to have transition pages for only some chapters.

## Writing Guidance for PPTD Generation

1. **Faithful to the original**: Distill rather than rewrite. Do not add viewpoints or data that do not exist in the original text. Page content must have corresponding basis in the source document
2. **Make good use of hyperlinks: When the PPT involves reference materials, further reading, or other external resources, use `<a href="url">` to add hyperlinks to related text, making it convenient for the audience to explore further**
3. **Per-page focus**: Each page should develop around the key points annotated in the outline, supported by key data and case studies from the original text. It is acceptable to condense verbose original text into concise expressions suitable for presentations, but core information must not be lost

## NEXT STEP
1. If visual design has not been completed, complete visual design and generate `design.md` first
2. When both `design.md` and `outline.md` are complete, proceed to generate_slides.md step6 to generate the presentation
