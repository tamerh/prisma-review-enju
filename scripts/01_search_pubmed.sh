#!/bin/bash
# Stage 1: Search PubMed via E-utilities and write raw records as JSONL.
set -euo pipefail

OUTDIR="$ENJU_PROJECT_DIR/data"
mkdir -p "$OUTDIR"

pip install requests --quiet --target /tmp/pypackages
export PYTHONPATH="/tmp/pypackages${PYTHONPATH:+:$PYTHONPATH}"

python3 - <<'PYEOF'
import os, json, time, sys
import requests

query     = os.environ["ENJU_PARAM_search_query"]
date_from = os.environ["ENJU_PARAM_date_from"]
date_to   = os.environ["ENJU_PARAM_date_to"]
max_res   = int(os.environ["ENJU_PARAM_max_results"])
outdir    = os.environ["ENJU_PROJECT_DIR"] + "/data"

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Step 1: esearch — get PMIDs
params = {
    "db": "pubmed", "term": query,
    "mindate": date_from, "maxdate": date_to,
    "datetype": "pdat",
    "retmax": max_res, "retmode": "json",
    "usehistory": "y",
}
r = requests.get(f"{BASE}/esearch.fcgi", params=params, timeout=30)
r.raise_for_status()
esearch = r.json()["esearchresult"]
pmids      = esearch["idlist"]
total_found = int(esearch["count"])
webenv     = esearch["webenv"]
query_key  = esearch["querykey"]

print(f"Found {total_found} records; retrieving {len(pmids)}", file=sys.stderr)

# Step 2: efetch — fetch abstracts in batches
records = []
batch = 100
for start in range(0, len(pmids), batch):
    time.sleep(0.4)   # NCBI rate limit: 3 req/s without API key
    r = requests.get(f"{BASE}/efetch.fcgi", params={
        "db": "pubmed", "WebEnv": webenv, "query_key": query_key,
        "retstart": start, "retmax": batch,
        "rettype": "abstract", "retmode": "xml",
    }, timeout=60)
    r.raise_for_status()
    # Parse XML minimally — extract PMID, title, abstract, year, journal
    import xml.etree.ElementTree as ET
    root = ET.fromstring(r.text)
    for art in root.findall(".//PubmedArticle"):
        pmid = art.findtext(".//PMID", "")
        title = art.findtext(".//ArticleTitle", "")
        abstract = " ".join(
            t.text or "" for t in art.findall(".//AbstractText")
        )
        year = art.findtext(".//PubDate/Year") or \
               art.findtext(".//PubDate/MedlineDate", "")[:4]
        journal = art.findtext(".//Journal/Title", "")
        authors_els = art.findall(".//Author")
        authors = []
        for a in authors_els[:3]:
            ln = a.findtext("LastName", "")
            ini = a.findtext("Initials", "")
            if ln:
                authors.append(f"{ln} {ini}".strip())
        doi_el = art.find(".//ArticleId[@IdType='doi']")
        doi = doi_el.text if doi_el is not None else ""
        records.append({
            "pmid": pmid, "title": title, "abstract": abstract,
            "year": year, "journal": journal,
            "authors": authors, "doi": doi,
        })

with open(f"{outdir}/raw_records.jsonl", "w") as f:
    for rec in records:
        f.write(json.dumps(rec) + "\n")

with open(f"{outdir}/search_stats.tsv", "w") as f:
    f.write("stage\tcount\n")
    f.write(f"pubmed_search_total\t{total_found}\n")
    f.write(f"pubmed_retrieved\t{len(records)}\n")

print(f"Wrote {len(records)} records to raw_records.jsonl", file=sys.stderr)
PYEOF

echo "search_pubmed done" >&2
