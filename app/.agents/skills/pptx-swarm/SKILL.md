---
name: pptx-swarm
description:  Exclusive skill for all PPT/presentation-related tasks. Any requests involving PowerPoint, PPT, PPTX, slides or presentations must be processed using this skill, including but not limited to: creating, generating, editing, modifying, redesigning, typesetting, beautifying or converting presentations, as well as modifying user-uploaded .pptx files.\nImportant Note:\nPresentations must be created using the PPTD domain-specific language (.pptd/.page) provided by this skill. Strictly prohibited from directly creating, editing or generating .pptx files using python-pptx, OpenXML SDK, or any other libraries/methods.\nNotice:\nThe main agent must complete visual design, outline design, and .pptd file construction. Sub-agents may only generate .page files. Before the .pptd file is generated, strictly prohibited from assigning production tasks to sub-agents using create_subagent or task-related tools!
---

# Definition
The pptx skill is responsible for generating, creating, or editing PPTX presentations. This skill defines an intermediate layer (with the .pptd extension) that further abstracts OOXML, making presentation generation effortless.

# .pptd Format
- The .pptd format is a simplified abstraction layer over OOXML, based on YAML syntax, designed specifically for AI to read and write presentations. This abstraction retains the core content of OOXML (themes, page layouts, element positions and definitions, etc.) while removing complex nested logic such as Masters, making each page self-contained and WYSIWYG.
- User usage: In the frontend, users can directly open .pptd files for preview, or click the "Export" button to convert .pptd to .pptx. Converting .pptx or .pptd files to images for preview purposes is strictly prohibited.
- Read format/pptd.md for the detailed definition of the .pptd format.

# Reading User-Uploaded PPTs
If you only want to read a PPT and loaded this skill by mistake, you can read user-uploaded .pptx files through the following three methods to obtain different levels of information:
1. read_file tool: Parses the .pptx file into markdown text, suitable for quickly obtaining the text content and basic structure of the PPT.
2. screenshot script: Generates screenshots of .pptx pages, suitable for obtaining the visual design and layout information of the PPT.
```bash
scripts/screenshot.sh path/input.pptx -o screenshot/

# You can also specify page numbers:
scripts/screenshot.sh path/input.pptx -p 1,3,5 -o screenshot/

# Or specify a page range:
scripts/screenshot.sh path/input.pptx -p 2-6 -o screenshot/
```
3. convert script: Converts .pptx to .pptd file format, obtaining complete information about the .pptx file, such as page notes and layouts, element positions, sizes, content, settings, etc. Suitable for editing user-uploaded .pptx files or when you need an in-depth understanding of the .pptx file structure.
```bash
scripts/convert.sh input.pptx -o output_dir/
```
- Methods listed later provide more detailed information, but also consume more context. You need to decide how to read the PPT based on the actual situation.

# PPTX Presentation Generation
When the user requests: creating a PPT / converting a document to PPT / replicating an image or website as a PPT / using an uploaded .pptx as a template / creating a PPT referencing a PPT style, read guideline/generate_slides.md for more guidance.

# Editing User-Uploaded PPTX Presentations
When the user requests modifying an uploaded PPT, read guideline/edit_user_slides.md for more guidance.

# Skill File Tree

```
pptx-swarm/
├── SKILL.md                        ← This file (skill entry point)
├── format/                         → PPTD format specification
│   ├── pptd.md                     → PPTD full specification
│   ├── shapes.md                   → Complete shape list
│   └── fonts.md                    → Available font list
├── guideline/                      → Workflow guidelines
│   ├── generate_slides.md          → Presentation generation
│   ├── edit_user_slides.md         → Editing user-uploaded PPTX
│   ├── content/                    → Content design modes
│   │   ├── outline_mode.md         → Outline mode
│   │   ├── summary_mode.md         → Summary mode
│   │   └── search_mode.md          → Search mode
│   ├── design/                     → Visual design modes
│   │   ├── creative_mode.md        → Creative mode
│   │   ├── reference_mode.md       → Reference/replication mode
│   │   ├── template_mode.md        → Template mode
│   │   ├── template/               → Preset template files
│   │   └── profiles/               → Scene style presets
│   ├── subagent/                   → Sub-agent guidelines
│   │   ├── attention.md            → Sub-agent notes
│   │   ├── search_writing.md       → Search writing guide
│   │   └── summary_writing.md      → Summary writing guide
│   └── search/                     → Search guidelines
│       └── text_search.md          → Information search
└── scripts/                        → Scripts and source code
    ├── convert.sh                  → PPTD/PPTX conversion script
    ├── check.sh                    → PPTD checker (format validation + overflow/occlusion detection)
    └── screenshot.sh               → PPTX screenshot script
```

# ATTENTION

## YAML Quoting Rules (Must Follow)
- The `content.text` field **must use block scalar (`|`)** and must not be wrapped with `"` or `'`, otherwise double quotes in HTML attributes (e.g., `style="..."`) will cause YAML parsing errors.
- For other fields, if the value contains special characters such as `:`, `#`, `{`, `}`, wrap them with quotes or use block scalar.

## Basic Guidelines
1. Scope of operations: Directly operating on .pptx files is strictly prohibited. All your operations should apply to .pptd files, and you are also prohibited from converting .pptd files to .pptx files. Users who need .pptx files should convert .pptd to .pptx themselves by clicking the "Export" button in the frontend.
2. Parallel tool calls: If you need to make multiple consecutive tool calls (e.g., generating multiple .page files in sequence; making multiple edit tool calls to modify different locations in the same file, etc.), you should make multiple parallel tool calls in a single output, rather than making separate thinking-toolcall, thinking-toolcall rounds. This avoids context redundancy caused by multiple rounds of output.
3. When the user requests creating multiple presentations, **you must adopt a generate-all-first, then check-one-by-one strategy!** That is: serially complete the creation or modification of each PPT (including .page files and .pptd files), and only proceed to unified checking, fixing, and delivery after all presentations are created. **Never complete one PPT and immediately check, fix, and deliver it before creating the next PPT**.
