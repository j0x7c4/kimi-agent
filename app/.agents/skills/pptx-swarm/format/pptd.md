# Global Conventions
## Coordinate System and Units
* All geometry and dimension units are in px (pixels), 1px=1pt, page origin is at the top-left corner (0, 0)
* `bounds`: [x, y, w, h] array (px)
* `rotation`: Clockwise rotation angle (degrees) around the center of the element's bounds
* Z-Order: Determined by the order of the Page.elements array

## Font Family (fontFamily)
* Supports specifying a single font (e.g., `"MiSans"`) or using "Latin, CJK" format for dual fonts (e.g., `"Arial, Microsoft YaHei"`)
* Applies to all `fontFamily` / `font-family` fields

# Multi-File Structure
PPTD uses a multi-file structure. A presentation project consists of a main entry file and independent page files:
```
project/
  slides_name.pptd     # Main entry file (size/theme/title + page reference list)
  pages/                 # Page file directory
    cover.page           # One .page file per page
    intro.page
    chart_slide.page
```
## Path Rules
- Paths in the `pages` list of the main entry `.pptd` file are relative to the directory containing the main entry file
## Cannot Directly Operate .page Files
- `.page` files cannot be passed individually to the convert or check commands; they must go through the main entry `.pptd` file

# Top-Level Structure
## Main Entry File (.pptd)
```typescript
interface Presentation {
  title?: string;  // Presentation title
  theme: Theme;
  size: [number, number];  // [width, height], recommended [1280, 720] for 16:9, [960, 720] for 4:3
  pages: string[];  // Page file path list (e.g., pages/cover.page, pages/intro.page)
}
```
**Example:**
```yaml
title: My Presentation
size: [1280, 720]
theme:
  colors:
    primary: "#1A73E8"
  textStyles:
    title: { fontSize: 32 }
pages:
  - pages/cover.page
  - pages/intro.page
  - pages/chart_slide.page
```
## Page File (.page)
```typescript
type PageType = "cover" | "table_of_contents" | "chapter" | "content" | "final";

interface PageFile {
  pageType: PageType;

  background?: Fill;
  notes?: string;  // Speaker notes, recommended to leave empty unless explicitly requested by the user

  elements: Element[]; // Element list; elements later in the array appear on higher layers
}
```
**Example (cover.page):**
```yaml
pageType: cover
background:
  type: solid
  color: "#FFFFFF"
notes: Speaker notes
elements:
  - elementId: title1
    elementType: text
    bounds: [100, 200, 760, 80]
    content:
      text: Hello World
```

## ElementBase (Element Base Class)

```typescript
type ElementType = "text" | "shape" | "image" | "icon" | "table" | "chart";

interface ElementBase {
  elementId: string;
  elementType: ElementType;

  bounds: [number, number, number, number];  // [x, y, w, h] (px)

  rotation?: number;  // degrees, default 0
  opacity?: number;   // 0-1, default 1
  flip?: [boolean, boolean];  // [horizontal flip, vertical flip], default no flip
}

type Element = Text | Shape | Image | Icon | Table | Chart;
```

# Theme System

The theme is used to centrally manage the colors and text styles of a PPT, supporting references in any color or rich text field.

## Type Definitions

```typescript
interface Theme {
  colors: Record<string, string>;
  textStyles: Record<string, TextStyleConfig>;
  tableStyles?: Record<string, TableStyleConfig>;
}

interface TextStyleConfig {
  color?: string;           // Text color
  fontSize?: number;        // Font size (px)
  fontFamily?: string;      // Font family
  fontStyle?: 'normal' | 'italic';
  backgroundColor?: string; // Background color
  lineHeight?: number;      // Line height (multiplier)
  lineHeightPx?: number;    // Fixed line height (px), mutually exclusive with lineHeight
  letterSpacing?: number;   // Letter spacing (px)
  marginTop?: number;        // Paragraph top margin (px)
}

interface TableStyleConfig {
  fontSize?: number;         // Uniform font size (px), can be overridden by cell rich text
  fontFamily?: string;       // Uniform font family
  fill?: Fill;               // Default cell background (applies when not overridden by headerFill/bodyFill)
  headerFill?: string;       // Header row background color (first row), supports theme references
  headerColor?: string;      // Header row text color
  headerBold?: boolean;      // Header row bold, default true
  headerBorder?: Border | [Border | null, Border | null] | [Border | null, Border | null, Border | null, Border | null];  // Header row border (overrides global border)
  bodyFill?: string[];       // Data row alternating background colors, applied cyclically
  bodyColor?: string;        // Data row text color
  bodyBorder?: Border | [Border | null, Border | null] | [Border | null, Border | null, Border | null, Border | null];  // Data row border (overrides global border, excludes first and last rows)
  lastRowBorder?: Border | [Border | null, Border | null] | [Border | null, Border | null, Border | null, Border | null];  // Last row border (overrides bodyBorder and global border)
  firstColumnFill?: string;  // First column background color
  firstColumnColor?: string; // First column text color
  firstColumnBold?: boolean; // First column bold
  border?: Border | [Border | null, Border | null] | [Border | null, Border | null, Border | null, Border | null];  // Default cell border
}
```

