---
name: kimi-widget
description: Kimi widget design system. Read this BEFORE your first show_widget call. Contains CSS variables, typography, layout rules, and component patterns. Your widget code runs inside a sandboxed iframe that has this design system pre-loaded — use the provided CSS variables, never hardcode colors or fonts.
---

# Kimi Widget — Design System

## When to generate a widget

1. **Your question must be decisive** — the user's answer will materially change your next action. If the answer doesn't affect the outcome, don't ask.
2. **Help the user think clearly, don't make the user think for you** — options should be concrete enough for the user to judge intuitively, never so abstract that they need to think another layer.
3. **Ask precisely** — each widget should collect one clear dimension of intent. Don't cram 6 questions into one widget.
4. **If you can infer, don't ask** — if the answer is derivable from context, user history, or common sense, just act.
5. **Pick the right interaction for the question** — you have radio, checkbox/chips, input, slider, toggle, drag-to-rank, scale, prev/next pagination, and any reasonable combination. Choose based on context.

## Design System

Your widget code runs inside a sandboxed iframe where **a design system CSS is already loaded**. All CSS variables, form element styles, and SVG classes listed below are available at runtime. You do not need to define them — just reference them.

**CRITICAL**: Never hardcode colors, fonts, or border-radius values. Always use `var(--xxx)`. Hardcoded values will break in dark mode and look inconsistent with the host UI.

## Core Design System

These rules apply to ALL widget output.

### Philosophy
- **Seamless**: Users shouldn't notice where kimi.com ends and your widget begins.
- **Flat**: No gradients, mesh backgrounds, noise textures, or decorative effects. Clean flat surfaces.
- **Compact**: Show the essential inline. Explain the rest in text.
- **Text goes in your response, visuals go in the tool** — All explanatory text, descriptions, introductions, and summaries must be written as normal response text OUTSIDE the tool call. The tool output should contain ONLY the visual element (diagram, chart, interactive widget). Never put paragraphs of explanation, section headings, or descriptive prose inside the HTML/SVG.

### Streaming
Output streams token-by-token. Structure code so useful content appears early.
- **HTML**: `<style>` (short) → content HTML → `<script>` last.
- **SVG**: `<defs>` (markers) → visual elements immediately.
- Prefer inline `style="..."` over `<style>` blocks — inputs/controls must look correct mid-stream.
- Keep `<style>` under ~15 lines. Interactive widgets with inputs and sliders need more style rules — that's fine, but don't bloat with decorative CSS.
- Gradients, shadows, and blur flash during streaming DOM diffs. Use solid flat fills instead.

### Rules
- No `<!-- comments -->` or `/* comments */` (waste tokens, break streaming)
- No font-size below 11px
- Emoji are allowed for decorative icons (e.g., 🌍 🧬). Set `font-size: 16px` explicitly — never let emoji inherit the container's font size.
- No gradients, drop shadows, blur, glow, or neon effects
- No dark/colored backgrounds on outer containers (transparent only — host provides the bg)
- **Typography**: The default font is inherited from the host via `var(--font-sans)`. Never set your own font-family — the design system provides it.
- **Headings**: h1 = 22px, h2 = 18px, h3 = 16px — all `font-weight: 500`. Heading color is pre-set to `var(--color-text-primary)` — don't override it. Body text = 16px, weight 400, `line-height: 1.7`. **Two weights only: 400 regular, 500 bold.** Never use 600 or 700 — they look heavy against the host UI.
- **Sentence case** always. Never Title Case, never ALL CAPS. This applies everywhere including SVG text labels and diagram headings.
- **No mid-sentence bolding**, including in your response text around the tool call. Entity names, class names, function names go in `code style` not **bold**. Bold is for headings and labels only.
- The widget container is `display: block; width: 100%`. Your HTML fills it naturally — no wrapper div needed. Just start with your content directly. If you want vertical breathing room, add `padding: 1rem 0` on your first element.
- Never use `position: fixed` — the iframe viewport sizes itself to your in-flow content height, so fixed-positioned elements collapse it to `min-height: 100px`.
- No DOCTYPE, `<html>`, `<head>`, or `<body>` — just content fragments.
- When placing text on a colored background (badges, pills, cards, tags), use a semantically matching text variable (e.g., `--color-text-info` on `--color-background-info`). Never use plain black or generic gray on colored fills.
- **Corners**: use `border-radius: var(--border-radius-md)` (or `-lg` for cards) in HTML. In SVG, `rx="4"` is the default — larger values make pills, use only when you mean a pill.
- **No rounded corners on single-sided borders** — if using `border-left` or `border-top` accents, set `border-radius: 0`. Rounded corners only work with full borders on all sides.
- **No titles or prose inside the tool output** — see Philosophy above.
- **Icon sizing**: For inline SVG icons, set `width: 16px; height: 16px`. For larger decorative icons, use 24px max.
- No tabs, carousels, or `display: none` sections during streaming — hidden content streams invisibly. Show all content stacked vertically. (Post-streaming JS-driven steppers are fine.)
- No nested scrolling — auto-fit height.
- **Keep widgets compact** — aim for content that fits in one viewport without scrolling. If there is too much content (e.g., many questions, long forms), split into pages with prev/next navigation inside the widget, rather than making one very tall widget.
- Scripts execute after streaming. Load external libraries via CDN `<script src="...">` (UMD globals), then use the global in a following `<script>` block.

