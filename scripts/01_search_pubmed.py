#!/usr/bin/env python3
# Stage 1: Search PubMed via E-utilities and write raw records as JSONL.
#
# First-class Python compute script (promoted from 01_search_pubmed.sh —
# the bash wrapper only did mkdir + pip-install-requests + a python
# heredoc). The `requests` dependency is dropped: NCBI E-utilities is
# plain HTTP, so stdlib urllib does it with no in-container pip step.
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

query = os.environ["ENJU_PARAM_search_query"]
date_from = os.environ["ENJU_PARAM_date_from"]
date_to = os.environ["ENJU_PARAM_date_to"]
max_res = int(os.environ["ENJU_PARAM_max_results"])
outdir = os.environ["ENJU_PROJECT_DIR"] + "/data"
os.makedirs(outdir, exist_ok=True)

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _get(url, params, timeout):
    full = url + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(full, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


# Step 1: esearch — get PMIDs
params = {
    "db": "pubmed", "term": query,
    "mindate": date_from, "maxdate": date_to,
    "datetype": "pdat",
    "retmax": max_res, "retmode": "json",
    "usehistory": "y",
}
esearch = json.loads(_get(f"{BASE}/esearch.fcgi", params, timeout=30))["esearchresult"]
pmids = esearch["idlist"]
total_found = int(esearch["count"])
webenv = esearch["webenv"]
query_key = esearch["querykey"]

print(f"Found {total_found} records; retrieving {len(pmids)}", file=sys.stderr)

# Step 2: efetch — fetch abstracts in batches
records = []
batch = 100
for start in range(0, len(pmids), batch):
    time.sleep(0.4)   # NCBI rate limit: 3 req/s without API key
    xml_text = _get(f"{BASE}/efetch.fcgi", {
        "db": "pubmed", "WebEnv": webenv, "query_key": query_key,
        "retstart": start, "retmax": batch,
        "rettype": "abstract", "retmode": "xml",
    }, timeout=60)
    # Parse XML minimally — extract PMID, title, abstract, year, journal
    root = ET.fromstring(xml_text)
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
print("search_pubmed done", file=sys.stderr)