## Example (YAML)

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
```

## Reference Specification

In any field that accepts a color or text style, theme references (`$` prefix + key name) can be used:

```yaml
fill:
  type: solid
  color: "$primary"      # Color reference
border:
  color: "$accent"
content:
  style: "$title"        # Text style reference
  text: "<p>...</p>"
```

- The `color` and `backgroundColor` fields within TextStyle also support color references in `$primary` format.

- The theme style set by TextContent.style serves as the default style and can be overridden by rich text inline styles or other TextContent fields.



# Element Types

## Text (Text Box)

```typescript
interface Text extends ElementBase {
  elementType: "text";
  content: TextContent;
}

interface TextContent {
  text: string;  // Rich text string, see "Rich Text Rules" below

  style?: string;           // Reference to a theme.textStyles key, e.g., "$title"
  color?: string;           // Base text color, can be overridden via <span style="color:...">
  fontSize?: number;        // Base font size (px), can be overridden via <span style="font-size:...">
  fontFamily?: string;      // Base font family; can be overridden via <span style="font-family:...">

  lineHeight?: number;      // Line height multiplier, default 1
  lineHeightPx?: number;    // Fixed line height (px), mutually exclusive with lineHeight, takes higher priority
  letterSpacing?: number;   // Letter spacing (px), default 0
  marginTop?: number;        // Paragraph top margin (px)

  textDirection?: "horizontal" | "vertical";  // Default horizontal
  wrap?: boolean;  // Text auto-wrap, default true, recommended to explicitly set to false for single-line text

  align?: Alignment; // Alignment

  gradient?: GradientFill;  // Text gradient color (applied to the text itself, not the text box)
  shadow?: Shadow;          // Text shadow (applied to the text itself, not the text box)
}

type HorizontalAlign = "left" | "center" | "right" | "justify" | "distributed";
// justify: Justified alignment (last line not stretched)
// distributed: Distributed alignment (last line stretched)
type VerticalAlign = "top" | "middle" | "bottom";
type Alignment = [HorizontalAlign, VerticalAlign];  // e.g., ["center", "middle"]
```

Examples:

```yaml
# Basic usage: theme style + plain text
- elementId: title-1
  elementType: text
  bounds: [100, 50, 760, 80]
  content:
    style: "$title"
    align: [center, middle]
    text: Annual Work Summary

# Rich text + content-level property overrides
- elementId: body-1
  elementType: text
  bounds: [100, 200, 600, 200]
  content:
    fontSize: 20
    color: "$text"
    lineHeight: 1.6
    align: [left, top]
    text: |
      <p><strong>Key Achievements</strong>: Completed <span style="color:$primary;">3</span> major projects</p>
      <p style="text-align:right; line-height:1.2"><span style="font-size:14px; color:#6b7280;">-- FY2024</span></p>

# Text gradient + shadow (effects applied to the text itself)
- elementId: hero-text
  elementType: text
  bounds: [100, 100, 760, 120]
  content:
    align: [center, middle]
    text: |
      <p><span style="font-size:64px;">FUTURE</span></p>
    gradient:
      type: gradient
      gradientType: linear
      angle: 90
      stops:
        - {position: 0, color: "$primary"}
        - {position: 1, color: "$accent"}
    shadow:
      blur: 6
      color: "#00000040"
      offset: [0, 3]
