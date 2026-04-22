# Multi-Agent Presentation Creation

> This document guides how to create long presentations by coordinating multiple agents

## File Isolation
Create an independent working directory for the current PPT task (directory name based on the English short name of the title/topic), and write all artifacts into this directory:
```
output/<ppt-dir>/
├── design.md          # Design document
├── outline.md         # Outline document
├── <ppt-name>.pptd   # PPT main entry file
└── pages/             # .page file directory
```

## Workflow

### step1: Requirements and Audience Analysis
- Analyze the requirements of the final presentation, including:
  1. Language requirements: Are there specific language requirements? If not, keep consistent with the user's input language
  2. Prerequisites: Are there reference materials from previous workflows? Such as artifacts in various formats from previous processes (markdown, docx, etc.), search results (content returned by search tools), or no prerequisites at all
  3. Page count requirements: Does the user have specific page count requirements? Such as explicitly requesting 20, 50, or even 100 pages, etc.
    * If the user has no specific page count requirements, the page count should be determined based on prerequisites, e.g.: collected 20 papers -> generate 20/40/60 content pages + n cover/TOC/chapter pages; collected 100 company profiles -> generate 100 content pages + n cover/TOC/chapter pages, etc.
    * If there are no prerequisites, the page count can be left tentative and decided based on subsequent research content
  4. Content requirements: Does the user have specific requirements for charts, data, conclusions, topics, or language style, or are there key information in the prerequisites that needs to be highlighted
  5. Visual requirements: Does the user have specific design style, color scheme, or image/chart style requirements; or are there corresponding content in the prerequisites
  6. Audience analysis: Analyze the target audience the user may be addressing, including age, profession, expertise level, expected content presentation style, etc.

### step2: Determine Working Mode
Based on the user requirements analyzed in step1, determine which working mode to enter:
- Visual mode:
  1. Creative mode: No visual references, only style/color requirements provided or nothing at all
  2. Replication/Reference mode: Uploaded images or websites, requesting you to replicate them as PPT; or create a PPT in the same style as reference screenshots, etc.
  3. Template mode: Uploaded a PPT and requested it as a template for creating a new PPT, or explicitly specified using a preset template
- Content mode:
  1. Summary mode: Uploaded long documents (such as papers, reports, etc.) to generate PPT based on the content; or previous workflows have generated prerequisite documents that need to be referenced for PPT creation
  2. Outline mode: Provided an outline with per-page content already planned; or provided very structured content, etc.
  3. Search mode: No outline or long document provided, only a topic and related requirements, requiring you to search and supplement content, etc.

### step3: Visual Design
- Based on the visual mode determined in step2, enter the corresponding visual design workflow, **use the write_file tool** to complete the visual design document `<ppt-dir>/design.md`
  1. Replication/Reference mode: Read guideline/design/reference_mode.md for more information
  2. Creative mode: Read guideline/design/creative_mode.md for more information
  3. Template mode: Read guideline/design/template_mode.md for more information
    * Note: Template mode should only be entered when the user explicitly requests using an uploaded PPT as a template or specifies using a preset template! Otherwise, reading template_mode.md is strictly prohibited!
- **design.md is the core visual reference for subsequent presentation generation. It must be persisted using the write_file tool for step5 to read and reference. It is strictly prohibited to only output it in the conversation.**

### step4: Content Design
- Based on the content mode determined in step2, enter the corresponding content design workflow, **use the write_file tool** to complete the content design document `<ppt-dir>/outline.md`
  1. Summary mode: Read guideline/content/summary_mode.md for more information
  2. Outline mode: Read guideline/content/outline_mode.md for more information
  3. Search mode: Read guideline/content/search_mode.md for more information
- **outline.md is the core content reference for subsequent presentation generation. It must be persisted using the write_file tool for step5 to read and reference. It is strictly prohibited to only output it in the conversation.**

### step5: Generate Presentation
- Refer to the image supplementation strategy below to add appropriate illustrations to the presentation
- Generate the presentation (including .pptd file and .page files) based on the visual design and content outline.
- If outline.md includes source URLs, use `<a href="url">` when generating PPTD to link key data, cited viewpoints, etc. to the original source pages, making it convenient for the audience to trace and verify.

#### Image Supplementation Strategy
1. Prioritize extracting suitable images from user-uploaded content (such as Word, PDF, PPTX, etc.) as presentation illustrations
2. If the user has not provided sufficient and suitable images, and has not explicitly requested no additional images, you should by default use image search, image generation tools, etc. to prepare appropriate illustrations for the presentation
3. Image search strategy:
  - Collected images should reference the visual design style in design.md, pursuing movie poster or magazine cover level visual impact and aesthetics. Prioritize high-resolution, watermark-free images
  - Using English keywords for searches typically yields higher quality results. Append style keywords to match the design style. Never include words like PPT, presentation, premium color scheme: these will cause search results to return PPT screenshots
  - Do not search for data charts (line charts, bar charts, pie charts, etc. — use chart elements), table screenshots (use table elements), icons (use icon elements), or diagrams (flowcharts, hierarchy diagrams, architecture diagrams, etc. — use shape+text+line element combinations)
