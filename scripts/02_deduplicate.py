#!/usr/bin/env python3
# Stage 2: Remove duplicates by PMID, then by DOI, then by title similarity.
#
# First-class Python compute script (promoted from 02_deduplicate.sh —
# the bash wrapper only set OUTDIR and ran a python heredoc; stdlib only).
import json
import os
import re

outdir = os.environ["ENJU_PROJECT_DIR"] + "/data"
os.makedirs(outdir, exist_ok=True)

records = []
with open(f"{outdir}/raw_records.jsonl") as f:
    for line in f:
        line = line.strip()
        if line:
            records.append(json.loads(line))

n_raw = len(records)

# Deduplicate by PMID (primary key — should be unique but guard anyway)
seen_pmids = set()
by_pmid = []
for r in records:
    if r["pmid"] and r["pmid"] not in seen_pmids:
        seen_pmids.add(r["pmid"])
        by_pmid.append(r)
n_after_pmid = len(by_pmid)

# Deduplicate by DOI (catches cross-database duplicates)
seen_dois = set()
by_doi = []
for r in by_pmid:
    doi = r.get("doi", "").strip().lower()
    if doi and doi in seen_dois:
        continue
    if doi:
        seen_dois.add(doi)
    by_doi.append(r)
n_after_doi = len(by_doi)


# Light title-based dedup: normalize and compare
def normalize(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


seen_titles = set()
unique = []
for r in by_doi:
    nt = normalize(r.get("title", ""))
    if nt and nt in seen_titles:
        continue
    if nt:
        seen_titles.add(nt)
    unique.append(r)
n_unique = len(unique)

with open(f"{outdir}/unique_records.jsonl", "w") as f:
    for r in unique:
        f.write(json.dumps(r) + "\n")

# Append dedup stats to search_stats.tsv
with open(f"{outdir}/dedup_stats.tsv", "w") as f:
    f.write("stage\tcount\n")
    f.write(f"after_pmid_dedup\t{n_after_pmid}\n")
    f.write(f"after_doi_dedup\t{n_after_doi}\n")
    f.write(f"after_title_dedup\t{n_unique}\n")
    f.write(f"duplicates_removed\t{n_raw - n_unique}\n")

print(f"Dedup: {n_raw} → {n_unique} unique records ({n_raw - n_unique} removed)", flush=True)
print("deduplicate done", flush=True)
