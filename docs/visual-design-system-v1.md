# Workforce Wonkery Visual Design System

Status: Canonical as of 2026-09-27

## Source of truth

The owner-approved Workforce Wonkery homepage is the visual anchor for the whole site.

The durable implementation is:
- wordpress/templates/homepage-editorial.html
- homepage version: editorial-20260926
- approved implementation blob: 0b46c8fd85607d66ae0a8218afeacedf8ce76344
- documented reference: docs/homepage-golden-master.md

Figma remains useful for exploration and prototyping, but it is secondary to the approved homepage direction. GitHub remains the code and governance source of truth. WordPress remains the public publishing layer.

## Design intent

The site should feel like a California workforce intelligence publication, not a software dashboard.

The design language is:
- editorial
- warm
- evidence-led
- calm
- information-rich without feeling crowded
- professional without becoming institutional
- distinctive without decorative excess

The brand promise is expressed through hierarchy: Policy. Data. Practice. Decoded.

## Core visual tokens

Use the homepage values as the default starting point.

### Color
- Paper: #fcfaf6
- Ink: #111d20
- Muted text: #4d5558
- Gold: #d49b25
- Gold dark: #986714
- Policy: #8d2437
- Data: #075f70
- Practice: #365d36
- Hairline: #dedbd3
- Focus outline: #185cac

Semantic accents should remain restrained. Policy, Data, and Practice are parts of one publication, not separate brands.

### Typography
- Editorial/display serif: Georgia, "Times New Roman", serif
- Utility sans: Arial, Helvetica, sans-serif

Use serif type for major headings, important labels, narrative emphasis, and primary calls to action. Use sans serif for utility text, controls, small labels, metadata, and dense supporting copy.

Headings should be bold, compact, and slightly tight in tracking. Eyebrows should be small, uppercase, letter-spaced, and used sparingly.

### Spacing and width
Default spacing rhythm:
8, 16, 24, 32, 48, 64, 96

Homepage content width:
- approximately calc(100% - 112px)
- max width 1320px
- responsive reductions at smaller breakpoints

Use generous section spacing, but keep related information visually close.

## Signature patterns

### Editorial hierarchy
Start with meaning before navigation or controls. A reader should understand what the page is for before encountering dense detail.

### Section introductions
Prefer:
- short eyebrow
- strong serif heading
- one concise explanatory paragraph
- one clear next action when useful

### Buttons
Primary actions use the gold rounded pill treatment. Secondary actions should be visually quieter and should not compete with the primary action.

### Rules and borders
Use thin hairlines to organize information. Avoid heavy boxes unless a container has a real structural purpose.

### Cards
Cards are allowed when items are genuinely parallel, such as policy priorities. Do not turn every section into a card grid.

### Data presentation
Lead with the story or decision. Show a small set of meaningful signals first. Put technical detail, methodology, and deeper evidence behind clear secondary paths.

### Images
Use California place-based imagery selectively. Images should reinforce identity or context, not fill empty space. Avoid generic corporate or AI stock imagery.

### Interaction
Controls should feel quiet and editorial. Keep visible focus, keyboard access, reduced-motion support, useful empty states, and responsive behavior.

## Page adaptation rules

The homepage is a design anchor, not a page template to copy literally.

### Policy
Emphasize timeliness, identifiers, consequences, and next steps. Burgundy is the primary semantic accent.

### Data
Emphasize interpretation before tools. Teal is the primary semantic accent. Prefer stories, signals, guided paths, and progressive disclosure over dashboard density. The approved section hero uses the shared editorial hierarchy: a short eyebrow, `Data Decoded.` as the primary serif headline, gold emphasis on `Decoded.`, and a concise serif deck. This is a sibling treatment to `Policy Decoded.` rather than a separate Data-specific display style.

### Practice
Emphasize learning, examples, and action. Green is the primary semantic accent. Organize resources around what a practitioner is trying to do. The approved section hero uses the shared editorial hierarchy: a short eyebrow, `Practice Decoded.` as the primary serif headline, gold emphasis on `Decoded.`, and a concise serif deck. This is a sibling treatment to `Policy Decoded.` and `Data Decoded.`.

### Reports
Use the editorial publication language most strongly: large serif hierarchy, restrained supporting metadata, and clear reading paths.

### Tools and explorers
Use the same visual system while giving controls enough structure to work. Do not let filters and selectors turn the page into a generic application shell.

## Anti-patterns

Do not introduce:
- generic SaaS visual language
- excessive gradients
- glassmorphism
- oversized rounded cards everywhere
- decorative AI imagery
- unnecessary animation
- multiple competing primary buttons
- dense control chrome before the reader understands the page
- a new typeface or palette without owner approval
- one-off styling that cannot be reused

## AI implementation protocol

For routine page work, do not begin with a new design exploration.

1. Read docs/homepage-golden-master.md.
2. Inspect the target page.
3. Reuse the homepage tokens and closest relevant patterns.
4. Make only the changes needed for the target page's purpose.
5. Preserve functionality and governed content.
6. Preview in Vercel when appropriate.
7. Run qa/visual-consistency-gate.md plus the normal acceptance checks.
8. Record intentional deviations.

Escalate to a new design exploration only when the existing visual system cannot solve the page's problem or the owner explicitly asks for a new direction.

## Governance

Reader-facing visual changes remain subject to existing Review, publication, owner-decision, accessibility, evidence, and safety gates.

A successful build is not publication approval.
