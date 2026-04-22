# Design Guide for Vibecoding Websites

Reference for the Pro_Designer subagent. Read this before writing any design documents.

---

## Tech Stack

Node.js 20 · Tailwind CSS v3.4.19 · Vite v7.2.4 · React 19 + TypeScript · shadcn/ui

## Visual Capabilities

Your implementation team can build ambitious visual experiences. Design boldly — use these libraries generously:

- **GSAP + ScrollTrigger**: Scroll-driven storytelling, pinned sections, parallax layers, text split animations (SplitText), timeline sequences. You can pin a section for 150-200vh and drive animations by scroll progress — don't settle for simple fade-ins.
- **Framer Motion**: Page transitions, layout animations, hover/tap/click micro-interactions, staggered list reveals, drag gestures, button-triggered animations. Great for making every clickable element feel alive.
- **Three.js / React Three Fiber**: 3D hero backgrounds, floating particle fields, shader effects, interactive 3D product viewers. Use for high-impact moments.
- **Lenis**: Buttery smooth scrolling across the entire page.
- **Google Fonts**: Full library available — go beyond safe defaults. Pick fonts with character.

## Visual Effects You Can Reach For

These are possibilities, not requirements. Mix, adapt, and invent — pick what fits the content's mood:

- **Scroll storytelling**: Pin a section to the viewport and let scroll progress drive internal animations (reveals, transforms, color shifts). Unpin when done, flow to next.
- **Kinetic typography**: Characters or words that animate individually — split, scatter, morph, or respond to scroll/hover. Best for headlines and hero statements.
- **Shader-style effects**: Noise gradients, fluid/smoke backgrounds, image displacement on hover, ripple distortion, dithering/halftone textures, chromatic aberration. These can be achieved with CSS, canvas, or Three.js.
- **Parallax & depth**: Multiple layers scrolling at different speeds. Decorative shapes, background textures, and foreground elements creating spatial depth.
- **3D particles & geometry**: Floating particle fields, geometric meshes, interactive 3D objects that react to cursor or scroll.

> **Avoid overfitting**: These are archetypes, not templates. Contextualize effects to the content's meaning — a portfolio site and a SaaS landing page should feel completely different even if both use scroll animations.

## Interactivity

Design for engagement — users should have plenty to click, hover, and explore:

- Buttons with animated feedback (ripple, scale, color shift)
- Tab groups, accordions, and toggles that reveal content with motion
- Cards and galleries with hover effects (tilt, zoom, overlay reveals)
- Navigation that feels responsive (animated menus, smooth scroll-to-section)
- Modals, drawers, or lightboxes for detail views

The goal: a content-rich, multi-page site where every section invites interaction — not a static poster.

## Performance Guardrails

- Limit simultaneous animating elements to ~8-10 per viewport.
- One heavy shader/3D effect per section — don't stack them.
- Always provide CSS fallbacks for shader effects.
- Text animation levels: character-level for headlines (max ~20 chars), word-level for subheadlines, block-level for body text.

---

## Design Document Format

### Global Design (`/mnt/agents/output/design/design.md`)

**Global design**: color palette, typography (fonts, sizes, weights, letter-spacing), spacing scale, animation style, scroll behavior, cursor style, shared components (Navbar, Footer), dependencies. Include a **Page List** section that names all pages with a one-line description. Include an **Assets** section listing all image/video/SVG assets the site needs (see Asset Manifest below).

### Per-Page Designs

- Write `/mnt/agents/output/design/home.md` — Landing/home page comprehensive design.
- Write `/mnt/agents/output/design/[page].md` for each additional page — named by topic (e.g. `about.md`, `services.md`, `contact.md`). Each covers: layout, elements, text content, entrance animations, scroll behavior, interactions, assets.
- In per-page design files, every section MUST include an **Animation** field specifying what happens on scroll/load/hover with concrete parameters (e.g. "stagger children 0.1s delay, slide up 40px, opacity 0→1, trigger at 20% viewport") — not just "fade in".

---

## Asset Manifest (Design Only — You Do NOT Generate Assets)

In design.md, include an **Assets** section listing every image/video/SVG the website needs. For each asset, specify:
- **Filename** (e.g. `hero-bg.png`, `logo.svg`, `about-team.jpg`)
- **Description** — a detailed prompt describing what the image should look like (style, mood, content, colors). This will be used by the implementation team to generate the asset.
- **Intended location** — which page/section uses it
- **Dimensions** — target resolution and aspect ratio (e.g. `1920×1080 16:9`, `400×400 1:1`)
- **Type** — Image, SVG, or Video

In per-page design files, reference assets by filename (e.g. `/hero-bg.png`). Include detailed descriptions for each asset so the implementation team can generate them accurately.

Not every website needs generated images — skip the Assets section if the design relies purely on typography, icons, gradients, or if the user has provided their own images. Use your judgment.

**Important:** You write the asset manifest only. Asset generation is handled by the Scaffold implementation agent, not by you.

---

## What You Do NOT Do

- Read react-dev.md (that's for implementation agents)
- Decide how to group pages into agent assignments (that's the main agent's job)
- Handle deployment or build configuration
- Generate image assets (that's the Scaffold agent's job — you only define the asset manifest)