```

### Rich Text Rules

> **YAML Writing Rules (Must Follow)**: The `content.text` field **must use block scalar (`|`)** and must not be wrapped with quotes. Reason: Rich text contains `style="..."` double-quote attributes; wrapping with `"..."` or `'...'` will cause YAML parsing errors.
>
> ```yaml
> # Correct
> text: |
>   <p><span style="color:$primary;">Text</span></p>
>
> # Wrong (double quotes inside style="" break YAML syntax)
> text: "<p><span style="color:$primary;">Text</span></p>"
> ```

#### Supported Tags

| Tag         | Description                | Example                                        |
| ---------- | ----------------- | ----------------------------------------- |
| `<p>`      | Paragraph, supports style attribute to override paragraph-level styles | `<p>This is a paragraph</p>`                           |
| `<span>`   | Inline style            | `<span style="color:#ff0000">Red text</span>` |
| `<strong>` | Bold                | `<strong>Important</strong>`                     |
| `<em>`     | Italic                | `<em>Emphasis</em>`                             |
| `<u>`      | Underline               | `<u>Underlined text</u>`                            |
| `<s>`      | Strikethrough               | `<s>Deleted</s>`                              |
| `<sup>`    | Superscript                | `100<sup>&copy;</sup>`                         |
| `<sub>`    | Subscript                | `H<sub>2</sub>O`                          |
| `<a>`      | Hyperlink, supports `https://`, `http://`, `mailto:` protocols. Hyperlinks automatically add blue underline style, overriding other format tags               | `<a href="https://example.com">Link</a>`    |
| `<ul>`     | Unordered list              | `<ul><li>Item 1</li></ul>`                   |
| `<ol>`     | Ordered list              | `<ol><li>First item</li></ol>`                   |
| `<li>`     | List item               | Used with `<ul>` or `<ol>`                     |

#### Style Properties

Both `<p>` and `<span>` tags support `style` attribute for inline styles. Paragraph-level styles on `<p>` override TextContent defaults; paragraphs without explicit settings inherit the corresponding TextContent properties.

| Property               | Applicable Tags          | Example Values                       | Description                                         |
| ---------------- | ------------- | -------------------------- | ------------------------------------------ |
| color            | `<span>`      | #ff0000, $primary          | Text color (supports theme references)                               |
| font-size        | `<span>`      | 24px                       | Font size (px)                                   |
| font-family      | `<span>`      | "Arial", "Arial, Microsoft YaHei" | Font family             |
| font-style       | `<span>`      | normal, italic             | Font style                                       |
| background-color | `<span>`      | #ffff00, $accent           | Text background color (supports theme references)                              |
| text-align       | `<p>`         | center, right              | Overrides the horizontal alignment of TextContent.align                  |
| line-height      | `<p>`         | 1.5, 24px                  | Overrides TextContent.lineHeight / lineHeightPx    |
| letter-spacing   | `<p>`         | 2px                        | Overrides TextContent.letterSpacing                |
| margin-top        | `<p>`        | 8px                        | Overrides TextContent.marginTop                    |

```yaml
content:
  align: [left, top]
  lineHeight: 1.2
  text: |
    <p><span style="font-size:32px; color:$primary;">Main Title</span><span style="font-size:18px; color:$secondary;">Subtitle</span></p>
    <p style="text-align:center; line-height:1.8">This paragraph is center-aligned with 1.8x line height</p>
    <p style="text-align:right">This paragraph is right-aligned, inheriting the default 1.2 line height</p>
```

#### Plain Text Shorthand

When `content.text` contains plain text directly, it is equivalent to wrapping it in a single `<p>`: `text: "Hello"` is equivalent to `text: "<p>Hello</p>"`

#### LaTeX Formulas

Rich text content supports embedding LaTeX formulas using `\(...\)` delimiters, either as standalone paragraphs or mixed with other text within `<p>` tags. Rich text tags are not allowed inside formulas; they inherit the `color`, `font-size`, and `font-family` of the surrounding context. Block-level formulas (standalone paragraphs) follow paragraph alignment.