### CSS Variables (pre-loaded, do NOT redefine)

All variables auto-adapt to light/dark mode.

**Text**:
| Variable | Usage |
|----------|-------|
| `--color-text-primary` | Main text |
| `--color-text-secondary` | Secondary text, descriptions |
| `--color-text-tertiary` | Hints, placeholders |
| `--color-text-info` | Links, emphasis (Kimi blue) |
| `--color-text-danger` | Error text |
| `--color-text-success` | Success text |
| `--color-text-warning` | Warning text |

**Backgrounds**:
| Variable | Usage |
|----------|-------|
| `--color-background-primary` | Cards, container backgrounds |
| `--color-background-secondary` | Surfaces, input field backgrounds |
| `--color-background-tertiary` | Page base color |
| `--color-background-info` | Light blue fill for small elements |
| `--color-background-danger` | Light red background |
| `--color-background-success` | Light green background |
| `--color-background-warning` | Light orange background |

**Borders**:
| Variable | Usage |
|----------|-------|
| `--color-border-tertiary` | Default borders |
| `--color-border-secondary` | Hover borders |
| `--color-border-primary` | Emphasis borders |
| `--color-border-info` | Info/accent border (Kimi blue) |

**Brand**:
| Variable | Usage |
|----------|-------|
| `--kimi-accent` | Primary action buttons, brand color (Kimi blue) |
| `--kimi-accent-10` | Brand color at 10%, selected state backgrounds |
| `--kimi-accent-disabled` | Button disabled state |

**Kimi-specific** (additional tokens available):
| Variable | Usage |
|----------|-------|
| `--kimi-fills-f1` | Hover overlay |
| `--kimi-fills-f2` | Pressed overlay, toggle container bg |
| `--kimi-fills-f3` | Stronger fill |
| `--kimi-fills-f4` | Emphasis fill, unchecked radio/checkbox border |
| `--kimi-labels-quaternary` | Weakest text, less prominent than tertiary |
| `--kimi-labels-link` | Link text color |
| `--kimi-purple` | Purple accent (secondary brand) |

**Typography**: `--font-sans`, `--font-serif`, `--font-mono`
**Layout**: `--border-radius-md` (8px), `--border-radius-lg` (12px — preferred for most components), `--border-radius-xl` (16px)

**Dark mode is mandatory** — every color must work in both modes:
- In HTML: always use CSS variables (`var(--color-text-primary)`, `var(--color-background-secondary)`, etc.) for text and backgrounds. **Never hardcode colors like `color: #333` or `background: white`** — they will be invisible or jarring in dark mode.
- In SVG: every `<text>` element needs a class (`t`, `ts`, `th`) — never omit fill or use `fill="inherit"`.
- Mental test: if the background were near-black, would every text element still be readable?

**Correct vs incorrect examples:**

```html
<!-- WRONG: hardcoded colors, custom font, custom variables -->
<div style="color: #2c2416; background: #faf8f3; font-family: system-ui;">
  <h1 style="color: #4a5d23;">Title</h1>
</div>

<!-- CORRECT: uses design system variables -->
<div style="color: var(--color-text-primary); background: var(--color-background-secondary);">
  <h1 style="color: var(--color-text-primary);">Title</h1>
</div>
```

### Pre-styled Components (already loaded, write bare tags)

The following components are **pre-styled** by the host where noted. For pre-styled components, write bare HTML tags — they will automatically match the Kimi design system. For others, follow the specs below.

**Button** (pre-styled: bare `<button>` = 32px height, outline style) — 4 fixed heights: 48, 40, 32, 26px. Default bare `<button>` renders at 32px. For other sizes, override with inline style (e.g., `style="height: 40px; padding: 0 12px; border-radius: 12px"`). Min-width based on 3 characters (centered). Icon buttons exempt from min-width rule. If a button triggers `sendPrompt`, append a ↗ arrow to its label.

| Size | height | padding | border-radius | font-size |
|------|--------|---------|---------------|-----------|
| Large | 48px | 0 16px | 12px | 15px |
| Medium | 40px | 0 12px | 12px | 14px |
| Small (default) | 32px | 0 10px | 10px | 14px |
| Mini | 26px | 0 8px | 8px | 12px |

Primary button (Kimi blue, solid): `style="background: var(--kimi-accent); color: white; border: none;"`

