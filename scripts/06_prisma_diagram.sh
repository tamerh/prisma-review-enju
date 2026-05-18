#!/bin/bash
# Phase 3: Generate PRISMA 2020 flow diagram as SVG.
set -euo pipefail

OUTDIR="$ENJU_PROJECT_DIR/data"
mkdir -p "$OUTDIR"

python3 - <<'PYEOF'
import os, csv

outdir = os.environ["ENJU_PROJECT_DIR"] + "/data"

counts = {}
with open(f"{outdir}/prisma_counts_final.tsv") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        counts[row["stage"]] = int(row["count"])

n_id      = counts.get("identified", 0)
n_ret     = counts.get("retrieved", 0)
n_dup     = counts.get("duplicates_removed", 0)
n_scr     = counts.get("screened", 0)
n_exc_abs = counts.get("excluded_abstract", 0)
n_unc     = counts.get("uncertain", 0)
n_ri      = counts.get("resolved_include", 0)
n_re      = counts.get("resolved_exclude", 0)
n_inc_abs = counts.get("total_included", 0) - n_ri
n_total   = counts.get("total_included", 0)

W, H = 720, 780
box_w, box_h = 220, 52
cx = W // 2

def box(x, y, w, h, fill="#ddeeff", stroke="#336699", r=6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'

def text(x, y, lines, size=12, weight="normal", anchor="middle", fill="#222"):
    out = []
    dy = size + 2
    total_h = len(lines) * dy
    start_y = y - total_h / 2 + dy / 2
    for i, line in enumerate(lines):
        out.append(f'<text x="{x}" y="{start_y + i*dy}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}" font-family="Arial,sans-serif">{line}</text>')
    return "\n".join(out)

def arrow(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#555" stroke-width="1.5" marker-end="url(#arr)"/>'

def side_box(x, y, w, h, lines, fill="#fff3cd", stroke="#b8860b"):
    svg = box(x, y, w, h, fill, stroke)
    cy = y + h // 2
    svg += "\n" + text(x + w//2, cy, lines, size=10)
    return svg

# Layout y positions
y_id   = 40
y_ret  = 140
y_scr  = 260
y_unc  = 390
y_res  = 490
y_inc  = 620
y_tot  = 710

svg_parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
    <path d="M0,0 L0,6 L8,3 z" fill="#555"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="white"/>

<!-- Title -->
<text x="{W//2}" y="22" font-size="13" font-weight="bold" text-anchor="middle" fill="#222" font-family="Arial,sans-serif">PRISMA 2020 Flow Diagram</text>
<text x="{W//2}" y="36" font-size="10" text-anchor="middle" fill="#666" font-family="Arial,sans-serif">Nanopore Phage Genomics — Systematic Review</text>
''']

# --- IDENTIFICATION ---
bx = cx - box_w//2
svg_parts.append(box(bx, y_id, box_w, box_h, "#cce5ff", "#0066cc"))
svg_parts.append(text(cx, y_id + box_h//2, [f"Records identified", f"PubMed (n={n_id})"], size=11, weight="bold"))

svg_parts.append(arrow(cx, y_id+box_h, cx, y_ret))

svg_parts.append(box(bx, y_ret, box_w, box_h, "#cce5ff", "#0066cc"))
svg_parts.append(text(cx, y_ret + box_h//2, [f"Records retrieved", f"(n={n_ret})"], size=11))

# Duplicate exclusion side box
svg_parts.append(side_box(cx+box_w//2+10, y_ret, 170, box_h,
    [f"Duplicates removed", f"(n={n_dup})"], "#ffe0cc", "#cc6600"))
svg_parts.append(arrow(cx+box_w//2, y_ret+box_h//2, cx+box_w//2+10, y_ret+box_h//2))

svg_parts.append(arrow(cx, y_ret+box_h, cx, y_scr))

# --- SCREENING ---
svg_parts.append(box(bx, y_scr, box_w, box_h, "#d4edda", "#28a745"))
svg_parts.append(text(cx, y_scr + box_h//2, [f"Records screened", f"(n={n_scr})"], size=11))

# Excluded side box
svg_parts.append(side_box(cx+box_w//2+10, y_scr, 170, box_h,
    [f"Excluded (abstract)", f"(n={n_exc_abs})"], "#f8d7da", "#721c24"))
svg_parts.append(arrow(cx+box_w//2, y_scr+box_h//2, cx+box_w//2+10, y_scr+box_h//2))

svg_parts.append(arrow(cx, y_scr+box_h, cx, y_unc))

# --- UNCERTAIN / FULL TEXT ---
svg_parts.append(box(bx, y_unc, box_w, box_h, "#d4edda", "#28a745"))
svg_parts.append(text(cx, y_unc + box_h//2, [f"Full-text assessed", f"(n={n_unc})"], size=11))

# Excluded at full text
svg_parts.append(side_box(cx+box_w//2+10, y_unc, 170, box_h,
    [f"Excluded (full-text)", f"(n={n_re})"], "#f8d7da", "#721c24"))
svg_parts.append(arrow(cx+box_w//2, y_unc+box_h//2, cx+box_w//2+10, y_unc+box_h//2))

svg_parts.append(arrow(cx, y_unc+box_h, cx, y_res))

# Resolved include
svg_parts.append(box(bx, y_res, box_w, box_h//2+4, "#d4edda", "#28a745"))
svg_parts.append(text(cx, y_res + (box_h//2+4)//2, [f"Resolved include (n={n_ri})"], size=10))

svg_parts.append(arrow(cx, y_res+(box_h//2+4), cx, y_inc))

# --- INCLUDED ---
svg_parts.append(box(bx, y_inc, box_w, box_h, "#c3e6cb", "#155724"))
svg_parts.append(text(cx, y_inc + box_h//2, [f"Included (abstract screen)", f"(n={n_inc_abs})"], size=11))

svg_parts.append(arrow(cx, y_inc+box_h, cx, y_tot))

# Total
svg_parts.append(box(bx, y_tot, box_w, box_h-10, "#155724", "#0d3b1e"))
svg_parts.append(text(cx, y_tot + (box_h-10)//2, [f"Total included", f"n = {n_total}"], size=13, weight="bold", fill="#ffffff"))

svg_parts.append("</svg>")

with open(f"{outdir}/prisma_diagram.svg", "w") as f:
    f.write("\n".join(svg_parts))

print(f"PRISMA diagram written: {outdir}/prisma_diagram.svg", flush=True)
PYEOF

echo "prisma_diagram done" >&2
