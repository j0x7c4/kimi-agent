# Presentation Generation

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

### step1: File Reading
- If the user has uploaded files, **read them in full** first, including images, documents, websites, etc. Do not proceed until all files have been fully read.

### step2: User Requirements and Audience Analysis
- Analyze the user's requirements for the final presentation, including:
  1. Language requirements: Does the user have a specific language preference? If not, match the language of the user's input
  2. Provided content requirements: Did the user provide a research topic, or a complete outline with page-level planning? Are there complete reference materials or reference images?
  3. Page count requirements
  4. Content requirements: Does the user have specific charts, data, conclusions, or topic requirements, or specific requirements for language style?
  5. Visual requirements: Does the user have specific design style or color scheme requirements, or specific requirements for images, charts, and other elements?
  6. Audience analysis: Analyze the target audience the user is likely addressing, including age, profession, expertise level, expected content presentation style, etc.

### step3: Determine Working Mode
Based on the user requirements analyzed in step2, determine which working mode to enter:
- Visual mode:
  1. Replication/Reference mode: e.g., user uploads images or websites and asks you to replicate them as PPT; or asks to create a PPT in the same style as reference screenshots
  2. Creative mode: No visual references provided, only style/color requirements or nothing at all
  3. Template mode: User uploads a PPT and requests it be used as a template for a new PPT, or explicitly specifies using a preset template
- Content mode:
  1. Summary mode: e.g., user uploads a long document (such as a paper, report, etc.) and asks you to generate a PPT based on it
  2. Outline mode: e.g., user provides an outline with per-page content planning; or provides a highly structured outline
  3. Search mode: User provides no outline or long document, only a topic and related requirements, requiring you to search and supplement content

**Note: If entering template mode, perform step5 content design first, then combine with content for step4 visual design!!**

### step4: Visual Design
- Based on the visual mode determined in step3, enter the corresponding visual design workflow, **use the write_file tool** to complete the visual design document `<ppt-dir>/design.md`
  1. Replication/Reference mode: Read guideline/design/reference_mode.md for more information
  2. Creative mode: Read guideline/design/creative_mode.md for more information
  3. Template mode: Read guideline/design/template_mode.md for more information
    * Note: Only enter template mode when the user explicitly requests using the uploaded PPT as a template or specifies using a preset template! Otherwise, reading template_mode.md is strictly forbidden!
- **design.md is the core visual reference for subsequent presentation generation. It must be persisted using the write_file tool for step6 to read and reference. It is strictly forbidden to only output it in the conversation.**

### step5: Content Design
- Based on the content mode determined in step3, enter the corresponding content design workflow, **use the write_file tool** to complete the content design document `<ppt-dir>/outline.md`
  1. Summary mode: Read guideline/content/summary_mode.md for more information
  2. Outline mode: Read guideline/content/outline_mode.md for more information
  3. Search mode: Read guideline/content/search_mode.md for more information
- **outline.md is the core content reference for subsequent presentation generation. It must be persisted using the write_file tool for step6 to read and reference. It is strictly forbidden to only output it in the conversation.**

### step6: Generate Presentation
- Refer to the image supplementation strategy below to add appropriate illustrations to the presentation
- Generate the presentation based on the visual design and content outline. Ensure full compliance with the format requirements defined in format/pptd.md during generation.
- If outline.md contains annotated source URLs, use `<a href="url">` in the PPTD to link key data, cited viewpoints, etc. to the original source pages, making it easy for the audience to trace and verify.
- Generation order: Files must be generated in the following order. Skipping pages or writing page files first is strictly forbidden:
  1. First generate the .pptd main file under `<ppt-dir>/`
  2. Then generate .page files in page order: Starting from page 1, generate sequentially according to the page order in outline.md, without skipping or reordering
  * The reason: The .pptd main file defines the global theme and page list, serving as the contextual foundation for all page files. Sequential generation ensures content continuity and style consistency between pages, avoiding context breaks caused by page skipping.

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

#### Text Box Size Estimation
- Text box wrapping control: When generating PPTD, you **must** explicitly set `wrap: false` for every text box intended to display on a single line: title text boxes, labels/badges, data numbers, navigation elements, etc.
- Line height calculation: The actual rendered line height of a font is approximately fontSize x 1.3 (ascent + descent in font metrics), not fontSize itself. Therefore:
  * Single-line text height = fontSize x max(lineHeight, 1.3)
  * X-line text height = fontSize x max(lineHeight, 1.3) x X
  * Example: fontSize=14, lineHeight=1.2 -> single-line height = 14 x 1.3 = 18.2px, not 14 x 1.2 = 16.8px.
- Text width calculation:
  * Chinese character width is approximately fontSize; English/digit width is approximately fontSize x 0.5~0.6
  * With letter spacing: total width is approximately fontSize x Y + letterSpacing x (Y - 1)
- Text box size calculation for required content
  * Use the above methods to calculate text width and line height, combined with paragraph spacing settings, to estimate the required text box dimensions (width and height)
  * Ensure text box dimensions match actual text content size: oversized content will cause text overflow; undersized content will cause page whitespace

#### Overall Page Layout Control
- Set body area content appropriately: After removing fixed page elements (title, footnotes, etc.), the body content area layout should also be evenly and reasonably distributed:
  * Avoid excessive content concentration: Avoid content height being far less than the page body area height (e.g., body area height 500px, content only 200px). Use font size, element spacing, number of decorative elements, etc. to ensure actual content height is close to the page body area height
  * Avoid top-heavy bottom-empty: When content is sparse and genuinely far less than the body area height, ensure the actual content area is centered within the body area with equal top and bottom whitespace. Content concentrated at the top with excessive bottom whitespace is strictly forbidden
