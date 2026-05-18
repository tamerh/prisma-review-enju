#!/usr/bin/env python3
# Phase 2, Stage 1: Fetch PMC full text for included + uncertain papers.
# Uses NCBI elink (PMID → PMCID) then efetch XML.
#
# First-class Python compute script (promoted from 04_fetch_fulltext.sh —
# the bash wrapper did mkdir + pip-install-requests + a python heredoc).
# `requests` dropped for stdlib urllib (plain HTTP); urlopen raises
# HTTPError on non-2xx, exactly as requests' raise_for_status did, so the
# retry/fallback control flow is preserved 1:1.
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

outdir = os.environ["ENJU_PROJECT_DIR"] + "/data"
os.makedirs(f"{outdir}/fulltext", exist_ok=True)
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def get_with_retry(url, params, timeout=30, retries=3):
    full = url + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(full, timeout=timeout) as resp:
                return resp.read().decode("utf-8", "replace")
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt
            print(f"  retry {attempt+1} after {wait}s: {e}", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError("unreachable")


# Collect PMIDs to fetch: include + uncertain
pmids = []
with open(f"{outdir}/screening_decisions.jsonl") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r["decision"] in ("include", "uncertain"):
            pmids.append(r["pmid"])

print(f"Fetching full text for {len(pmids)} papers (include + uncertain)", file=sys.stderr)

fetched, missing = [], []
for pmid in pmids:
    time.sleep(0.35)
    # Try to get PMCID via elink
    try:
        body = get_with_retry(f"{BASE}/elink.fcgi", params={
            "dbfrom": "pubmed", "db": "pmc",
            "id": pmid, "retmode": "json",
        }, timeout=20)
        links = json.loads(body).get("linksets", [{}])[0].get("linksetdbs", [])
    except Exception:
        links = []
    pmcid = None
    for db in links:
        if db.get("dbto") == "pmc":
            ids = db.get("links", [])
            if ids:
                pmcid = ids[0]
                break

    if not pmcid:
        missing.append(pmid)
        # Fall back to abstract only
        try:
            text = get_with_retry(f"{BASE}/efetch.fcgi", params={
                "db": "pubmed", "id": pmid,
                "rettype": "abstract", "retmode": "text",
            }, timeout=20).strip()
        except Exception:
            text = ""
        with open(f"{outdir}/fulltext/{pmid}.txt", "w") as f:
            f.write(f"[ABSTRACT ONLY — no PMC full text]\n\n{text}")
        continue

    # Fetch PMC full text XML
    time.sleep(0.35)
    try:
        body = get_with_retry(f"{BASE}/efetch.fcgi", params={
            "db": "pmc", "id": pmcid,
            "rettype": "full", "retmode": "xml",
        }, timeout=60)
    except Exception:
        missing.append(pmid)
        continue

    # Extract readable text from XML (methods + results sections)
    try:
        root = ET.fromstring(body)
        parts = []
        title = root.findtext(".//article-title", "")
        if title:
            parts.append(f"TITLE: {title}\n")
        for sec in root.findall(".//sec"):
            heading = sec.findtext("title", "")
            sec_body = " ".join(p.text or "" for p in sec.findall(".//p") if p.text)
            if sec_body:
                parts.append(f"\n[{heading.upper()}]\n{sec_body}")
        text = "\n".join(parts)[:8000]  # cap at 8k chars
    except ET.ParseError:
        text = body[:8000]

    with open(f"{outdir}/fulltext/{pmid}.txt", "w") as f:
        f.write(text)
    fetched.append(pmid)

# Write manifest
with open(f"{outdir}/fulltext_manifest.tsv", "w") as f:
    f.write("pmid\tstatus\n")
    for p in fetched:
        f.write(f"{p}\tfull_text\n")
    for p in missing:
        f.write(f"{p}\tabstract_only\n")

print(f"Full text: {len(fetched)} fetched, {len(missing)} abstract-only", file=sys.stderr)
print("fetch_fulltext done", file=sys.stderr)
