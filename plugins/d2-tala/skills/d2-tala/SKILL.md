---
name: d2-tala
description: Write, migrate or review d2 diagrams for TALA. Pins `top`/`left` on a 20px grid, equal boxes, straight labeled edges, then renders and checks. Use for `d2` blocks in Markdown/MDX, `.d2` files, `elk`/`dagre` to `tala` moves, or messy diagrams.
---

# d2 diagrams on TALA

- **Author**: write a new diagram by these rules.
- **Migrate**: rewrite an auto-layout (elk, dagre, plain tala) diagram so every object is pinned.

Keep the meaning. Never drop a node, edge or label word unless it is a typo or a rule says so.

## Scope

- `shape: sequence_diagram` blocks get no positions, only the text and edge rules.
- If the site config already sets TALA (e.g. `astro-d2` `layout: 'tala'`), add no `layout=tala` to the fence.

## Layout

1. Every node and container gets `top` and `left`. No `grid-columns`, `grid-rows`, `grid-gap` or `direction`.
2. Every `top`, `left`, `width` and `height` is a multiple of 20.
3. Children sit relative to their container. First row at `top: 0`, first column at `left: 0`.
4. TALA pads containers by 60 on every side. Don't fight it. Outer size = children's bounding box + 120 per axis (title included).
5. Gaps between siblings:
   - 40 between boxes in a row with no edge between them.
   - 60 between rows an edge crosses. On a collision there (label on node, border or label, squeezed arrowhead, bent edge), raise that one gap by 20 and render again until clean.
   - A horizontal labeled edge gets at least label width + 40.
6. Boxes in the same row share one `height`. Boxes in the same column share one `width`. Size boxes with the formulas below, then take the max per row or column.
7. Straight edges: connected nodes share a center line (x for vertical, y for horizontal edges). With equal widths that means equal `left`. A fan-out (one node to many) may bend, but center the single node over the fan.
8. Place containers like nodes, by their outer size.

### Box sizes

Measured for a 16px monospace font (JetBrains Mono). Re-measure for other fonts by rendering a known label.

- width = round up to 20 of `9.6 × longest line in chars + 44`
- height = round up to 20 of `51 + 16 × lines`. Gives 80 for 1 line, 100 for 2 or 3, 120 for 4.
- Shapes need more room than their label, or TALA puts the label outside the shape:
  - cylinder: height 140 for 1 or 2 lines, 160 for 3 lines.
  - diamond: width about 1.6 × the label box. 300×120 for 1 line, 300×140 for 2 lines, 400×220 for 3 lines.

### TALA quirks

- A diamond has four ports. More incoming edges than free sides give diagonals. Group the sources in a container with one edge (e.g. `Triggers` with one `fires` edge).
- An edge crossing a container title moves the title (top-right, bottom or outside). Accept it if readable, or set `label.near: top-left` when the left side is free.
- A full bipartite fan (K3,3: three sources each linked to the same three targets) always crosses. Put one source at the side in the target row to get one crossing.
- A 20px move can change routing a lot. On a detour, try two or three nearby positions and keep the best render.

## IDs

1. Meaningful camelCase that names the thing: `replicationSource`, `backupStorage`. Never cryptic IDs like `rs`, `rS`, `a`, `b` or `n1`.
2. Full words by default. Shorten only long IDs, with common clear short forms (`repl`, `src`, `dst`, `ns`, `db`, `config`), e.g. `replSource`.
3. Every node and container sets a label, so no ID shows in the picture:

   ```d2
   replSource: "ReplicationSource" {
     top: 0
     left: 0
   }
   ```

## Edges

1. Every edge has a label, even parallel edges with the same verb.
2. Labels sit mid-edge. Use `source-arrowhead.label` only when mid-edge collides with a node or label.
3. A reference that is not a flow (a spec field pointing at another object, "references", "refers to") is undirected and dashed. Nothing else is dashed, and shapes keep a solid border:

   ```d2
   restore -- backup: {
     style.stroke-dash: 4
     source-arrowhead.label: "references"
   }
   ```

## Text

1. Wrap node and edge labels over about 20 chars at a word break with `\n`. Never pad lines with spaces to center them.
2. Containers set `style.font-size: 24`. Nodes keep the default.
3. Container labels are plain text, no `\n(...)` subtitle when a short name says it.
4. Double quote every label (node, container, edge, arrowhead): `replSource -> backupStorage: "uploads to"`.
5. Placeholder Kubernetes namespaces (made up for the picture, like "your namespace" or "data") get a `my-` prefix: `my-restore-namespace`, `my-app-namespace`, `my-backup-namespace`. Keep names that the surrounding text or its commands create or use (e.g. `kubectl create namespace wordpress`), system namespaces (`velero`) and generated names (`bret-scratch-<hash>`). After a rename, update the prose too.
6. Fix typos.

## Migration cleanup

- Remove `direction`, `grid-*`, redundant `layout=` fence attributes and empty lines inside blocks.
- Trim spaces at label ends.
- Rename cryptic IDs and update every edge and reference to them in the block. Add missing quoted labels and quote bare ones.
- Order block properties: shape, label style, `top`, `left`, `width`, `height`, children, edges.

## Workflow

1. Read the diagram. List rows, columns, connections and each label's longest line.
2. Compute sizes, then positions. Write the block.
3. Render and **look at every PNG** with the Read tool:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/render.py OUT_DIR docs/src/content/docs/page.md \
     --vars THEME_VARS.d2 --fonts docs/src/assets/fonts
   ```

   Uses `d2` from PATH, else the `terrastruct/d2` Docker image (bundles TALA). TALA is open source: no license, no watermark. `--vars` takes d2 text the site prepends to every block (theme overrides). `--dark` renders the dark theme.
4. Check for overlapping boxes, labels on nodes, bent edges that could be straight, cut-off text and uneven gaps. Fix the numbers and render again until clean.
5. If the docs site builds diagrams (e.g. `npm run build` with astro-d2), run the build once at the end.