**Input** (pre-styled: bare `<input>` works) — Text input, textarea, select. Height 40px, `var(--color-background-primary)` bg, focus border turns `var(--color-border-info)`.

**Radio** (not pre-styled, use custom markup) — 16x16px. Selected: `var(--kimi-accent)` fill with 8x8 white inner circle. Unselected: `var(--kimi-fills-f4)` border. For mutually exclusive options within a group.

**Checkbox** (not pre-styled, use custom markup) — 16x16px. Selected: `var(--kimi-accent)` fill with white checkmark. Unselected: `var(--kimi-fills-f4)` border, rounded square. For binary selection (checked/unchecked).

**Switch/Toggle** (not pre-styled, use custom markup) — Track: 44x24px, `var(--kimi-accent)` when on, `var(--kimi-fills-f2)` when off, border-radius 999px. Thumb: 16x16px white circle. For binary on/off states.

**Range slider** (pre-styled: bare `<input type="range">` works) — 4px track + 18px thumb.

### sendPrompt(text)
A global function that sends a message to chat as if the user typed it. Use it when the user's next step benefits from Kimi thinking. Handle filtering, sorting, toggling, and calculations in JS instead.

**Copy guidelines for sendPrompt text**: The text will appear in chat as if the user typed it. Write it in a tone that feels natural coming from the user — concise, direct, no filler. Avoid robotic phrasing like "I have selected option A, please proceed". Write what a smart user would actually say.

### Links
`<a href="https://...">` just works — clicks are intercepted and open the host's link-confirmation dialog.

## When nothing fits
Pick the closest use case below and adapt. When nothing fits cleanly:
- Default to editorial layout if the content is explanatory
- Default to card layout if the content is a bounded object
- All core design system rules still apply
- Use `sendPrompt()` for any action that benefits from Kimi thinking

## SVG setup

**ViewBox safety checklist** — before finalizing any SVG, verify:
1. Find your lowest element: max(y + height) across all rects, max(y) across all text baselines.
2. Set viewBox height = that value + 40px buffer.
3. Find your rightmost element: max(x + width) across all rects. All content must stay within x=0 to x=624.
4. For text with text-anchor="end", the text extends LEFT from x.
5. Never use negative x or y coordinates. The viewBox starts at 0,0.

**SVG setup**: `<svg width="100%" viewBox="0 0 624 H">` — 624px wide, flexible height.

**Pre-built SVG classes** (already loaded):
- `class="t"` = sans 14px primary, `class="ts"` = sans 12px secondary, `class="th"` = sans 14px medium (500)
- `class="box"` = neutral rect (bg-secondary fill, border stroke)
- `class="arr"` = arrow line (1.5px, open chevron head)
- `class="leader"` = dashed leader line

Arrow marker (include in every SVG):
```
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>
```

## UI components

### Aesthetic
Flat, clean, white surfaces. Minimal 0.5px borders. Generous whitespace.

### Tokens
- Borders: always `0.5px solid var(--color-border-tertiary)`
- Corner radius: `var(--border-radius-md)` for most elements, `var(--border-radius-lg)` for cards
- Cards: `var(--color-background-primary)` bg, 0.5px border, radius-lg, padding 1rem 1.25rem
- Form elements are pre-styled — write bare tags
- Round every displayed number

### Use cases

**1. Interactive explainer** — sliders, buttons, live state displays
```html
<div style="display: flex; align-items: center; gap: 12px; margin: 0 0 1.5rem;">
  <label style="font-size: 14px; color: var(--color-text-secondary);">Years</label>
  <input type="range" min="1" max="40" value="20" id="years" style="flex: 1;" />
  <span style="font-size: 14px; font-weight: 500; min-width: 24px;" id="years-out">20</span>
</div>
```
Use `sendPrompt()` for follow-up questions.

**2. Compare options** — side-by-side card grid
- Use `repeat(auto-fit, minmax(160px, 1fr))` for responsive columns
- Each option in a card with `var(--color-background-primary)` bg, `0.5px solid var(--color-border-tertiary)` border
- Recommended option: accent with `border: 2px solid var(--color-border-info)`
- Add `sendPrompt()` buttons for deeper exploration

**3. Data record** — bounded UI object in a single raised card
```html
<div style="background: var(--color-background-primary); border-radius: var(--border-radius-lg); border: 0.5px solid var(--color-border-tertiary); padding: 1rem 1.25rem;">
  <!-- content here -->
</div>
```

## Charts (Chart.js)
Load UMD build via CDN. **Exception to the no-hardcode rule**: Canvas cannot resolve CSS variables, so use hardcoded hex values for chart colors. Use Kimi brand colors: `#1783FF` (blue), `#16c456` (green), `#ff3849` (red), `#ff9500` (orange), `#985ffb` (purple).
