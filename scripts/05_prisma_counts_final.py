#!/usr/bin/env python3
# Phase 2, Stage 4: Final PRISMA counts after uncertainty resolution.
#
# First-class Python compute script (promoted from
# 05_prisma_counts_final.sh — bash wrapper only set OUTDIR + python
# heredoc; stdlib only).
import json
import os

outdir = os.environ["ENJU_PROJECT_DIR"] + "/data"
os.makedirs(outdir, exist_ok=True)


def read_tsv(path):
    rows = {}
    with open(path) as f:
        next(f)
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                rows[parts[0]] = int(parts[1])
    return rows


search = read_tsv(f"{outdir}/search_stats.tsv")
dedup = read_tsv(f"{outdir}/dedup_stats.tsv")

# Abstract screening
abstract = {"include": 0, "exclude": 0, "uncertain": 0}
with open(f"{outdir}/screening_decisions.jsonl") as f:
    for line in f:
        line = line.strip()
        if line:
            d = json.loads(line)
            abstract[d.get("decision", "uncertain")] += 1

# Uncertainty resolution
resolved = {"include": 0, "exclude": 0}
try:
    with open(f"{outdir}/resolved_decisions.jsonl") as f:
        for line in f:
            line = line.strip()
            if line:
                d = json.loads(line)
                resolved[d.get("decision", "exclude")] += 1
except FileNotFoundError:
    pass

total_included = abstract["include"] + resolved["include"]

n_identified = search.get("pubmed_search_total", 0)
n_retrieved = search.get("pubmed_retrieved", 0)
n_dupes = dedup.get("duplicates_removed", 0)
n_screened = dedup.get("after_title_dedup", 0)

flow = f"""
PRISMA 2020 Flow Diagram (Final)
════════════════════════════════════════

IDENTIFICATION
  Records identified via PubMed:         {n_identified:>5}
  Records retrieved (cap):               {n_retrieved:>5}

SCREENING
  Duplicates removed:                    {n_dupes:>5}
  Records screened (title/abstract):     {n_screened:>5}
    └─ Excluded at abstract screen:      {abstract['exclude']:>5}
    └─ Uncertain → full-text review:     {abstract['uncertain']:>5}
        └─ Resolved include:             {resolved['include']:>5}
        └─ Resolved exclude:             {resolved['exclude']:>5}

INCLUDED
  Confirmed at abstract screen:          {abstract['include']:>5}
  Added after full-text review:          {resolved['include']:>5}
  ─────────────────────────────────────────────
  Total included:                        {total_included:>5}

════════════════════════════════════════
"""

print(flow)

with open(f"{outdir}/prisma_flow_final.txt", "w") as f:
    f.write(flow)

with open(f"{outdir}/prisma_counts_final.tsv", "w") as f:
    f.write("stage\tcount\n")
    for k, v in [
        ("identified", n_identified), ("retrieved", n_retrieved),
        ("duplicates_removed", n_dupes), ("screened", n_screened),
        ("excluded_abstract", abstract["exclude"]),
        ("uncertain", abstract["uncertain"]),
        ("resolved_include", resolved["include"]),
        ("resolved_exclude", resolved["exclude"]),
        ("total_included", total_included),
    ]:
        f.write(f"{k}\t{v}\n")

print("prisma_counts_final done", flush=True)