```yaml
content:
  text: |
    <p>Pythagorean theorem: \(a^2 + b^2 = c^2\)</p>
    <p>\(\int_0^1 x^2 \mathrm{d}x = \frac{1}{3}\)</p>
```

#### Default Styles

| Property | Default Value |
|---|---|
| Font | "MiSans", Arial, sans-serif |
| Font size | 18px |
| Color | #000000 |
| Font weight | normal (400) |
| Line height | 1 |


## Shape

```typescript
interface Shape extends ElementBase {
  elementType: "shape";

  shapeName: string;      // See supported shape list below
  adjustments?: number[]; // Shape geometry parameters, see supported shape list below

  path?: string; // Custom geometry path, used only when shapeName="custom". Format: "viewBoxW,viewBoxH;SVG path data"

  arrow?: [ArrowType | null, ArrowType | null]; // Connector arrows [start, end], only valid when shapeName is a line-type shape

  fill?: Fill;
  border?: Border;
  shadow?: Shadow;
}

type ArrowType = "none" | "arrow" | "stealth" | "diamond" | "oval";
```

Examples:

```yaml
- elementId: shape-1
  elementType: shape
  bounds: [200, 200, 300, 150]
  shapeName: roundRect
  adjustments: [20000]
  fill:
    type: solid
    color: "$primary"
  border:
    style: solid
    width: 2
    color: "$accent"
- elementId: shape-2
  elementType: shape
  bounds: [100, 200, 500, 5]
  shapeName: custom
  path: "1000,100;M0 0 L1000 0 L1000 100 L0 100 Z"
  fill:
    type: solid
    color: "$accent1"
```

### Supported Shape List

adjustments parameter conventions:
* Described following the parameter order and count defined by OOXML
* Value range is generally [0, 100000] (100000 = 100%), conversion: `value / 1000 = percentage`
* The parameter array must be complete (intermediate values cannot be omitted), or entirely absent to use default values

#### Shape List

> The complete list of 177 shapes and their adjustments parameters can be found in ./shapes.md. The table below lists only the most commonly used shapes.

| shapeName | Description | adjustments Parameters | Default Values |
| --------- | --- | -------------- | ---- |
| rect | Rectangle | - | - |
| roundRect | Rounded rectangle | [corner radius] | [16667] |
| ellipse | Ellipse | - | - |
| triangle | Triangle | [apex horizontal position] | [50000] |
| diamond | Diamond | - | - |
| plus | Plus sign | [arm width ratio] | [25000] |
| homePlate | Pentagon arrow | [arrow tip offset] | [50000] |
| chevron | Chevron | [V tip offset] | [50000] |
| donut | Donut | [ring width ratio] | [25000] |
| star5 | 5-point star | [inner radius ratio, horizontal factor, vertical factor] | [19098, 105146, 110557] |
| rightArrow | Right arrow | [shaft width, head length] | [50000, 50000] |
| wedgeRectCallout | Rectangular callout | [tip X offset, tip Y offset] | [-20833, 62500] |
| bracePair | Brace pair | [curvature] | [8333] |
| custom | Custom geometry | - (uses `path` property to define geometry path) | - |

> **Angle parameter note**: Shapes such as `pie`, `arc`, `blockArc` use angle units of OOXML 1/60000 of a degree, conversion: `OOXML value = angle x 60000`.
> Flowchart shapes (`flowChartProcess`, `flowChartDecision`, `flowChartTerminator`, etc.) are detailed in ./shapes.md.

#### Line Shape List
The following `shapeName` values are line-type shapes that support endpoint arrows via the `arrow` field. Line coordinate rules:
1. bounds = [x, y, width, height] represents the bounding box of the line, **the line connects the diagonal corners of the bounding box**
2. **Horizontal line: height must be 0**; **Vertical line: width must be 0**
3. Default direction: from the top-left to the bottom-right of the bounds
4. `flip` changes the line direction, e.g., `[true, false]` makes the line go from top-right to bottom-left

Examples:
```yaml
# Horizontal line (height must be 0)
- elementId: hline
  elementType: shape
  bounds: [100, 250, 700, 0]
  shapeName: straightConnector1
  border: {style: solid, width: 2, color: "$primary"}

# Diagonal line with arrow (width and height are both non-zero)
- elementId: diagonal
  elementType: shape
  bounds: [100, 100, 300, 200]
  shapeName: straightConnector1
  arrow: [null, "arrow"]
  border: {style: solid, width: 2, color: "$accent"}
```

