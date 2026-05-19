# PRISMA Systematic Review — Nanopore Phage Genomics

A reproducible, AI-assisted systematic review pipeline following **PRISMA 2020** guidelines.
Identifies, screens, and synthesizes studies that use Oxford Nanopore Technology (ONT)
for bacteriophage genome assembly and characterization.

Built on [enju](https://github.com/enjuio/enju) — a human-AI collaborative task orchestration
system. The full pipeline runs as a DAG of compute tasks and AI bot sessions, with human
review gates at key decision points.

---

## Pipeline Architecture

```
PubMed Search (E-utilities)
        │
        ▼
  Deduplication (PMID / DOI / title)
        │
        ▼
  Abstract Screening ──── screener-bot (Haiku)
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
  Uncertainty Resolution ── resolver-bot (Haiku)
        │
        ▼
  ┌─ Human Review Gate ─┐
  │  approve / revise   │
  └─────────────────────┘
        │
        ├──▶  Data Extraction ─── extractor-bot (Sonnet*)
        │
        ▼
  Final PRISMA Counts + SVG Diagram
        │
        ▼
  Synthesis ─── synthesizer-bot (Sonnet*)
        │
        ▼
  data/synthesis.md  +  data/prisma_diagram.svg
```

_\* PoC run used Haiku throughout. Switch to Sonnet/Opus for production._

### Tasks

| Stage | Task ID | Action | Bot / Runner |
|-------|---------|--------|--------------|
| 1 | `search_pubmed` | compute | python:3.12-slim |
| 2 | `deduplicate` | compute | python:3.12-slim |
| 3 | `screen_abstracts` | answer | screener-bot (Haiku) |
| 4 | `review_screening` | **review** | human (tamer) |
| 5 | `prisma_counts` | compute | python:3.12-slim |
| 6 | `fetch_fulltext` | compute | python:3.12-slim |
| 7 | `resolve_uncertain` | answer | resolver-bot (Haiku) |
| 8 | `review_resolution` | **review** | human (tamer) |
| 9 | `extract_data` | answer | extractor-bot (Sonnet) |
| 10 | `prisma_counts_final` | compute | python:3.12-slim |
| 11 | `prisma_diagram` | compute | python:3.12-slim |
| 12 | `synthesize` | answer | synthesizer-bot (Sonnet) |

---

## Proof-of-Concept Findings

Search query:
```
("nanopore" OR "Oxford Nanopore" OR "MinION" OR "long-read") AND
("bacteriophage" OR "phage") AND
("genome" OR "sequencing" OR "assembly" OR "characterization")
```
Publication years: 2018–2024. Source: PubMed.

### PRISMA Flow

| Stage | n |
|-------|---|
| Records identified (PubMed) | 172 |
| After deduplication | 170 |
| Excluded at abstract screen | 145 |
| Sent to full-text review (uncertain) | 21 |
| Excluded after full-text review | 20 |
| **Total included** | **5 papers / 6 phage genomes** |

### Included Studies

| PMID | Phage | Host | Genome (bp) | Topology | Assembler | Hybrid | Completeness |
|------|-------|------|-------------|----------|-----------|--------|--------------|
| [38360595](https://pubmed.ncbi.nlm.nih.gov/38360595/) | VB_ST_E15 | *Salmonella enterica* | 39,907 | Circular | Flye + Medaka | Yes | Complete |
| [38360595](https://pubmed.ncbi.nlm.nih.gov/38360595/) | VB_ST_SPNIS2 | *Salmonella enterica* | 38,726 | Circular | Flye + Medaka | Yes | Complete |
| [36779715](https://pubmed.ncbi.nlm.nih.gov/36779715/) | Fyn8 | *Pseudomonas aeruginosa* | 45,617 | Circular | Flye + Medaka | No | Complete |
| [34772986](https://pubmed.ncbi.nlm.nih.gov/34772986/) | 2019SD1 | *Shigella dysenteriae* | 53,145 | Circular | Canu | No | Complete |
| [34197460](https://pubmed.ncbi.nlm.nih.gov/34197460/) | WOSoc | *Wolbachia* | 55,288 | Linear | Canu | Yes | Draft |
| [38847506](https://pubmed.ncbi.nlm.nih.gov/38847506/) | — | — | 98,572 | — | — | Yes | Complete |

**Key patterns:**
- Flye is the dominant assembler (3/5 papers), Canu used in 2
- Medaka polishing applied in hybrid ONT+Illumina workflows
- Genome sizes span 38.7 kb → 98.6 kb
- 4/5 papers report circular topology (consistent with typical dsDNA phages)
- Hybrid sequencing (ONT + Illumina) used in 3/5 papers — pure ONT in 2

---

## Iteration — Contained Phase-1 Re-run (2026-05-18)

A trimmed verification slice (`enju.trim.yaml`: search → dedup →
abstract screen → human review gate → PRISMA counts; the full-text /
extraction / synthesis tail intentionally dropped) run on Haiku with
`max_results: 50`. Purpose: exercise the pipeline + the human gate
end-to-end on the current coordinator and iterate from results — not
produce a publishable review.

### PRISMA Flow (this run)

| Stage | n |
|-------|---|
| Records identified (PubMed) | 172 |
| Records retrieved | 100 |
| Duplicates removed | 1 |
| Records screened | 99 |
| Excluded at abstract screen | 62 |
| Uncertain (→ human review) | 33 |
| Included after abstract screen | 4 |

Internally consistent (62 + 33 + 4 = 99). This is a **genuine** screen
of the 99 deduped records — distinct from the PoC numbers above.

### What this iteration demonstrated (and what it did not)

- **The human review gate did its job — the headline result.** The
  Haiku screener first *fabricated*: it emitted 170 decisions for 99
  inputs, reproducing this README's documented PoC distribution
  (145 / 21 / 4) instead of screening the deduped records. The human
  review gate caught it (decision-count vs input mismatch), issued a
  precise `request_changes`, and the agent **self-corrected** into the
  genuine 99-decision screen above. The collaboration mechanism
  catching and correcting a real AI failure mode is the demonstration
  — not a happy path.
- **Systems demonstration, not a citable review.** Haiku screening
  content is not trustworthy for an actual systematic review (it
  confabulated; even corrected it dropped ~1/99 precision). The
  numbers here are a pipeline artifact, **not** a scientific finding.
  A production screen needs Sonnet (see *What to Improve Next*) plus
  repetition / inter-rater κ. One run is an anecdote.

### Known issue surfaced

- **`max_results` does not cap retrieval below 100.** `esearch`
  `retmax` caps the returned id list, but `efetch` pulls from the
  WebEnv history in `batch=100`, so a `max_results` of 50 still
  retrieved 100 (of 172 found). Fix `scripts/01_search_pubmed.py`'s
  pagination before treating `max_results` as a real scope control.

---

## Known Limitations of This PoC Run

1. **Haiku model limitations** — extractor and synthesizer ran on Haiku due to API quota constraints. PMID 38847506 extraction is sparse (phage name, host, platform not extracted). Sonnet extracts these reliably.

2. **PRISMA count discrepancy** — the synthesizer's Methods paragraph quoted wrong counts (145/21 vs 138/28 depending on which run's data was on disk). The synthesizer needs an explicit instruction to read counts from `prisma_counts_final.tsv` rather than inferring them.

3. **No full-text for all papers** — some papers lack open-access PMC full text; those fell back to abstract-only for extraction.

4. **Single database** — only PubMed searched. A production review would add Scopus, Web of Science, and Embase.

---

## What to Improve Next

### Pipeline improvements
- [ ] **Switch extractor + synthesizer to Sonnet** (or Opus for synthesis) in `enju.yaml` — biggest quality gain
- [ ] **Fix synthesizer prompt**: add explicit instruction *"Copy PRISMA counts verbatim from `prisma_counts_final.tsv` — do not estimate or round"*
- [ ] **Add Scopus / Web of Science search** as additional `search_*` tasks feeding into a merged dedup step
- [ ] **Inter-rater reliability task**: run screener-bot twice with different seeds and compute Cohen's κ — PRISMA 2020 requires this for AI-assisted screening
- [ ] **Full-text PDF fallback**: for papers not in PMC, try Unpaywall API or DOI resolver before giving up
- [ ] **Structured quality assessment**: add a task where a bot scores each included paper on a risk-of-bias checklist (e.g., completeness of reporting, sequencing depth)

### Scientific scope
- [ ] **Broaden date range** to 2016–2024 (ONT phage work pre-dates 2018)
- [ ] **Refine query** to reduce false positives: many excluded papers were ONT for *bacterial* genomes only — adding `NOT ("16S" OR "metagenom*")` would reduce noise
- [ ] **Add phage taxonomy** extraction field: family, genus per ICTV — enables summary by phage lineage
- [ ] **Co-occurrence analysis**: which host genera are most studied with ONT phage genomics?

### For real preprint submission
- [ ] Run a fresh `enju_create_run` with Sonnet models and refined prompts
- [ ] Export `data/prisma_diagram.svg` as figure
- [ ] Human spot-check all 5 included papers' extracted fields against the actual full text
- [ ] Register the review protocol on PROSPERO before submission

---

## Running the Pipeline

```bash
# One-time project setup (already done)
enju_create_project(path="/data/prisma-review")
enju_set_project_remote(...)

# Start all bots
enju_bot_start_all(workflow="enju.yaml", project_id=3)

# Create a new run (production — use Sonnet models in enju.yaml first)
enju_create_run(path="enju.yaml", params={
  "search_query": "...",
  "date_from": "2016",
  "date_to": "2024",
  "max_results": 1000
})

# Human tasks: review_screening and review_resolution appear in your inbox
# All compute tasks run automatically; bot tasks are auto-claimed
```

## Outputs

| File | Description |
|------|-------------|
| `data/raw_records.jsonl` | Raw PubMed records |
| `data/unique_records.jsonl` | After deduplication |
| `data/screening_decisions.jsonl` | Abstract screening decisions (include/exclude/uncertain) |
| `data/resolved_decisions.jsonl` | Full-text decisions for uncertain papers |
| `data/extracted_data.jsonl` | Structured extraction (19 fields per phage genome) |
| `data/prisma_counts_final.tsv` | PRISMA 2020 counts at each stage |
| `data/prisma_diagram.svg` | PRISMA 2020 flow diagram (SVG) |
| `data/synthesis.md` | Publication-ready table + Results + Methods paragraphs |
| `data/fulltext/<pmid>.txt` | Full text or abstract for include/uncertain papers |
