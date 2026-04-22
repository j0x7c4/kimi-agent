# Replication/Reference Mode Workflow

When the user uploads images or websites requesting replication or reference, analyze the reference source and **use the write_file tool** to build a detailed design.md document.

## workflow

### step1. Determine Replication/Reference Scope
Based on user requirements, determine the scope of replication/reference: Style? Color scheme? Layout? Content?
- If the user does not explicitly specify a scope, default to referencing **style + color scheme + layout** (excluding content)
- If the user explicitly requests "replicate" or "1:1 reproduction", enter full replication mode covering style + color scheme + layout + content

### step2. Profile Recommendation

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

- Compare the reference image's characteristics with the scenario profiles and output the final content expression strategy in design.md
- If the reference image's expression strategy does not match the user's actual scenario (e.g., the reference source has a low-density brand style but the user needs a consulting report), follow the reference source

### step3. Analyze Reference Source

Based on the scope determined in step1, systematically extract style information from the reference source:

- **Style anchor identification**: Determine whether the reference source belongs to a recognizable style school or brand system (e.g., McKinsey/BCG consulting style, Apple/Muji brand style, Bauhaus/Swiss International Style, etc.)
- **Color extraction**: Identify primary color, secondary color, accent color, background color, text color
- **Container and decoration analysis**: Card structures, separation methods, decorative elements
- **Font hierarchy analysis**: Font, size, and special treatments for titles/body/auxiliary text
- **Image style analysis**: Visual style of icons, charts, tables, and illustrations
- **Layout pattern summarization**: Global characteristics, special pages, content page layout patterns

Based on the analysis results, output the complete design document following the "design.md Output Structure" below.

---

## design.md Output Structure

design.md must include the following sections, output in order:

### 1. Profile Baseline Declaration

- **Profile selection**: Specify which scenario profile file serves as the baseline for this design (e.g., `profiles/business_insight.md`, `profiles/general.md`, etc.)
- **Selection rationale**: Briefly explain why this profile was chosen (scenario match, audience characteristics, etc.)
- **Referenced dimensions**: Describe which dimensions were referenced from this profile — design philosophy, information density, color guidance, font guidance, layout patterns, content expression techniques, decoration prohibitions, etc.
- **Deviation notes**: If this design needs to deviate from certain profile guidance (e.g., user has explicit requirements, or reference source style is inconsistent with the profile), list each deviation point and reason here

### 2. Style Baseline Declaration

- **Style anchor identification**: Identify whether the reference source belongs to a recognizable style school or brand system
  - E.g.: McKinsey/BCG consulting style, Apple/Muji brand style, The Economist/Monocle publication style, Bauhaus/Swiss International Style, etc.
  - If a clear style anchor can be identified, note it as a baseline reference for subsequent generation
- **Referenced dimension explanation**: Beyond the style anchor, more importantly, explain what aspect of this style to reference — language style, color scheme, page layout, or information density?
  - If the reference source's characteristics cannot be fully attributed to a single anchor, multiple anchors may be selected with explanations of what to emulate or learn from each
- **Reference scope declaration**: Specify the dimensions being referenced (style/color scheme/layout/content)

### 3. Extract Style from Reference Source

Based on the reference scope determined in step1, systematically extract style information across the following dimensions from the reference source:

1. **Typographic character**: The overall visual impression
   - E.g.: Minimal and restrained / Information-dense / Lively and dynamic / Premium business / Academic rigor, etc.

2. **Color Extraction**
   - Identify core colors from the reference source and map to theme.colors color roles:
     * **primary** (required): The most recognizable dominant color in the reference source, used for titles, navigation, key visual anchors
     * **secondary** (required): Supporting color, used for secondary information and differentiation
     * **accent** (optional): Emphasis color, used for key data, CTAs, and highlights. May be omitted if the reference source has an overall restrained style (e.g., consulting style, academic style)
     * **background** (required): Page background color
     * **text** (required): Body text color
   - Brand colors first: If the reference source involves a specific brand (e.g., Starbucks/Tsinghua University), prioritize extracting its brand colors
   - Keep core colors to 3-4 (primary + secondary + optional accent + grayscale), pursuing visual consistency with the reference source
   - Explain how each color is used across different scenarios (e.g.: titles use $primary, body text uses $text, decorative lines use $accent, etc.)

