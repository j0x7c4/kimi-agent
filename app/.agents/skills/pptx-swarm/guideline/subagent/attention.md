# Attention

## YAML Quoting Rules (Must Follow)
- The `content.text` field **must use block scalar (`|`)**. Do not wrap it with `"` or `'`, otherwise double quotes inside HTML attributes (e.g., `style="..."`) will cause YAML parsing errors.
- For other fields, if the value contains special characters such as `:`, `#`, `{`, `}`, wrap it in quotes or use block scalar.

## Basic Guidelines
1. Scope of operations: You are strictly prohibited from directly manipulating pptx files. All your operations should target pptd files, and you are also prohibited from converting pptd files to pptx files. The pptx files users need should be obtained by the users themselves on the frontend by clicking the "Export" button to convert pptd to pptx.
2. Parallel tool calls: If you need to make multiple consecutive tool calls (e.g., generating multiple .page files in succession; using the edit tool multiple times to modify different parts of the same file), you should make parallel tool calls in a single output, rather than making separate thinking-toolcall, thinking-toolcall rounds. This avoids context redundancy caused by multiple output rounds.


## Text Box Size Estimation
- Text box wrapping control: When generating pptd, you **must** explicitly set `wrap: false` for every text box intended to display on a single line: title text boxes, labels/badges, data numbers, navigation elements, etc.
- Line height calculation: The actual rendered line height of a font is approximately fontSize x 1.3 (ascent + descent from font metrics), not fontSize itself. Therefore:
  * Single-line text height = fontSize x max(lineHeight, 1.3)
  * X-line text height = fontSize x max(lineHeight, 1.3) x X
  * Example: fontSize=14, lineHeight=1.2 -> single-line height = 14 x 1.3 = 18.2px, not 14 x 1.2 = 16.8px.
- Text width calculation:
  * Chinese character width ≈ fontSize; English/digit width ≈ fontSize x 0.5~0.6
  * With letter spacing: total width ≈ fontSize x Y + letterSpacing x (Y - 1)
- Text box size calculation for required content
  * Use the above methods to calculate text width and line height, combined with paragraph spacing settings, to estimate the required text box dimensions (width and height)
  * Ensure text box dimensions match actual text content size: oversized content will cause text overflow; undersized content will cause page whitespace

## Overall Page Layout Control
- Set body area content appropriately: After removing fixed page elements (title, footnotes, etc.), the body content area layout should also be evenly and reasonably distributed:
  * Avoid excessive content concentration: Avoid content height being far less than the page body area height (e.g., body area height 500px, content only 200px). Use font size, element spacing, number of decorative elements, etc. to ensure actual content height is close to the page body area height
  * Avoid top-heavy bottom-empty: When content is sparse and genuinely far less than the body area height, ensure the actual content area is centered within the body area with equal top and bottom whitespace. Content concentrated at the top with excessive bottom whitespace is strictly forbidden
- Maintain grid alignment: Ensure all elements are properly aligned
  * For left-right layouts, ensure left and right content grids are aligned with consistent heights: avoid one side extending to the bottom while the other only fills halfway
  * For top-bottom layouts, ensure content has equal left and right whitespace: avoid content concentrated on the left with large right-side whitespace

## Check the .pptd File After Completion

1. Check
- After completing the corresponding .page files, you **must** use the built-in checker to verify the files, ensuring there are no format errors or unexpected overflow issues.
- **You must use the `--pages` parameter to only check the pages you are responsible for.** The page paths should match the references in the `pages` list of the .pptd file:

```bash
# Example: only check the 3 pages you are responsible for
{skill_path}/scripts/check.sh filename.pptd --pages pages/slide_02.page,pages/slide_03.page,pages/slide_04.page
```

- The checker will check for the following issues, divided into Error and Warning categories:
  * Format check: Whether YAML syntax is valid, required fields are present, field values are valid, elementId is unique within pages, etc.
  * Data validation: Color format and reference validity, elements exceeding page boundaries, shapeName validity, chart/table data completeness
  * Layout detection: Text being occluded, text boxes not aligned with underlying containers
  * Text box content detection: Text width/height overflow, text underfill