| shapeName          | Description           | adjustments           | Default Values             | Value Range         |
| ------------------ | ------------ | --------------------- | --------------- | ------------ |
| straightConnector1 | Straight line           | -                     | -               | -            |
| bentConnector2     | L-shaped connector (1 bend point)  | -                     | -               | -            |
| bentConnector3     | Z-shaped connector (2 bend points)  | X coordinate offset (midpoint position)        | [50000]        | [0, 100000] |
| bentConnector4     | Z-shaped connector (3 bend points)  | [X offset, Y offset] (midpoint position) | [50000, 50000] | [0, 100000] |
| curvedConnector2   | Simple arc         | -                     | -               | -            |
| curvedConnector3   | S-shaped curve (1 inflection point) | X coordinate offset (control point position)        | [50000]        | [0, 100000] |
| curvedConnector4   | Spiral curve (2 inflection points)  | [X offset, Y offset] (control point position) | [50000, 50000] | [0, 100000] |

## Image

```typescript
interface Image extends ElementBase {
  elementType: "image";

  src: string;  // Image URL or local path

  // Shape clipping (optional, default "rect")
  shapeName?: string;
  adjustments?: number[];

  // Fit and crop
  fit?: ImageFit;    // Default { mode: "cover" }
  crop?: ImageCrop;

  border?: Border;
  shadow?: Shadow;
}

interface ImageFit {
  mode: "fill" | "contain" | "cover";
  // fill: Stretch to fill the container, may distort
  // contain: Display the complete image, maintain aspect ratio, may leave whitespace
  // cover: Fill the container, maintain aspect ratio, may crop (default)
}

interface ImageCrop {
  left?: number;    // 0-1, crop ratio
  top?: number;     // 0-1
  right?: number;   // 0-1
  bottom?: number;  // 0-1
}
```

Example:

```yaml
- elementId: img-1
  elementType: image
  bounds: [50, 50, 400, 300]
  src: "https://example.com/image.jpg"
  shapeName: roundRect
  adjustments: [15000]
  fit:
    mode: cover
  shadow:
    blur: 10
    color: "#00000033"
    offset: [0, 4]
```

## Icon

```typescript
interface Icon extends ElementBase {
  elementType: "icon";

  iconName: string;  // Font Awesome icon name, see Icon Library section below

  fill?: Fill;  // Icon fill, supports complex fills
  border?: Border;
  shadow?: Shadow;
}
```

Example:

```yaml
- elementId: icon-1
  elementType: icon
  bounds: [100, 100, 48, 48]
  iconName: "fas:lightbulb"
  fill:
    type: solid
    color: "$primary"
```

### Icon Library

This specification uses Font Awesome 7.x. Documentation: https://fontawesome.com/search?ic=free-collection

iconName format: `style:name`

* `fas`: Solid (filled, default)
* `far`: Regular
* `fab`: Brands

Examples: `fas:house` (solid house), `far:heart` (outlined heart), `fab:github` (brand icon)

## Table

```typescript
interface Table extends ElementBase {
  elementType: "table";

  columnWidths: number[];  // Width percentage per column (0-1, sum to 1)
  rowHeights: number[];    // Height percentage per row (0-1, sum to 1)

  rows: Cell[][];

  style?: string | TableStyleConfig;  // "$default" references theme, or inline TableStyleConfig

  // Priority: Cell-level properties > style config > defaults

  shadow?: Shadow;
}

interface Cell {
  content?: TextContent;  // Cell text content; if content.align is not set, defaults to [center, middle]
  fill?: Fill;            // Cell background
  border?: Border | [Border | null, Border | null] | [Border | null, Border | null, Border | null, Border | null];  // Cell border, supports per-edge setting
  rowSpan?: number;       // Number of rows to merge downward, default 1
  colSpan?: number;       // Number of columns to merge rightward, default 1
}
```

border array format: single value = same for all sides; two values = [top-bottom, left-right]; four values = [top, right, bottom, left] (clockwise); `null` means no border on that side.

Default when border is not set: `{style: solid, width: 1, color: "#000000"}`

