# Academic Report / Thesis Defense

> Applicable scenarios: Thesis defense, research group meetings, academic conference presentations, research project reports, project progress reports, etc.
> Style anchor: Nature/Science paper figure style + academic conference presentation standards

## Design Philosophy

- **Content is king**: Visuals serve academic content; all design decisions prioritize clearly communicating research findings, avoiding any over-decoration
- **Rigorous and standardized**: Follow academic expression norms with complete figure annotations and traceable data sources. **Hallucinations are strictly prohibited — ensure all content has authentic, complete citations!**
- **Logically clear**: The research logic chain should be immediately apparent — Problem → Method → Results → Conclusion, with each page serving a clear argumentation node
- **Plain and professional**: Do not pursue visual flashiness; pursue professionalism and credibility. The persuasiveness of an academic report comes from data and logic, not visual effects
- **Information-rich**: Academic report pages must not be empty; they should have sufficient research content and data support, with each page carrying substantive academic information
- **Faithful to the source**: Prioritize reusing original figures, data, and expressions from the paper/report, maintaining consistency with the source material without unsupported secondary processing

## Information Density: High

- Each page focuses on one research point, content area fill rate **70-85%**, whitespace controlled to 15-30%
- Charts and data are the core content carriers; text serves to explain and logically connect
- Formulas, tables, and charts can be densely arranged but must maintain clear annotations, numbering, and visual hierarchy
- Each page can have a summary conclusion at the bottom or end, using bold or accent color to highlight the page's core finding
- High information density does not mean clutter: ensure readability under high density through alignment, columns, and spacing control

> **Core principle: The committee/audience can accurately extract one research finding from each page and understand its supporting evidence**

## Text-to-Visual Ratio: Chart-Dominant

- Recommended ratio for content pages: approximately 35% text + 55% charts, original figures, formulas, tables + 10% whitespace
- Results pages are absolutely chart-centric, with text serving only as annotations and key interpretations
- Encourage using flowcharts and diagrams to show research architecture, method workflows, and system design
- Avoid text-only pages (except for research background overview pages); strive for text-visual integration
- Original figures and charts from the source should be prioritized for direct reuse (see "Original Figure Reuse" strategy in "Content Expression Techniques")

## Color Guidance

- **University theme color**: Use the target university's emblem/VI standard color as the primary color — this is the top priority for academic presentation color schemes. When the user specifies a university name, look up the university's standard color and use it as the primary color. If the user does not specify a university, follow the color guidance below
- **Overall tone**: Color schemes should serve content readability, pursuing a clean, restrained, professional style. Keep the total number of colors minimal to avoid distracting the audience from academic content with visual complexity
- **Primary color logic**: A single low-saturation, steady theme color is recommended to anchor the overall design, used for titles, navigation bars, key annotations, and other core visual anchors. The tone should match the context — academic presentations call for calm, serious tones rather than vivid, dynamic colors
- **Background and body text**: Backgrounds should maintain sufficient brightness to ensure high readability of charts, formulas, and text; body text color must form clear contrast with the background to avoid visual fatigue
- **Chart colors**: Distinguishability is the primary goal for chart colors, while avoiding overly harsh or overly similar colors. Reference the color palettes of major academic journals (such as Nature/Science) to maintain professionalism
- **Accent color**: Used only to highlight key findings, core conclusions, or significance markers; usage should be restrained and not overextended
- **Overall prohibitions**: Avoid dark backgrounds for large body text areas (impairs chart readability), high-saturation neon colors, and visual clutter caused by multiple high-contrast colors used simultaneously in large areas

## Font Guidance

- **Titles**: Sans-serif Bold (e.g., QuattrocentoSans Bold, MiSans Bold), clean and clear, ensuring legibility in projection environments
- **Body text**: Sans-serif Regular (e.g., QuattrocentoSans, MiSans), ensuring readability on projectors
- **Formulas/code**: Use LaTeX for formula rendering; code can use the body text font
- **English references/terminology**: Keep the same font family as body text; do not switch fonts
- Font size hierarchy: Cover title 36-44px, page title 26-32px, subtitle (Table N / Fig. N / analysis section title) 22-26px, body analysis 18-22px (use 22px when page text content is light, 20px for moderate, 18px for heavy; must not go below 18px), footnotes, source annotations, navigation text 12-16px

## Content Pages