2. Fix
Refer to the following approaches to fix issues found in the pages you created. **No need to address issues on other pages.**
- Fix all ERRORs first: These issues will cause conversion failure and must be fixed.
- Then handle WARNINGs: **PPTD renders precisely and will not automatically scale text or adjust layout. Every WARNING reported by the checker means a corresponding visual issue (truncation, occlusion, overflow, etc.) will appear in the final PPTX and will not be auto-corrected.** Therefore, WARNINGs must be fixed by default, unless you can clearly determine that a WARNING is part of the intended design (e.g., decorative elements intentionally extending beyond the canvas). If you skip a WARNING, you must explain the reason.
- **Parallel fixing**: **Must call the edit_file tool in parallel as many times as possible in a single response**, fixing issues across multiple files at once, rather than fixing files one by one sequentially.
  1. TextOverflowWarning (text overflow): Text content requires more space than the text box provides, causing content truncation (must fix)
  2. TextOcclusionWarning (text occlusion): Text is occluded by other elements (images/shapes/text boxes, etc.), making text unreadable
  3. TextDriftWarning (text drift): The text box is crossed through by another element, or not fully aligned with underlying shapes, images, etc.
  4. TextUnderfillWarning (text underfill): Text box is too large or font size is too small, resulting in large blank areas within the text box, which often causes unexpected whitespace on the page
  5. BoundsOutsideWarning (out of bounds): Element is partially or fully outside the canvas dimensions, making it partially or fully invisible

3. Re-verification
- After fixing, **re-run the checker** (also using the `--pages` parameter to only check the pages you are responsible for) and **review the complete output** (do not use grep/sed or other filters). Focus on the issue type counts in the Summary at the bottom to confirm all ERRORs have been eliminated and all unexpected WARNINGs have been addressed. If there are remaining issues, continue fixing and repeat verification until the Summary shows `0 errors, 0 warnings`. **Do not use grep to filter and only view/fix partial issues!**

### Fix Precautions
- Maintain margins: After adjusting element bounds, check whether reasonable spacing is still maintained between the element and page edges, adjacent elements, and bottom elements. Do not forget to leave appropriate margins when adjusting bounds to resolve text overflow or whitespace issues, causing text boxes to be pressed against edges and losing original margins. **Fixed bounds should maintain consistent margins with other elements of the same type on the page.**
- Do not move common element positions: Common elements on pages (such as navigation bars, titles, corner badges, etc.) should maintain consistent positions across pages. When layout issues exist, prioritize adjusting content layout to avoid subtle differences in common elements across pages (such as inconsistent heights, font sizes, etc.; intentionally designed special layouts are exceptions)
- Ensure content alignment: When adjusting element A, ensure related elements are adjusted in sync. Common situations include:
  * Adjusted text box size but did not sync the background color/card size beneath the text box
  * Adjusted element A's position but did not sync attached decorative elements (such as decoration bars, progress bars, etc.) in size and position, causing misalignment

### Text Overflow Fix Strategy
When the checker reports TextOverflowWarning, fix in the order suggested by the checker:
- Height overflow:
  1. Condense text: Compress wording, merge key points, remove secondary content
  2. Reduce font size: Reduce content font size, line spacing, paragraph spacing, etc.
  3. Expand text box height: If the above approaches are not feasible and there is space below the text box, increase the bounds height to accommodate the content. But be careful not to introduce overlap or drift issues
- Width overflow:
  1. Condense text: Shorten text content, reduce the content amount to the percentage suggested by the checker
  2. Switch to multi-line: Set `wrap: true` to enable auto-wrapping, and adjust the text box height and layout accordingly
> **Do not excessively reduce font size to eliminate overflow, causing large blank areas within the text box** -- this is worse for aesthetics than slight overflow.


## Deliver the Presentation
- After completion, inform the main agent which pages you have completed and where they are located, so the main agent can continue execution.

</output>