### Basic Example (Using Theme Table Style)

```yaml
- elementId: table-basic
  elementType: table
  bounds: [80, 120, 800, 280]
  columnWidths: [0.3, 0.35, 0.35]
  rowHeights: [0.33, 0.33, 0.34]
  style: "$default"
  rows:
    - - content: {text: "Metric"}
      - content: {text: "2023"}
      - content: {text: "2024"}
    - - content: {text: "Revenue (100M)"}
      - content: {text: "82.5"}
      - content: {text: "96.3"}
    - - content: {text: "Net Profit (100M)"}
      - content: {text: "12.1"}
      - content: {text: "15.8"}
```

### Merged Cells

Use `rowSpan`/`colSpan` to declare merge regions. Each row array lists only actual cells, automatically skipping occupied columns from left to right.

Example (3x3 table, top-left 2x2 merge):

```yaml
- elementId: table-1
  elementType: table
  bounds: [100, 100, 600, 400]
  columnWidths: [0.33, 0.33, 0.34]
  rowHeights: [0.33, 0.33, 0.34]
  rows:
    - - content:
          text: "Merged Cell"
        fill:
          type: solid
          color: "$accent"
        rowSpan: 2
        colSpan: 2
      - content:
          text: "C1"
    - - content:
          text: "C2"
    - - content:
          text: "A3"
      - content:
          text: "B3"
      - content:
          text: "C3"
```

## Chart