4. Retry strategy: If initial search results are of poor quality, you must try different keywords or use image generation tools (if available). ***Never use low-quality images or substitute with gradients/solid colors/placeholders!**
  - Do not replace image slots that originally need images with solid color backgrounds, gradient fills, shape compositions, etc. just because searching is difficult. If a suitable image truly cannot be found, use the closest search result rather than removing the image.
5. Image usage guidelines
  - Cover/chapter/closing pages: Full-bleed high-quality images with gradient masks are recommended to create visual impact
  - Content pages: Images should be directly relevant to the page content; avoid purely decorative images
  - Image sizing: Set sizes appropriately based on layout needs; cropping is preferred; avoid stretching unless necessary

#### 1. Main Agent Creates .pptd File
- Read the format requirements defined in format/pptd.md, and generate the main entry .pptd file under `<ppt-dir>/`
- This file defines the presentation's theme and plans the pages

#### 2. Create .page Files

> **Condition check**: Only when the user requests creating **1 PPT** with **<= 20 pages**, the main agent may skip the sub-agent workflow and complete the .page files on its own, proceeding directly to step6. In all other cases (multiple PPTs, or a single PPT with more than 20 pages), always delegate to sub-agents.

1. Based on the number of .page files to be created, use create_subagent to create sub-agents. The following information must be declared when creating:
  * The identity is a **pptx page building sub-agent** (not the main agent)
  * The main agent has already completed the design.md design document, outline.md content outline document, and the pptname.pptd main entry file design
  * The goal is to build x .page files
  * The following content must be read before execution for guidance:
    a. {skill_path}/format/pptd.md: Format definition of the pptd file
    b. {skill_path}/guideline/design/profiles/xxxx.md: Corresponding preset scene reference (depends on which preset scene was read before generating design.md)
    c. The design.md file produced by the main agent
    d. The .pptd file produced by the main agent
    e. The outline.md file produced by the main agent
    f. {skill_path}/guideline/subagent/attention.md: Notes for creating presentations

2. Assign tasks to sub-agents: Use task to assign tasks to sub-agents: assign 20 pages of production tasks to each sub-agent. The following information must be declared when assigning tasks:
  * The sub-agent's content writing mode: Based on the current situation, inform the sub-agent which writing guide to read
    * Summary writing (read {skill_path}/guideline/subagent/summary_writing.md): Used when there is a clear content source. Including: previous workflows have document deposits, or no document deposits but the main agent has obtained complete information on its own
    * Search writing (read {skill_path}/guideline/subagent/search_writing.md): Used when there are no document deposits and the sub-agent needs to search and expand content on its own
  * Which pages should be created: Simply inform the file names of the pages to be created in the .pptd main entry file
  * Declare documents that the sub-agent needs to reference — **Primary principle: For any file already persisted to disk, always pass the file path and let the sub-agent read the full content on its own. It is strictly prohibited to summarize, abstract, or paraphrase file content before passing it to the sub-agent!** Any form of summarization leads to information loss — the sub-agent receives degraded information, significantly reducing generation quality. Specific rules:
    - If reference content already exists as files (whether markdown/docx/txt produced by previous workflows, or intermediate files generated by the main agent), directly provide the file paths and their purpose, e.g.: `When creating slide_03~08, you must fully read output/xxx/research_report.md and output/xxx/company_data.md`
    - If reference content only exists in the main agent's context (e.g., search results, user supplements in conversation, not written to files), you should **first use write_file to persist the content as files**, then pass the file paths to the sub-agent; if there is truly no persistable content, provide all potentially needed **complete original content** to the sub-agent, as comprehensive as a research report, ensuring this content can support the creation of the corresponding number of PPT pages
> Task assignment logic: Prioritize assigning similar pages to the same sub-agent: e.g., one sub-agent handles all covers, table of contents, and chapter transition pages, while other n sub-agents handle content pages, etc.; rather than having each sub-agent handle both chapter transition pages and content pages.

### Multi-Presentation Workflow
When the user requests creating multiple presentations, **you must adopt a generate-all-first, then check-one-by-one strategy!** That is: the main agent first completes all PPTs' design.md, outline.md, and .pptd files, then collectively creates sub-agents to assign all PPTs' .page production tasks, and only proceeds to unified checking, fixing, and delivery after all presentations are created. **Never complete one PPT and immediately check, fix, and deliver it before creating the next PPT**.