- Maintain grid alignment: Ensure all elements are properly aligned
  * For left-right layouts, ensure left and right content grids are aligned with consistent heights: avoid one side extending to the bottom while the other only fills halfway
  * For top-bottom layouts, ensure content has equal left and right whitespace: avoid content concentrated on the left with large right-side whitespace

### step7: Check .pptd Files

1. Check
- After generating the .pptd files, you **must** use the built-in checker to verify the files, ensuring no format errors or unexpected overflow issues:
> Tip: Use relative paths. Make sure to cd to the pptx skill directory before running check.sh
```bash
scripts/check.sh filename.pptd
```
- The checker will check for the following issues, divided into Error and Warning categories:
  * Format check: Whether YAML syntax is valid, required fields are present, field values are valid, elementId is unique within pages, etc.
  * Data validation: Color format and reference validity, elements exceeding page boundaries, shapeName validity, chart/table data completeness
  * Layout detection: Text occlusion, text box misalignment with underlying containers
  * Text box content detection: Text width/height overflow, text underfill

2. Fix
- Fix all ERRORs first: These issues will cause conversion failures and must be fixed
- Then handle WARNINGs: **PPTD renders precisely and will not automatically scale text or adjust layout. Every WARNING reported by the checker means a corresponding visual issue (truncation, occlusion, overflow, etc.) will appear in the final PPTX and will not be auto-corrected.** Therefore, WARNINGs must be fixed by default unless you can clearly determine that the WARNING is part of the intended design (e.g., decorative elements intentionally extending beyond the canvas). If skipping a WARNING, you must explain the reason.
- **Fix in parallel**: **You must call the edit_file tool in parallel as much as possible in a single response**, fixing issues across multiple files at once rather than fixing files one by one sequentially.
  1. TextOverflowWarning (text overflow): The space required by text content exceeds the text box space, causing content truncation (must fix)
  2. TextOcclusionWarning (text occlusion): Text is occluded by other elements (images/shapes/text boxes, etc.), making text unreadable
  3. TextDriftWarning (text drift): The text box is pierced through by other elements, or is not fully aligned with underlying shapes, images, etc.
  4. TextUnderfillWarning (text underfill): The text box is too large or the font size is too small, resulting in large blank areas within the text box, often causing unexpected whitespace on the page
  5. BoundsOutsideWarning (out of bounds): The element is partially or fully outside the canvas dimensions, making it partially or fully invisible

3. Re-verification
- After fixing, **re-run the checker** and **review the complete output** (using grep/sed to filter is forbidden). Focus on the Summary at the bottom, checking the count of each issue type to confirm all ERRORs have been eliminated and all unexpected WARNINGs have been addressed. If residual issues remain, continue fixing and repeat verification until the Summary shows `0 errors, 0 warnings`. **Using grep to filter and only viewing/fixing partial issues is strictly forbidden!**

#### Fix Precautions
- Maintain margins: After adjusting element bounds, check whether reasonable spacing is still maintained between the element and page edges, adjacent elements, and bottom elements. Do not forget to leave appropriate margins when adjusting bounds to resolve text overflow or whitespace issues, causing text boxes to be pressed against edges and losing original margins. **Fixed bounds should maintain consistent margins with other elements of the same type on the page.**
- Do not move common element positions: Common elements on pages (such as navigation bars, titles, corner badges, etc.) should maintain consistent positions across pages. When layout issues exist, prioritize adjusting content layout to avoid subtle differences in common elements across pages (such as inconsistent heights, font sizes, etc.; intentionally designed special layouts are exceptions)
- Ensure content alignment: When adjusting element A, ensure related elements are adjusted in sync. Common situations include:
  * Adjusted text box size but did not sync the background color/card size beneath the text box
  * Adjusted element A's position but did not sync attached decorative elements (such as decoration bars, progress bars, etc.) in size and position, causing misalignment

#### Text Overflow Fix Strategy
When the checker reports TextOverflowWarning, fix in the order suggested by the checker:
- Height overflow:
  1. Condense text: Compress expressions, merge points, remove secondary content
  2. Reduce font size: Decrease content font size, line spacing, paragraph spacing, etc.
  3. Expand text box height: If the above approaches are not feasible and there is space below the text box, increase the bounds height to accommodate the content. But be careful not to introduce overlap or drift issues
- Width overflow:
  1. Condense text: Shorten text content, reducing the content volume to the percentage suggested by the checker
  2. Switch to multi-line: Set `wrap: true` to enable auto-wrapping, and adjust text box height and layout accordingly
> **It is forbidden to excessively reduce font size to eliminate overflow, causing large blank areas within the text box** -- this is more detrimental to aesthetics than slight overflow.

### step8: Deliver .pptd Files
- Inform the user that the presentation is complete, and provide a summary of the content highlights, core insights, specific structure, and other key information.
- Inform the user that they can click the card in the conversation to view and download the presentation in PPTX format

## Additional Notes

### Multi-Presentation Generation
When the user requests creating multiple presentations, **you must adopt a generate-all-first, then check-one-by-one strategy!** That is: serially complete the creation or modification of each PPT (including .page files and .pptd files), and only proceed to unified checking, fixing, and delivery after all presentations are created. **Never complete one PPT and immediately check, fix, and deliver it before creating the next PPT**.

### Parallel Writing
**You must call the write_file tool in parallel as much as possible in a single response.** Specifically:
- After generating the .pptd main file, write as many .page files as possible in parallel in the same response
- Each .page file is an independent write_file call with no dependencies, and should all be issued in the same response
