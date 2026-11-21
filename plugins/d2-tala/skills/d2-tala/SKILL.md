---
name: d2-tala
description: Write or migrate d2 diagrams for the TALA layout engine with hand-pinned top/left positions on a 20px grid, equal box sizes, straight edges and labeled edges, then render and inspect them. Use when creating, editing, polishing or reviewing d2 diagrams (```d2 blocks in Markdown/MDX, .d2 files), when moving diagrams from elk/dagre to tala, or when the user says a diagram looks messy.
---

# d2 diagrams on TALA

Two jobs, same rules:

- **Author**: write a new diagram that follows the rules below.
- **Migrate**: rewrite an existing auto-layout (elk, dagre, plain tala) diagram so every object is pinned.

Keep the meaning of the diagram. Never drop a node, an edge or a label word unless it is a typo or a rule below says so.

## Scope

- `shape: sequence_diagram` blocks are exempt from positioning. Only apply the text and edge rules to them.
- Layout engine is TALA. If the site config (e.g. `astro-d2` `layout: 'tala'`) already sets it, do not add `layout=tala` to the code fence.

## Layout rules

1. Every node and every container gets `top` and `left`. No `grid-columns`, `grid-rows`, `grid-gap` or `direction`. Remove them when migrating.
2. Every `top`, `left`, `width` and `height` is a multiple of 20.
3. Children of a container are positioned relative to the container. The first row starts at `top: 0`, the first column at `left: 0`.
4. TALA adds 60px padding on every side of a container. Do not fight it. A container's outer size is the children's bounding box plus 120 in each axis (title included).
5. Spacing between siblings:
   - 40 between boxes in a row with no edge between them.
   - 60 between rows that an edge crosses. Render, and if anything collides there (label on a node or border, label on label, squeezed arrowhead, bent edge), raise that gap by 20 and render again. Repeat until clean. Raise each gap on its own, not all at once.
   - A horizontal edge with a label gets a gap of at least the label width plus 40.
6. Boxes in the same row share one `height`. Boxes in the same column share one `width`. Size boxes with the formulas below, then take the max per row or column.
7. Straight edges: put connected nodes on one center line. Same center x for vertical edges, same center y for horizontal ones. With equal widths that means equal `left`. A fan-out (one node to many) may bend, but center the single node over the fan.
8. Place containers the same way as nodes, using their outer size from rule 4.

### Box size formulas

Measured for a 16px monospace font (JetBrains Mono). Re-measure for other fonts by rendering a known label.

- width = round up to 20 of `9.6 × longest line in chars + 44`
- height = round up to 20 of `51 + 16 × lines`. Gives 80 for 1 line, 100 for 2 or 3, 120 for 4.
- Shapes need more room than their label, or TALA puts the label outside the shape:
  - cylinder: height 140 for 1 or 2 lines, 160 for 3 lines.
  - diamond: width about 1.6 × the label box. 300×120 for 1 line, 300×140 for 2 lines, 400×220 for 3 lines.

### TALA behavior to plan for

- A diamond has four ports. If more edges enter than free sides exist, TALA draws diagonals. Group the sources into a container with one edge instead (e.g. `Triggers` with one `fires` edge).
- When an edge crosses a container title, TALA moves the title (top-right, bottom, or outside). Accept that if it stays readable, or set `label.near: top-left` when the left side is free.
- A complete bipartite fan (e.g. three sources each linked to the same three targets, K3,3) cannot be drawn without a crossing. Put one source at the side, in the target row, to get down to one crossing.
- Moving a node by 20px can change routing a lot. When an edge takes a detour, try two or three nearby positions and keep the best render.

## Edge rules

1. Every edge has a label, even when several parallel edges repeat the same verb.
2. The label sits mid-edge by default. Move it to `source-arrowhead.label` only when the mid-edge spot collides with a node or another label.
3. A reference that is not a flow (a spec field pointing at another object, "references", "refers to") is undirected and dashed:

   ```d2
   a -- b: {
     style.stroke-dash: 4
     source-arrowhead.label: references
   }
   ```

   Nothing else is dashed. Shapes always keep a solid border.

## Text rules

1. Wrap any node or edge label longer than about 20 chars at a word break with `\n`. Never pad lines with spaces to center them.
2. Every container sets `style.font-size: 24`. Nodes keep the default size.
3. Container labels are the plain text. No `\n(...)` subtitle when a short name says it.
4. Placeholder Kubernetes namespaces (made up for the picture, like "your namespace" or "data") use a `my-` prefix: `my-restore-namespace`, `my-app-namespace`, `my-backup-namespace`. Keep the name when the surrounding text or its commands create or use that namespace (e.g. a walkthrough that runs `kubectl create namespace wordpress`), system namespaces (e.g. `velero`) and generated names (e.g. `bret-scratch-<hash>`). If you rename a placeholder, update the prose that names it.
5. Fix typos.

## Cleanup when migrating

- Remove `direction`, `grid-*`, redundant `layout=` fence attributes and empty lines inside blocks.
- Remove leading or trailing spaces inside labels.
- Keep one style: properties of a block in the order shape, label-related style, `top`, `left`, `width`, `height`, then children, then edges.

## Workflow

1. Read the diagram. List rows and columns, which nodes connect, and the longest line of each label.
2. Compute sizes (formulas), then positions (layout rules). Write the block.
3. Render with `scripts/render.py` and **look at every PNG** with the Read tool:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/render.py OUT_DIR docs/src/content/docs/page.md \
     --vars THEME_VARS.d2 --fonts docs/src/assets/fonts
   ```

   It uses the `d2` binary if on PATH, else the `terrastruct/d2` Docker image, which bundles TALA. TALA is open source now, so no license is needed and renders have no watermark. `--vars` takes d2 text that the site prepends to every block (theme overrides). `--dark` renders the dark theme.
4. Check the PNG for overlapping boxes, labels on top of nodes, bent edges that could be straight, cut-off text and uneven gaps. Fix the numbers and render again until clean.
5. If the docs site builds diagrams (e.g. `npm run build` with astro-d2), run the build once at the end.
