# PRISMA Systematic Review — FMT for Recurrent *C. difficile* (RCTs)

A reproducible, AI-assisted systematic review pipeline following **PRISMA 2020** guidelines.
Identifies, screens, extracts, and synthesizes randomized controlled trials of fecal microbiota
transplantation (FMT) for recurrent / refractory *Clostridioides difficile* infection (rCDI).

Built on [enju](https://github.com/enjuio/enju) — a human-AI collaborative task orchestration
system. The full pipeline runs as a DAG of compute tasks and AI-agent sessions, with explicit
**human review gates** at the screening and uncertainty-resolution stages.

---

## Pipeline Architecture

```
PubMed Search (E-utilities)
        │
        ▼
  Deduplication (PMID / DOI / title)
        │
        ▼
  Abstract Screening ──── screener-agent (Sonnet)
        │
        ▼
  ┌─ Human Review Gate ─┐
  │  approve / revise   │
  └─────────────────────┘
        │
        ├──▶  PRISMA Counts (abstract stage)
        │
        ▼
  Full-text Fetch (PMC via elink + efetch)
        │
        ▼
  Uncertainty Resolution ── resolver-agent (Sonnet)
        │
        ▼
  ┌─ Human Review Gate ─┐
  │  approve / revise   │
  └─────────────────────┘
        │
        ├──▶  Data Extraction ─── extractor-agent (Sonnet)
        │
        ▼
  Final PRISMA Counts + SVG Diagram
        │
        ▼
  Synthesis ─── synthesizer-agent (Sonnet)
        │
        ▼
  data/synthesis.md  +  data/prisma_diagram.svg
```

### Tasks

| Stage | Task ID | Action | Agent / Runner |
|-------|---------|--------|--------------|
| 1 | `search_pubmed` | compute | python:3.12-slim |
| 2 | `deduplicate` | compute | python:3.12-slim |
| 3 | `screen_abstracts` | answer | screener-agent (Sonnet) |
| 4 | `review_screening` | **review** | human |
| 5 | `prisma_counts` | compute | python:3.12-slim |
| 6 | `fetch_fulltext` | compute | python:3.12-slim |
| 7 | `resolve_uncertain` | answer | resolver-agent (Sonnet) |
| 8 | `review_resolution` | **review** | human |
| 9 | `extract_data` | answer | extractor-agent (Sonnet) |
| 10 | `prisma_counts_final` | compute | python:3.12-slim |
| 11 | `prisma_diagram` | compute | python:3.12-slim |
| 12 | `synthesize` | answer | synthesizer-agent (Sonnet) |

---

## Latest Run Findings (2026-05-20)

Search query:
```
("fecal microbiota transplant*" OR "faecal microbiota transplant*" OR FMT) AND
("Clostridioides difficile" OR "Clostridium difficile" OR CDI) AND
(randomized OR randomised OR "randomized controlled trial"[pt])
```
Publication years: 2013–2024. Source: PubMed.

### PRISMA Flow

| Stage | n |
|-------|---|
| Records identified (PubMed) | 220 |
| Records retrieved | 219 |
| Duplicates removed | 2 |
| Records screened | 217 |
| Excluded at abstract screen | 201 |
| Uncertain → full-text review | 3 |
| Resolved include | 1 |
| Resolved exclude | 2 |
| **Total included** | **14 RCTs** |

Internally consistent: 13 confirmed at abstract screen + 1 resolved include = **14**.

### Included Trials

| PMID | Trial | *n* | Comparator | Cure / recurrence result | Follow-up |
|------|-------|-----|------------|--------------------------|-----------|
| [24762631](https://pubmed.ncbi.nlm.nih.gov/24762631/) | Youngster 2014 | 20 | NGT-delivered frozen FMT | 80% colonoscopy, 60% NGT (90% post-retreatment) | 8 weeks |
| [25728808](https://pubmed.ncbi.nlm.nih.gov/25728808/) | Cammarota 2015 | 39 | Vancomycin | FMT 90% vs vanco 26% (P < 0.0001) | 10 weeks |
| [26757463](https://pubmed.ncbi.nlm.nih.gov/26757463/) | Lee 2016 | 232 | Fresh FMT enema | Frozen 83.5% vs fresh 85.1% (per-protocol) | 13 weeks |
| [27547925](https://pubmed.ncbi.nlm.nih.gov/27547925/) | Kelly 2016 | 46 | Autologous FMT | Donor 90.9% vs autologous 62.5% (P = 0.042) | 8 weeks |
| [28011612](https://pubmed.ncbi.nlm.nih.gov/28011612/) | Hota 2017 | 30 | Vancomycin taper | FMT 43.8% vs vanco taper 58.3% (futility-stopped) | 120 days |
| [28220514](https://pubmed.ncbi.nlm.nih.gov/28220514/) | Jiang 2017 | 72 | Frozen / lyophilized FMT | Overall 87%; fresh > lyophilized (P = 0.022) | 2 months |
| [29183074](https://pubmed.ncbi.nlm.nih.gov/29183074/) | Kao 2017 | 116 | Colonoscopy FMT | Capsule 96.2% vs colonoscopy 96.2% (non-inferior) | 12 weeks |
| [29851107](https://pubmed.ncbi.nlm.nih.gov/29851107/) | Ianiro 2018 | 56 | Single FMT + vancomycin | Multiple FMT 100% vs single 75% (P = 0.01) | NR |
| [30388112](https://pubmed.ncbi.nlm.nih.gov/30388112/) | Jiang 2018 | 65 | Frozen FMT by enema | Capsule 84% vs enema 88% no-recurrence (P = 0.76) | 60–90 days |
| [30610862](https://pubmed.ncbi.nlm.nih.gov/30610862/) | Hvas 2019 | 64 | Fidaxomicin; vancomycin | FMT 71% vs fida 33% vs vanco 19% | 8 weeks |
| [31976311](https://pubmed.ncbi.nlm.nih.gov/31976311/) | Garza-González 2019 | 21 | FMT + *Lactobacillus* capsule | Similar efficacy in pilot multicenter RCT | 90 days |
| [33694229](https://pubmed.ncbi.nlm.nih.gov/33694229/) | Rode 2021 | 96 | 12-strain bacteriotherapy; vancomycin | FMT 76% vs vanco 45% vs bact 52% | 90 days |
| [36152636](https://pubmed.ncbi.nlm.nih.gov/36152636/) | Baunwall 2022 (EarlyFMT) | 42 | Placebo | FMT 90% vs placebo 33% (stopped early) | 8 weeks |
| [38501667](https://pubmed.ncbi.nlm.nih.gov/38501667/) | Allegretti 2024 | 61 | FMT + placebo (vs FMT + bezlotoxumab) | No benefit from bezlotoxumab (P = 0.15) | NR |

See `data/synthesis.md` for the full Results + Methods narrative.

---

## What the run demonstrated

This usecase exercises enju's **human review gate** as a first-class primitive in three layered modes:

- **Catching AI failure (earlier Haiku run, different topic).** A Haiku screener emitted 170 decisions for 99 inputs, echoing a prior PoC's documented numbers instead of screening. The human gate caught the decision-count mismatch, issued a precise `request_changes`, and the agent self-corrected into a genuine 99-record screen. The gate catches confabulation in the act.
- **Validating a good screen on an unseen topic (Sonnet, contained Phase-1 slice).** Sonnet-on-FMT, with an explicit no-peeking guardrail, produced 120/120 clean abstract-level decisions. The gate genuinely reviewed and approved. Distinct from the catch-mode demo.
- **Carrying the full pipeline end-to-end (Sonnet, this latest run).** All four agents + six compute tasks + two human gates produced the 14-RCT included set + the publication-quality `synthesis.md` above. No confabulation, internally consistent PRISMA flow, evidence-grounded resolution of uncertains, real published-trial numbers in the synthesis table.

The collaboration mechanism doing real work on a real (unseen) topic is the demonstration — *not* flawless AI.

---

## Honest scope

- **Systems demonstration, not a citable systematic review.** Single run on a single topic, one screener / one resolver / one extractor / one synthesizer. A methodological claim still needs repetition + inter-rater κ across screeners.
- **The synthesis is a working draft, not a publishable manuscript.** `data/synthesis.md` is internally consistent with the extracted data and the PMIDs cite real trials with correct numbers, but a clinical expert would need to editorially review it before publication (clarify endpoint definitions, harmonize follow-up windows, place the trial set in the context of the broader literature, etc.).
- **Single database.** Only PubMed is searched. A production review would add Scopus, Web of Science, and Embase as additional `search_*` tasks feeding into a merged dedup step.
- **No risk-of-bias appraisal.** Production-grade PRISMA reviews include a structured RoB assessment per included trial; that task is not present in this DAG.

---

## What to improve next

- **Inter-rater reliability**: re-run `screen_abstracts` with a different seed and compute Cohen's κ — PRISMA 2020 expects this for AI-assisted screening.
- **Additional databases**: parallel `search_scopus`, `search_wos`, `search_embase` tasks with a merged dedup step.
- **Full-text fallback chain**: for papers not in PMC, try Unpaywall API or DOI resolver before giving up.
- **Structured quality assessment**: add a task scoring each included trial on a risk-of-bias checklist (e.g., Cochrane RoB 2).
- **PROSPERO protocol registration** before any submission attempt.

---

## Running the Pipeline

```bash
# One-time project setup (already done if you cloned the published repo)
enju_create_project(path="/path/to/prisma-review")
enju_set_project_remote(remote_url="git@github.com:tamerh/prisma-review-enju.git")

# Start all four Sonnet agents declared in enju.yaml
enju_agent_start_all(workflow="enju.yaml", project_id=<id>)

# Create a fresh run
enju_create_run(path="enju.yaml", params={
  "search_query": "...",
  "date_from": "2013",
  "date_to": "2024",
  "max_results": 1000
})

# Human tasks: review_screening + review_resolution appear in your inbox.
# Compute tasks run automatically (enju_execute_run); agent tasks are auto-claimed.
```

## Outputs

| File | Description |
|------|-------------|
| `data/raw_records.jsonl` | Raw PubMed records |
| `data/unique_records.jsonl` | After deduplication |
| `data/screening_decisions.jsonl` | Abstract screening decisions (include/exclude/uncertain) |
| `data/resolved_decisions.jsonl` | Full-text decisions for uncertain papers |
| `data/extracted_data.jsonl` | Structured per-trial extraction |
| `data/prisma_counts_final.tsv` | PRISMA 2020 counts at each stage |
| `data/prisma_diagram.svg` | PRISMA 2020 flow diagram |
| `data/synthesis.md` | Included-trials table + Results + Methods narrative |
| `data/fulltext/<pmid>.txt` | Full text for include / uncertain papers |
