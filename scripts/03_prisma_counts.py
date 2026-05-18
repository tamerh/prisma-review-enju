#!/usr/bin/env python3
# Stage 5: Compute PRISMA 2020 flow counts and render a text flow diagram.
#
# First-class Python compute script (promoted from 03_prisma_counts.sh —
# the bash wrapper only set OUTDIR and ran a python heredoc; stdlib only).
import json
import os

outdir = os.environ["ENJU_PROJECT_DIR"] + "/data"
os.makedirs(outdir, exist_ok=True)


def read_tsv(path):
    rows = {}
    with open(path) as f:
        next(f)  # header
        for line in f:
            k, v = line.strip().split("\t")
            rows[k] = int(v)
    return rows


search = read_tsv(f"{outdir}/search_stats.tsv")
dedup = read_tsv(f"{outdir}/dedup_stats.tsv")

decisions = {"include": 0, "exclude": 0, "uncertain": 0}
with open(f"{outdir}/screening_decisions.jsonl") as f:
    for line in f:
        line = line.strip()
        if line:
            d = json.loads(line)
            decisions[d.get("decision", "uncertain")] += 1

n_identified = search.get("pubmed_search_total", 0)
n_retrieved = search.get("pubmed_retrieved", 0)
n_unique = dedup.get("after_title_dedup", 0)
n_duplicates = dedup.get("duplicates_removed", 0)
n_screened = n_unique
n_excluded = decisions["exclude"]
n_uncertain = decisions["uncertain"]
n_included = decisions["include"]

counts = [
    ("identified",        n_identified),
    ("retrieved",         n_retrieved),
    ("duplicates_removed", n_duplicates),
    ("screened",          n_screened),
    ("excluded_abstract", n_excluded),
    ("uncertain",         n_uncertain),
    ("included_abstract", n_included),
]

with open(f"{outdir}/prisma_counts.tsv", "w") as f:
    f.write("stage\tcount\n")
    for k, v in counts:
        f.write(f"{k}\t{v}\n")

flow = f"""
PRISMA 2020 Flow Diagram
════════════════════════════════════════

IDENTIFICATION
  Records identified via PubMed:       {n_identified:>5}
  Records retrieved (cap):             {n_retrieved:>5}

SCREENING
  Duplicates removed:                  {n_duplicates:>5}
  Records screened (title/abstract):   {n_screened:>5}
    └─ Excluded:                       {n_excluded:>5}
    └─ Uncertain (→ human review):     {n_uncertain:>5}

INCLUDED
  Records included after abstract screen: {n_included:>4}

════════════════════════════════════════
"""

with open(f"{outdir}/prisma_flow.txt", "w") as f:
    f.write(flow)

print(flow)
print("prisma_counts done", flush=True)