### step6: Check .pptd File

1. Check
- After all sub-agents complete their .page file creation, the built-in checker **must** be used to check the files, ensuring no format errors or unexpected overflow issues.
- The main agent should run the checker **without the `--pages` parameter** to perform a full check on all pages (sub-agents have already checked their own pages using `--pages`; this serves as the final full verification):

```bash
{skill_path}/scripts/check.sh filename.pptd
```

- The checker will check the following issues, divided into Error and Warning categories:
  * Format check: Whether YAML syntax is valid, required fields are present, field values are valid, elementId is unique within pages, etc.
  * Data validation: Color format and reference validity, elements exceeding page boundaries, shapeName validity, chart/table data completeness
  * Layout detection: Text occlusion, text box misalignment with underlying containers
  * Text box content detection: Text width/height overflow, text underfill

2. Fix
Fix the issues found in your created pages using the following approaches. **No need to address issues in other pages**
- Fix all ERRORs first: These issues will cause conversion failure and must be fixed
- Then handle WARNINGs: **PPTD renders precisely and will not automatically scale text or adjust layouts. Every WARNING reported by the checker means the final PPTX will have a corresponding visual issue (truncation, occlusion, overflow, etc.) that will not be auto-corrected.** Therefore, WARNINGs must be fixed by default, unless you can clearly determine the WARNING is part of the intended design (e.g., decorative elements intentionally extending beyond the canvas). If skipping a WARNING, you must explain the reason for skipping.
- **Parallel fixing**: **Must call the edit_file tool in parallel as many times as possible in a single response**, fixing issues across multiple files at once, rather than fixing files one by one sequentially.
  1. TextOverflowWarning (text overflow): Text content requires more space than the text box provides, causing content truncation (must fix)
  2. TextOcclusionWarning (text occlusion): Text is occluded by other elements (images/shapes/text boxes, etc.), making text unreadable
  3. TextDriftWarning (text drift): Text box is intersected by other elements, or is not fully aligned with underlying shapes/images
  4. TextUnderfillWarning (text underfill): Text box is too large or font size too small, leaving large blank areas in the text box, often resulting in unexpected blank space on the page
  5. BoundsOutsideWarning (out of bounds): Element is partially or fully outside the canvas, making it partially or fully invisible

3. Re-verification
- After fixing, **rerun the checker** and **must review the complete output** (using grep/sed to filter is prohibited). Focus on verifying the count of each issue type in the Summary at the bottom, confirming all ERRORs are eliminated and all unexpected WARNINGs are handled. If there are remaining issues, continue fixing and repeat verification until the Summary shows `0 errors, 0 warnings`. **It is strictly prohibited to use grep to filter and only view/fix partial issues!**

#### Fix Precautions
- Maintain margins: After adjusting element bounds, check whether reasonable spacing is still maintained between the element and page edges, adjacent elements, and bottom elements. Do not forget to leave appropriate margins when adjusting bounds to resolve text overflow or whitespace issues, causing text boxes to be pressed against edges and losing original margins. **Fixed bounds should maintain consistent margins with other elements of the same type on the page.**
- Do not move common element positions: Common elements on pages (such as navigation bars, titles, corner badges, etc.) should maintain consistent positions across pages. When layout issues exist, prioritize adjusting content layout to avoid subtle differences in common elements across pages (such as inconsistent heights, font sizes, etc.; intentionally designed special layouts are exceptions)
- Ensure content alignment: When adjusting element A, ensure related elements are adjusted in sync. Common situations include:
  * Adjusted text box size but did not sync the background color/card size beneath the text box
  * Adjusted element A's position but did not sync attached decorative elements (such as decoration bars, progress bars, etc.) in size and position, causing misalignment

#### Text Overflow Fix Strategy
When the checker reports TextOverflowWarning, fix in the order suggested by the checker:
- Height overflow:
  1. Condense text: Compress expressions, merge bullet points, remove secondary content
  2. Reduce font size: Decrease content font size, line spacing, paragraph spacing, etc.
  3. Expand text box height: If the above approaches are not feasible and there is space below the text box, increase the bounds height to accommodate content. But be careful not to create overlap or drift issues
- Width overflow:
  1. Condense text: Shorten text content, reduce the content amount to the percentage suggested by the checker
  2. Switch to multi-line: Set `wrap: true` to enable auto-wrap, and adjust the text box height and layout accordingly
> **It is prohibited to excessively reduce font size to eliminate overflow, causing large blank areas in the text box** — this is worse aesthetically than minor overflow.

### step7: Deliver .pptd File
- Inform the user that the presentation is complete, and summarize the content highlights, key insights, specific structure, and other key information of the presentation.
- Inform the user they can click the card in the conversation to view and download the presentation in pptx format
