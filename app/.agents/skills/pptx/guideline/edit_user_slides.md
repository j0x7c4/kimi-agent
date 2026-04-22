# Edit User-Uploaded Presentations

Read this guide when a user uploads a PPTX file and requests **modifications** to its content, style, or structure.

> **Note**: If the user uploads a PPT to use as a template/reference for creating a new presentation (e.g., "use this PPT as a template to make a new one", "create a PPT about xxx in this style"), follow the generation workflow in generate_slides.md (template mode) instead of this guide.

---

### step1: Understand User Requirements

Clarify what the user wants to modify:
- **Content modification**: Change text, update data, add/remove pages
- **Style modification**: Change color scheme, fonts, layout
- **Structure modification**: Adjust page order, merge/split pages
- **Mixed modification**: Combination of the above

### step2: Review PPTX Content as Needed

Choose the most cost-effective reading approach based on the scope of modifications, avoiding unnecessary context consumption:

1. First use `read_file` to quickly understand the content structure, locate the pages and positions of text to be modified, then use `scripts/screenshot.sh` to view the visual appearance of the corresponding pages to ensure reasonable visual results during the modification process
2. For batch modifications of certain elements (e.g., batch replace logos, batch adjust font sizes), first use `scripts/screenshot.sh` to view screenshots and find these elements, then use `scripts/convert.sh` to convert to PPTD format, read the corresponding pages to identify common properties of the elements (e.g., they all reference the same image src, they all use the same text style), facilitating subsequent batch replacement using Grep and similar commands.
3. For full-presentation layout beautification, first use `scripts/screenshot.sh` to view screenshots, determine which pages have poor layout and which have good layout, then restructure the poorly laid-out pages to align with the visual quality of the other pages

### step3: Convert to PPTD

```bash
scripts/convert.sh input.pptx -o output_dir/
```

After conversion, the following will be generated in `output_dir/`:
- `*.pptd` main entry file (contains size, theme, and page path list)
- `pages/*.page` page files (one `.page` file per page)
- `images/` directory (extracted image resources)
- `fonts/` directory (extracted embedded fonts)

### step4: Locate Target Content

#### Location Strategies

1. Locate by page
Read the main entry file to understand page order: `output_dir/*.pptd`
List all page files: `Glob: pattern="output_dir/pages/*.page`

2. Locate by element ID: Search within pages: `Grep: pattern="elementId: title_1" path=output_dir/pages/`

3. Locate by text content: Search for the text to modify in the pages directory: `Grep: pattern="market size" path=output_dir/pages/`

4. Locate by element type: `Grep: pattern="elementType: chart" path=output_dir/pages/`

5. Locate by style: Search for color, font size, and other style properties: `Grep: pattern="#FF5733" path=output_dir/pages/`

#### Detailed Reading After Location

Once the target page is found, simply read the `.page` file to get the complete page structure.

### step5: Modify PPTD Using edit_file

Use the `edit_file` tool to make precise modifications to PPTD files. **You must call the edit_file tool in parallel as much as possible in a single response**, modifying multiple files at once rather than modifying files one by one sequentially.

#### Multi-Presentation
When the user requests editing multiple presentations simultaneously, **you must adopt a modify-all-first, then check-one-by-one strategy!** That is: serially complete the modification of each PPT (step1~step5), and only proceed to unified checking, fixing, and delivery after all presentations are modified. **Never complete one PPT's modification and immediately check, fix, and deliver it before modifying the next PPT**.

#### Modify Page Content
To modify page text, elements, element properties, etc., simply find the corresponding location and edit directly

#### Modify Theme
The main entry file contains the theme definition. First determine whether the desired change can be achieved quickly by modifying the theme definition

#### Add/Remove Pages
- **Remove pages**: Remove the corresponding `.page` file from the `pages` list in the main `.pptd` entry, and delete the file
- **Add pages**: Add the relative path of the new page to the `pages` list in the main `.pptd` entry, and create the new `.page` file in the `pages/` directory
- **Reorder pages**: Modify the path order in the `pages` list of the main `.pptd` entry

### step6: Check the Modified PPTD

After modifications are complete, run the checker to ensure no new issues were introduced:

```bash
scripts/check.sh output.pptd
```

- Fix all ERRORs first (format errors, invalid references, etc. -- unfixed errors will cause conversion failure)
- Then handle WARNINGs: **PPTD renders precisely and will not automatically scale text or adjust layout. Every WARNING reported by the checker means a corresponding visual issue (truncation, occlusion, overflow, etc.) will appear in the final PPTX and will not be auto-corrected.** Therefore, WARNINGs must be fixed by default unless you can clearly determine that the WARNING is part of the intended design (e.g., decorative elements intentionally extending beyond the canvas). If skipping a WARNING, you must explain the reason.
  1. TextOverflowWarning (text overflow): The space required by text content exceeds the text box space, causing content truncation (must fix unless it existed in the user's original PPTX)
  2. TextOcclusionWarning (text occlusion): Text is occluded by other elements, making text unreadable
  3. TextDriftWarning (text drift): Text box is not fully aligned with underlying elements
  4. TextUnderfillWarning (text underfill): Text box too large or font size too small, causing large blank areas
  5. BoundsOutsideWarning (out of bounds): Element partially or fully outside the canvas
- **Fix in parallel**: **You must call the edit_file tool in parallel as much as possible in a single response**, fixing issues across multiple files at once rather than fixing files one by one sequentially.
- Repeat checking until all ERRORs are eliminated and all unexpected WARNINGs are handled

### step7: Deliver

- Inform the user that the modifications are complete, and provide a summary of the changes made
- Inform the user that they can click the card in the conversation to view and download the presentation in PPTX format
