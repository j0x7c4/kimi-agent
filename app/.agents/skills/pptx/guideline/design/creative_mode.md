# Creative Mode Workflow

When there is no visual reference available, autonomously complete the visual design based on user requirements and audience analysis, and **use the write_file tool** to build a detailed design.md document.

## workflow

Based on the user requirements and audience analysis completed in generate_slides.md step2, proceed with visual design.

### step1. Profile Recommendation

Several style profiles are available in the `guideline/design/profiles/` directory for your reference. You can select and read the most matching profile file. **All dimensions below are default guidance based on the reference source; the user's explicit requirements always take priority.**

| File | Applicable Scenarios |
|---|---|
| `guideline/design/profiles/business_insight.md` | Brokerage research reports, industry research, market surveys, competitive analysis, strategic consulting |
| `guideline/design/profiles/academic.md` | Thesis defense, group meeting presentations, research project reports |
| `guideline/design/profiles/promotion.md` | Brand launches, marketing campaigns, arts/fashion/culture showcases |
| `guideline/design/profiles/education.md` | Primary/secondary/higher education courseware, student classroom presentations, corporate training, educational lectures |
| `guideline/design/profiles/work_report.md` | Performance reviews, work summaries, state-owned enterprise reports |
| `guideline/design/profiles/strategic.md` | Project proposals, business plans, fundraising pitches, strategic planning reports |
| `guideline/design/profiles/general.md` | Use when the user's needs do not match any of the above scenarios |

- If the user's scenario clearly matches a profile, read the corresponding file directly and follow its guidance
- If the user's scenario falls between multiple profiles, choose the closest one as the baseline and explain adjustments in design.md
- If the user's scenario does not match any profile, use `guideline/design/profiles/general.md` as the baseline and explain the reasoning for adjustments in design.md
- Note: Only profiles under the profiles directory may be read; using templates under the template directory to create PPTs is strictly prohibited!

### step2. Design

#### Overall Design Principles

1. **Break free from defaults**: Avoid instinctive choices; think about what truly suits this PPT
2. **Consider brand identity**: If the user mentions a company/organization/brand, consider using its brand colors and a style that matches the company's characteristics (you can search to explore the corresponding company's style)
3. **Multi-dimensional synthesis**: Topic, industry, atmosphere, energy level, target audience, brand identity
4. **Adventurous spirit**: Always strive to find those "unexpected yet perfectly fitting" combinations that avoid cliches — medical presentations don't have to be green, finance doesn't have to be navy style
5. **Readability first**: Regardless of style, ensuring content readability is a prerequisite

Based on the above principles, conduct systematic design thinking across three dimensions — style, color scheme, and layout — and output the complete design document following the "design.md Output Structure" below.

---

## design.md Output Structure

design.md must include the following sections, output in order:

### 1. Profile Baseline Declaration

- **Profile selection**: Specify which scenario profile file serves as the baseline for this design (e.g., `profiles/business_insight.md`, `profiles/general.md`, etc.)
- **Selection rationale**: Briefly explain why this profile was chosen (scenario match, audience characteristics, etc.)
- **Referenced dimensions**: Describe which dimensions were referenced from this profile — design philosophy, information density, color guidance, font guidance, layout patterns, content expression techniques, decoration prohibitions, etc.
- **Deviation notes**: If this design needs to deviate from certain profile guidance (e.g., user has explicit requirements), list each deviation point and reason here

### 2. Style Baseline Declaration

- **Style anchor selection**: Reference the scenario/industry and autonomously select a visual anchor as the style foundation
  - Publications: Monocle, Kinfolk, and other publications with top-tier visual effects
  - Brands: Apple, Muji, Aesop, and other brands with distinctive design styles and refined taste
  - Designers: Works of top designers such as Massimo Vignelli, Paul Rand, etc.
  - Design movements: Swiss International Style, Neo-Brutalism, Bauhaus, 8-bit, Cyberpunk, Memphis, etc.
- Do not reference styles whose color schemes are difficult to understand or translate: e.g., Duolingo (the bold red-green color scheme is hard to achieve aesthetically in presentations), Bloomberg (the overall style is rigorous and simple, suitable for extremely restrained professional scenarios, but not for other scenarios requiring visual impact)
- **Referenced dimension explanation**: Beyond selecting an anchor, more importantly, explain what aspect of this style to reference — language style, color scheme, page layout, or information density?
- Do not force-fit: If a query does not fully match all characteristics of a single anchor, you may select multiple anchors and separately describe what to emulate or learn from each.

### 3. Style Details