```typescript
// Bar chart, line chart, area chart, scatter chart, pie chart (including donut), radar chart, combo chart, bubble chart
type ChartType = 'bar' | 'line' | 'area' | 'scatter' | 'pie' | 'radar'
               | 'combo' | 'bubble';

// -- Chart-level options (cannot be overridden per series) --
interface ChartOptions {
  direction?: 'vertical' | 'horizontal';  // bar only, default 'vertical'
  barWidth?: number;      // Bar width ratio 0~1 (larger = wider bars), default auto
  innerRadius?: number;   // Pie chart inner radius ratio 0~1, creates donut chart when set
  startAngle?: number;    // Pie chart start angle (degrees), default 0
  stacked?: true | '100%'; // Stacking mode (applicable to bar/line/area)
  nullHandling?: 'zero' | 'gap' | 'connect';  // Null value handling, default 'gap'
  fontFamily?: string;    // Chart global font, all text components inherit this setting
}

// -- Chart title --
// Supports string shorthand: title: "text"
interface ChartTitleConfig {
  text: string;
  color?: string;
  fontSize?: number;
}

// -- Data labels --

interface DataLabelConfig {
  show?: boolean;           // Default false, i.e., when dataLabels is not configured, all chart types default to not showing data labels
  content?: 'value' | 'percentage' | 'category' | 'name';  // Default 'value'
  color?: string;
  numberFormat?: string;    // e.g., '0.0%', '#,##0'
  fontSize?: number;
}
// The fontSize of each component can override the auto-calculated value; when not set, it is auto-calculated based on chart size. fontFamily is uniformly inherited from ChartOptions.fontFamily.

// -- Legend --
// Supports bool shorthand: legend: false / legend: true
interface LegendConfig {
  show?: boolean;
  position?: 'top' | 'bottom' | 'left' | 'right';  // Default 'bottom'
  color?: string;
  fontSize?: number;
}

// -- Series style --
type MarkerShape = 'circle' | 'square' | 'diamond' | 'triangle';

interface MarkerConfig {
  shape?: MarkerShape;    // Default 'circle'
  fill?: SolidFill | GradientFill;   // Inherits SeriesStyleConfig.fill when not set
  border?: Border;                    // Inherits SeriesStyleConfig.border when not set
  size?: number;          // Marker size (px); auto-calculated based on chart size when not set (scatter charts default to larger)
}

interface SeriesStyleConfig {
  name?: string;          // Series display name (overrides the corresponding value in names)
  fill?: SolidFill | GradientFill;   // Series fill
  border?: Border;        // Series border
  smooth?: boolean;       // Smooth curve (line/area)
  line?: 'solid' | 'dash' | 'dot';   // Line style
  width?: number;         // Line width (px)
  marker?: false | MarkerConfig;      // false=hide marker, object=custom marker
  type?: 'bar' | 'line' | 'area';    // combo only, specifies series subtype
  axis?: 'primary' | 'secondary';    // Default 'primary', used in combo to bind to secondary axis
  dataLabels?: DataLabelConfig;       // Series-level data label override
}

// -- Axes --
interface AxisLabelConfig {
  color?: string;         // Tick label text color
  fontSize?: number;      // Tick label font size (px)
}

interface AxisLineConfig {
  style?: 'solid' | 'dash' | 'dot';  // Line style
  color?: string;         // Color
  width?: number;         // Line width (px)
  arrow?: boolean;        // Arrow (ignored in gridLine)
}

// -- Axis title --
interface AxisTitleConfig {
  text: string;
  color?: string;
  fontSize?: number;
}

interface AxisConfig {
  show?: boolean;                     // false=hide entire axis
  label?: boolean | AxisLabelConfig;  // false=hide tick labels
  axisLine?: boolean | AxisLineConfig; // false=hide axis line, object=custom style
  gridLine?: boolean | AxisLineConfig; // false=hide grid lines, object=custom style
  min?: number;           // Minimum value (numeric axis)
  max?: number;           // Maximum value (numeric axis)
  numberFormat?: string;  // Tick number format, e.g., '#,##0', '0.0%'
  title?: string | AxisTitleConfig;   // Axis title, string shorthand or object config
}

interface Chart extends ElementBase {
  elementType: 'chart';

  // -- Data --
  type: ChartType;
  data: Record<string, any>[];    // Array of objects, each record is a data point
  x: string;                      // Category field name (field values used as category labels)
  y: string | string[];           // Value field name(s) (multiple = one series each)
  names?: string[];               // Series display names (overrides y field names), corresponds 1:1 with y

  // -- Series colors (shorthand) --
  colors?: string[];              // Color for each series, applied cyclically in order

  // -- Chart-level options --
  options?: ChartOptions;

  // -- Series styles --
  // key: '*' for global default, y field name for per-series override
  seriesStyle?: Record<'*' | string, SeriesStyleConfig>;

  // -- Axis styles --
  // bar(vertical)/line/area: xAxis=category axis, yAxis=value axis
  // bar(horizontal):         xAxis=value axis, yAxis=category axis
  // scatter/bubble:          both axes are value axes
  // pie/radar:               no axes, this config is ignored
  xAxis?: AxisConfig;
  yAxis?: AxisConfig;

  title?: string | ChartTitleConfig;  // Chart title
  legend?: boolean | LegendConfig;    // false=hide, true=show, object=config
  dataLabels?: DataLabelConfig;       // Chart-level data labels
  size?: string;                      // bubble only, bubble size field name
  secondaryAxis?: AxisConfig;         // Secondary axis (used for right-side value axis in combo charts)

  // -- Container styles --
  fill?: Fill;
  border?: Border;
}
```

### Examples

Basic bar chart (vertical, default):

```yaml
- elementId: c1
  elementType: chart
  bounds: [50, 100, 600, 400]
  type: bar
  data:
    - {quarter: "Q1", revenue: 120, cost: 220}
    - {quarter: "Q2", revenue: 132, cost: 182}
    - {quarter: "Q3", revenue: 101, cost: 191}
    - {quarter: "Q4", revenue: 134, cost: 234}
  x: quarter
  y: [revenue, cost]
  names: ["Revenue", "Cost"]
  colors: ["#5470c6", "#91cc75"]
```

Line chart (per-series differentiation):

```yaml
- elementId: c2
  elementType: chart
  bounds: [50, 100, 600, 400]
  type: line
  data:
    - {month: "Jan", actual: 72, target: 65, baseline: 50}
    - {month: "Feb", actual: 85, target: 70, baseline: 50}
    - {month: "Mar", actual: null, target: 78, baseline: 50}
    - {month: "Apr", actual: 90, target: 82, baseline: 50}
  x: month
  y: [actual, target, baseline]
  names: ["Actual", "Target", "Baseline"]
  colors: ["#5470c6", "#ee6666", "#999999"]
  seriesStyle:
    "*":
      smooth: true
      width: 2
    actual: {line: solid, width: 3}
    target: {line: dash}
    baseline: {line: dot, width: 1, smooth: false, marker: false}
  yAxis:
    min: 0
    max: 100
    gridLine:
      color: "#f0f0f0"
  xAxis:
    label:
      color: "#666"
      fontSize: 10
```