3. **Font Hierarchy Extraction**
   - Identify font styles (serif/sans-serif/handwritten, etc.) for each level — titles/subtitles/body/annotations — from the reference source
   - Font size relationships and contrast intensity across levels
   - Whether there are special font treatments (e.g., all caps, wide letter spacing, special font weights, etc.)
   - Read `format/fonts.md` for the available font list and select font combinations closest to the reference source style
   - When the user query is in Chinese or requires a Chinese PPT delivery, both Chinese and English fonts need to be specified; otherwise, only English fonts need to be set
   - **Body font size should be controlled at 18-22px (use 22px when page text content is minimal, 20px for moderate, 18px for heavy; must not go below 18px) to ensure presentation readability**

4. **Text Box and Container Styles**
   - Does the reference source use card structures? Are cards rounded or sharp-cornered? What is the corner radius?
   - Content separation methods: Card separation, line separation, whitespace separation, color block separation?
   - Are there decorative elements (textures, color bands, angled shapes, etc.)?

5. **Image Style**: Extract the overall style of illustrations, icons, charts, tables, and other visual elements from the reference source
   - Icons: Outline icons or solid icons? Color strategy (monochrome/theme color/multicolor)? Are there containers (circular/square backgrounds)?
   - Tables: Table visual style preference (minimal/complex/flat/skeuomorphic/monochrome/multicolor), table styling (three-line table/special header row style/special first column style/alternating colors/font choices, etc.)
   - Charts: Chart style preference (minimal/full/flat/skeuomorphic/monochrome/multicolor), series colors (same color family or different for different series? What colors to use?), whether colors follow the theme
   - Illustrations: Illustrations should pursue the visual impact and aesthetic quality of movie posters or magazine covers; extract the reference source's illustration color palette (vibrant or restrained), style (illustration, realistic, skeuomorphic, abstract, etc.), processing method (original/mask overlay/cropped to specific shapes/desaturated, etc.)

### 4. Layout System

Extract **common characteristics and design patterns** of page layouts from the reference source, rather than specific values or fixed content quantities.

1. **Global Layout Characteristics**
   - Page margins: Extract the reference source's margin style to ensure breathing room
   - Unified page elements: Identify whether the reference source has consistent elements such as logos, decorative elements (shapes, lines), text box elements (such as fixed title areas, page numbers/data source annotations), and whether there are fixed navigation bars/sidebars/top tab bars for page navigation

2. **Special Page Layouts** (cover, table of contents, chapter divider, closing page)
   - Cover and closing pages: Identify whether Hero design is used (full-size background image + gradient mask, combined with large text, using asymmetric layout/centered layout/diagonal cuts/tilted elements/special text effects)
   - Other pages: Extract layout patterns suitable for the page type

3. **Content Page Layout Patterns**
   - Summarize content page layout patterns from the reference source: single column, two columns, left-right split, top-bottom sections, wrap-around, etc.
   - Identify advanced layout styles in the reference source:
     * Multi-layer overlapping of image + mask + text for visual impact
     * Z/F-pattern reading flow
     * Magazine-style layouts
     * Diagonal separators instead of straight horizontal/vertical lines, asymmetric distribution, overlapping shapes, etc.
   - Identify special content pages:
     * Full-page image + gradient mask + brief content as transition pages
     * Pages dominated by a full-page SmartArt: such as Gantt charts, pyramid diagrams, etc.
     * Full-page tables, full-page charts
   - **Moderate expansion allowed**: For visual variety in the final presentation, additional layout patterns may be added beyond the reference layouts (note in design.md: "expanded xxx layout beyond the reference to enrich visual variety")

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
- Decoration prohibitions from the scenario profile (e.g., decorative elements unsuitable for this scenario, such as prohibiting rounded rectangles)
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

### 8. Content Replication (Full Replication Mode Only)

Output this section only in full replication mode (when the user explicitly requests "replicate" / "1:1 reproduction"):

1. **Replication requirement declaration**: Explicitly declare that content needs to be fully replicated 1:1, ensuring every page's text, data, charts, and other content is identical to the reference source

2. **Page inventory**: List the total number of pages to replicate and each page's type (cover/table_of_contents/chapter/content/final)

3. **No need for verbatim transcription**: The reference images uploaded by the user are already in context; design.md only needs to note "Page N: 1:1 replicate the content from the reference image" without repeating all the text

4. **Position information may be described**: For pages with complex layouts, key elements' approximate positional relationships can be briefly noted to assist subsequent generation

---

### NEXT STEP
1. **Use the write_file tool** to generate the complete design.md document
2. Based on user requirements, determine which content design mode to enter (summary mode, outline mode, or search mode?) and read the relevant guideline document