- **Navigation bar**: Recommend setting up a horizontal or vertical navigation bar with width/height matching the page width/height, chapter titles evenly distributed, current chapter highlighted with a white rectangle with themed border and readable text color, helping the audience track presentation progress and overall structure; navigation bar format is flexible
- **Page title**: Use descriptive short phrases (e.g., "Experimental Results: Multi-Metric Performance Comparison"), no more than one line; the title should directly convey the page's research point
- **University logo**: When the user specifies a university name, it is recommended to search online for the university's logo (or extract from user-uploaded attachments) and place it at a consistent fixed position on every page to clearly indicate the presenting institution
- **Content area**:
  - Single-column analysis structure (vertical narrative)
  - Left-figure, right-interpretation structure
  - Top-figure, bottom-insight structure
  - Dual-figure comparison structure
  - Data table + conclusion structure
- **Numbering and references**: All figures and tables should have standard numbering (e.g., Table 1, Figure 2, etc.); charts must have complete titles, legends, axis labels, and unit annotations
- **Reference citations**: References cited in the body must use standardized citation formats (see citation format requirements in "Narrative Style"). If a reference has an online link (such as DOI or paper homepage), `<a href="url">` hyperlinks can be used to link to the original text
- **Footer area**: Footnotes, reference superscripts, or supplementary notes at the bottom-left of the page; page numbers fixed at the bottom-right

## Narrative Style: Argumentation-Driven

- **Overall structure**: Organize slides following the classic academic paper structure — Background & Problem, Related Work, Method, Experimental Design, Results Analysis, Conclusion & Future Work
- **Language style**: Objective and rigorous, using academic language, avoiding subjective exaggeration and vague expressions. **Hallucinations are strictly prohibited — ensure all content has authentic, complete citations!**
- **Citation format requirements**: When citing related work in the body, reference numbers must be annotated (e.g., [1], [2-4]), with numbers corresponding one-to-one to the reference list at the end. Citation format should follow the user-specified standard (e.g., GB/T 7714, APA, IEEE, etc.); if the user does not specify, Chinese defenses default to GB/T 7714 format, English scenarios default to APA format
- **Faithful citation**: Faithfully cite the core viewpoints and conclusions of related work based on the original text; do not fabricate or speculate. Every citation must be traceable to the original literature
- **Reference page (required)**: A dedicated reference page must be included at the end of the slides, listing all references cited in the body with consistent formatting and sequential numbering. Each entry should include author, title, journal/conference name, year, and other key information. If references are numerous, they can span two pages, using small font size (12-16px) with compact arrangement

## Content Expression Techniques

- **Original figure reuse (priority)**: Academic presentations should prioritize using original figures and images from the paper or report rather than redrawing them. Original figures preserve complete data precision, annotation standards, and academic formatting; redrawing can introduce errors or omissions. When reusing, maintain the original image's resolution and clarity; add text interpretations or arrows to highlight key findings beside the figure when necessary
- **Experimental charts**: Line charts (trend comparison), bar charts (method comparison), scatter plots (correlation analysis), radar charts (multi-dimensional comparison), etc.; all charts must have complete annotations. Common chart types not defined in pptd.md (such as waterfall charts) can be built using shape + text box combinations
- **Data tables**: Method comparison tables (rows for methods, columns for metrics), best results highlighted with bold or accent color; tables must have headers and numbering
- **Flowcharts/architecture diagrams**: Use shapes, arrows, and text to illustrate research method workflows or system architecture, suitable for presenting methodology and experimental design
- **Formulas**: Key formulas displayed centered independently, rendered with LaTeX, with variable explanations before and after the formula
- **Bullet lists**: Research contributions, experimental settings, ablation study conclusions, etc. presented as numbered lists, concise and clear
- **References**: Complete reference list on a dedicated page at the end; footnotes on content pages can include abbreviated key references cited on that page

## Decoration Prohibitions

| Prohibited | Alternative |
|--------|---------|
| Flashy backgrounds/textures | Pure white, very light gray, or other plain backgrounds |
| Decorative icons/illustrations | Scientific diagrams and data charts |
| WordArt/text effects | Standard academic fonts, differentiated by weight and size |
| Charts without annotations | Complete annotations: title, axis labels, legend, units, data source |
| Gradient colors and shadow effects | Flat solid colors, maintaining clean academic chart standards |
| Excessive visual effects | Clean and restrained; the content itself is the focus |