Combo chart (bar + line + secondary axis):

```yaml
- elementId: c4
  elementType: chart
  bounds: [50, 100, 600, 400]
  type: combo
  title: "Revenue and Growth Rate"
  legend: {position: top}
  data:
    - {month: "Jan", revenue: 120, growthRate: 0.15}
    - {month: "Feb", revenue: 150, growthRate: 0.25}
  x: month
  y: [revenue, growthRate]
  names: ["Revenue", "Growth Rate"]
  colors: ["#5470c6", "#ee6666"]
  seriesStyle:
    revenue: {type: bar}
    growthRate: {type: line, axis: secondary, smooth: true, width: 2}
  yAxis: {title: "Amount (10K)", numberFormat: "#,##0"}
  secondaryAxis: {title: "Growth Rate", numberFormat: "0%", min: 0, max: 0.5}
```

Pie chart (donut):

```yaml
- elementId: c6
  elementType: chart
  bounds: [50, 100, 400, 400]
  type: pie
  title: "Revenue Composition"
  legend: {position: right}
  data:
    - {category: "Product", value: 55}
    - {category: "Service", value: 30}
    - {category: "Licensing", value: 15}
  x: category
  y: [value]
  colors: ["#5470c6", "#91cc75", "#fac858"]
  options:
    innerRadius: 0.5
    startAngle: 90
  dataLabels:
    show: true
    content: percentage
    numberFormat: "0%"
```
**Note: If you want to customize colors, please set the color values for all elements added to the chart, including series/markers/lines, etc. Avoid inconsistent chart color schemes!**

# Style Structures (Fill / Border / Shadow)

## Fill

```typescript
// Solid fill
interface SolidFill {
  type: "solid";
  color: string;  // hex8 color e.g., #ffffff99, or theme reference e.g., "$primary"
}

// Gradient fill
interface GradientFill {
  type: "gradient";
  gradientType: "linear" | "radial";
  stops: ColorStop[];
  angle?: number;  // degrees, linear only, default 0 (left→right). 90=top→bottom, 180=right→left, 270=bottom→top
}

// Image fill
interface ImageFill {
  type: "image";
  src: string;  // Image URL or local path

  fit?: ImageFit;
  crop?: ImageCrop;  // Only effective when fit.mode is not "fill"

  mask?: SolidFill | GradientFill;  // Mask color overlay
  opacity?: number; // Opacity, 0-1
}

type Fill = SolidFill | GradientFill | ImageFill;
```

## Border

```typescript
interface Border {
  style: "solid" | "dash" | "dot" | "none";
  width?: number;   // px, default 1
  color: string;    // Supports theme references, supports hex8 for transparency (e.g., "#0a0a0d80")
}
```

## Shadow

```typescript
interface Shadow {
  blur: number;              // Blur radius (px)
  color: string;             // Shadow color, recommended to use colors with alpha
  offset?: [number, number]; // [x, y] offset (px), default [0, 0]
}
```

## ColorStop (Gradient Color Stop)

```typescript
interface ColorStop {
  position: number;  // 0-1
  color: string;     // Supports theme references, e.g., "$primary"
}
```

Example:

```yaml
# Image fill (for Shape/Page background)
fill:
  type: image
  src: "https://example.com/bg.jpg"
  fit: {mode: cover}
  mask:
    type: solid
    color: "#00000080"
  opacity: 0.9
```

# Validation Constraints

## Value Ranges

| Field                 | Constraint            |
| ------------------ | ------------- |
| opacity            | 0 <= value <= 1 |
| ColorStop.position | 0 <= value <= 1 |
| ImageCrop.\*       | 0 <= value <= 1 |
| columnWidths       | Array elements sum = 1     |
| rowHeights         | Array elements sum = 1     |

## Theme Reference Constraints

All theme reference formats are `$<key>`. Circular references are prohibited, and the key must exist in the corresponding table:

| Reference Type | Key Location |
|---|---|
| Color reference | theme.colors |
| Text style reference | theme.textStyles |
| Table style reference | theme.tableStyles |