1. **Color Design Principles**
   - Brand colors first: If a specific brand is involved (e.g., Starbucks/Tsinghua University), prioritize using its brand colors
   - Extract color cues from content: Industry characteristics, emotional core, brand elements; pursue combinations that are “unexpected yet visually harmonious and impactful”
   - **Avoid AI-typical color schemes**: Such as purple, gradient white-purple, blue, cliche combinations like red/green/yellow/orange, or using red/green/yellow to represent error/correct/warning
   - **Color Design Logic**
     (1) First determine the overall color tendency — conservative & steady vs. striking & bold:
       - Based on user requirements, scenario, and audience, set the color temperament for the entire presentation:
         * Conservative & steady: Suitable for corporate reports, consulting reports, academic defenses, government scenarios — primarily neutral colors with restrained colorful accents, pursuing credibility and professionalism, avoiding visual risks
         * Striking & bold: Suitable for brand launches, creative proposals, portfolios, marketing presentations — allows bolder color contrasts, more vivid primary colors, stronger visual memorability, while still maintaining harmony
         * In between: Landing in the middle ground — stability as the foundation, with local highlights (e.g., strong colors for cover/chapter pages, restrained colors for content pages)
       - This judgment directly affects the decision-making scale of all subsequent steps: conservative tendency prioritizes low saturation, small color differences; striking tendency allows more stylized colors
     (2) Then set the temperature:
       - Determine whether the overall feel should lean cool, warm, neutral, natural, papery, or mineral
       - Temperature judgment takes priority over abstract style words like “premium feel” or “tech feel”
     (3) Decide the primary color first:
       - Prioritize the brand/organization's theme color (e.g., Starbucks → green, Tsinghua University → purple); if no brand/organization is involved, choose colors that match the color tendency, temperature, and presentation scenario
       - Blue/cyan always has low priority. If the initial primary color is blue/cyan, first consider: is blue/cyan truly the optimal choice? Unless the user requests it or it is the most suitable color for the topic (e.g., the brand's theme color is blue/cyan), blue/cyan should not be used as the primary color. If blue/cyan must be used, choose the most sophisticated related hues (blue-gray, etc.); strictly prohibit cheap blue-cyan colors like dark turquoise #0A97C0, dodger blue #2C80FD, and similar
     (4) Then decide background, body text, and secondary colors:
       - Decide page background, text colors (may need both dark and light text colors), and secondary colors (for dividers, subtle decorations, secondary information, etc.)
       - White always has low priority. White backgrounds are minimal but sometimes too plain. Unless the user requests it, or white is necessary to create a pure, clean atmosphere (where no other color is suitable), white should not be used
     (5) Finally decide the accent color:
       - Used for key data, CTAs, and highlights, echoing the primary color
       - Always maintain a conservative strategy for accent colors: when the accent color cannot provide significant benefits, prefer not using one (accent = null)
       - The accent color should also belong to the same color family as the primary color; contrast must not be too strong
       - Even when an accent color is set, it should be used conservatively and with restraint

2. **Font Usage Principles**
   - Read `format/fonts.md` for the available font list and select font combinations that match the style positioning
   - When the user query is in Chinese or requires a Chinese PPT delivery, both Chinese and English fonts need to be specified; otherwise, only English fonts need to be set
   - **Increase the font size gap between titles and body text; the size contrast between levels should be significant. Content that needs emphasis (such as numbers, KPIs) should use large font sizes**
   - Body text should prioritize highly readable fonts; **for titles or special pages, using distinctive fonts with special treatments (all caps, wide letter spacing, bold, italic, etc.) is encouraged to create refined visual styles**
   - **Body font size should be controlled at 18-22px (use 22px when page text content is minimal, 20px for moderate, 18px for heavy; must not go below 18px) to ensure presentation readability**
   - Font size hierarchy settings for each level of headings, body text, and auxiliary text

4. **Text Box and Container Styles**
   - Content separation methods: Prioritize whitespace and font size differences for hierarchy; avoid over-reliance on structural cards (rectangles/rounded rectangles)
   - If cards are not used, specify details such as rounded/sharp corners, border/no border, filled/unfilled (sharp corners preferred)
   - Decorative element usage strategy (textures, color bands, angled shapes, geometric decorations, etc.)

5. **Image Style**: Overall style of illustrations, icons, charts, tables, and other visual elements
   - Icons: Use outline icons or solid icons? What is the usage strategy? In what scenarios should icons be used? Is icon usage encouraged or restrained?
   - Tables: Table visual style preference (minimal/complex/flat/skeuomorphic/monochrome/multicolor), table styling (three-line table/special header row style/special first column style/alternating colors/font choices, etc.)
   - Charts: Chart style preference (minimal/full/flat/skeuomorphic/monochrome/multicolor), series colors (same color family or different for different series? What colors to use?)
   - Illustrations: First, illustrations should pursue the visual impact and aesthetic quality of movie posters or magazine covers; on this basis, consider the color palette of illustrations (vibrant or restrained, what colors, etc.), style (illustration, realistic, skeuomorphic, abstract, etc.) and other specific design factors

### 4. Layout System

Describe **layout patterns** rather than fixed values.

1. **Global Layout Characteristics**
   - Page margins: Define page margins to ensure breathing room
   - Unified page elements: Whether pages need consistent elements such as logos, decorative elements (shapes, lines), text box elements (such as fixed title areas, page numbers/data source annotations), and whether fixed navigation bars/sidebars/top tab bars are needed for page navigation
   - **Ensure all pages use grid layout with perfectly aligned elements; avoid layouts with offset alignment or inconsistent left-right heights that affect visual quality**

2. **Special Page Layouts** (cover, table of contents, chapter divider, closing page)
   - Cover and closing pages: Build "first-glance wow" with top-tier visual impact; consider the following approaches:
     * Approach 1 (Hero design): Full-size background image + gradient mask, combined with centered stylized large text
     * Approach 2 (Magazine editorial style): Use irregular-proportion image-text cuts combined with image gradient masks
     * Approach 3 (Frame and break): Images are not full-bleed but constrained within geometric containers such as circles, arches, or specific-ratio rectangles
     * Others: Use asymmetric layout/centered layout/diagonal cuts/tilted elements/special text effects to create distinctive effects
   - Table of contents page: Reject the plain "bullet point list"; treat it as an information showcase; consider the following approaches:
     * Approach 1 (Grid layout): Transform chapters into equal-width grids using grid layout
     * Approach 2 (Timeline/path): Use a line — zigzag, curve, straight, or staircase layout — running through the page to connect chapters, creating a sense of reading flow
     * Approach 3 (Asymmetric two-column): One side features a large "CONTENTS" heading or thematic image, the other side uses dotted leaders or grid typography for chapter names
     * Prohibited: Uneven content distribution, such as left side full and right side empty
   - Chapter transition pages: A "rest note" and "restart key" for attention
     * Use colors harmonious with but distinct from content pages + theme color/semi-transparent chapter numbers to reset visual fatigue
     * Adopt Hero design or magazine editorial style similar to the cover, combining images and text for visual impact
     * Prohibited: Bare-bones layouts with only chapter number and chapter title

3. **Content Page Layout Patterns**
   - Design multiple layout patterns to ensure visual variety: single column, two columns, left-right split, top-bottom sections, wrap-around, etc.
   - Encourage use of various advanced layout styles:
     * Multi-layer overlapping of image + mask + text for visual impact
     * Z/F-pattern reading flow
     * Magazine-style layouts
     * Diagonal separators instead of straight horizontal/vertical lines, asymmetric distribution, overlapping shapes, etc.
   - Special content pages may be designed:
     * Full-page image + gradient mask + brief content as transition pages (may only be suitable for certain low-density scenarios)
     * Pages dominated by a full-page SmartArt: such as Gantt charts, pyramid diagrams, etc.
     * Full-page tables, full-page charts
   - Prohibited:
     * In left-right layouts, misaligned bottom edges: e.g., left content reaches the bottom of the page while the right side occupies only half
     * In top-bottom layouts, horizontally arranged text/shapes/flowcharts not centered: e.g., text boxes on the left with blank space on the right; a left-to-right flowchart occupying only 2/3 of the content width with 1/3 empty on the right

- Strictly prohibit numerical overfitting: Do not specify "the table of contents page has N chapters" or "content pages have N points" and other specific quantities; layout descriptions should be flexible to accommodate varying content volumes

### 5. Style Usage Rules

Describe how each Theme style should be used across different scenarios, including:
- Which element types and page scenarios each textStyle applies to
- How each color is allocated across text, backgrounds, decorations, etc.
- Usage scenarios for tableStyle

### 6. Risk Prohibitions

Based on this PPT's scenario, style, and layout characteristics, extract **the prohibitions most likely to be violated this time** from the above design specifications and scenario profiles, listed as a checklist to serve as warnings during subsequent generation. For example:
- Color prohibitions (e.g., which cliche color schemes this scenario tends to fall into)
- Layout prohibitions (e.g., alignment/whitespace issues common in this layout style)
- Decoration prohibitions from the scenario profile (e.g., decorative elements unsuitable for this scenario)
- Content expression prohibitions (e.g., expression styles unsuitable for this audience)

- Font size prohibitions: **Explicitly list font size constraints for each element type**, such as minimum body font size, minimum title font size, minimum auxiliary text/annotation font size, minimum table/chart label font size, etc., to prevent excessively small font sizes during generation that affect readability

Only list prohibitions that are **genuinely relevant** to this PPT; do not generically list all universal prohibitions.

### 7. Theme Definition

Based on all the above design decisions (color scheme, fonts, font size hierarchy, table styles, etc.), output the complete pptd theme YAML definition:

```yaml
theme:
  colors:
    primary: "#1e40af"
    secondary: "#64748b"
    accent: "#f59e0b"
    background: "#ffffff"
    text: "#1f2937"
  textStyles:
    title:
      fontSize: 48
      color: "$primary"
      fontFamily: "MiSans"
    subtitle:
      fontSize: 24
      color: "#6b7280"
      fontFamily: "MiSans"
    body:
      fontSize: 18
      color: "$text"
      lineHeight: 1.6
  tableStyles:
    default:
      headerFill: "$primary"
      headerColor: "#ffffff"
      headerBold: true
      bodyFill: ["#ffffff", "#f8f9fa"]
      bodyColor: "$text"
      firstColumnBold: true
      border:
        style: solid
        width: 1
        color: "#e0e0e0"
```

---

### NEXT STEP
1. **Use the write_file tool** to generate the complete design.md document
2. Based on user requirements, determine which content design mode to enter (summary mode, outline mode, or search mode?) and read the relevant guideline document
