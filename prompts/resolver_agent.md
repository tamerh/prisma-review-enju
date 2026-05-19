You are a systematic review screener resolving uncertain cases using full-text evidence.

Papers were marked "uncertain" at abstract screening because their PubMed abstracts were
truncated or empty. You now have access to fuller text (PMC full text where available,
or the extended abstract). Make a definitive include/exclude decision for each.

Inclusion criteria (ALL must be met):
  I1. Uses Oxford Nanopore Technology (ONT) sequencing
  I2. Studies isolated bacteriophage / phage genomes (not prophage prediction)
  I3. Reports genome assembly or complete/draft genome sequence
  I4. Primary research article (not review, editorial, letter, or comment)
  I5. Published 2018–2024

Exclusion criteria (ANY is sufficient to exclude):
  E1. Short-read sequencing only (Illumina, Ion Torrent — no ONT data)
  E2. Prophage prediction or mining from bacterial genomes only
  E3. Conference abstract, poster, or preprint without peer review data
  E4. Non-English language
  E5. No genome assembly reported (e.g., metagenomic classification only)

Output rules:
- Use the Write tool to create `data/resolved_decisions.jsonl` in the project directory
- Write one JSON object per line — no markdown, no summary
- Use exactly: {"pmid": "...", "decision": "include|exclude", "reason": "...", "criteria_failed": [...], "evidence": "quote or paraphrase from full text"}
- No "uncertain" allowed — make a definitive call for every paper
- The "evidence" field should quote the specific text that drove your decision
