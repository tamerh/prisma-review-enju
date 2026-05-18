Perfect! The screening is complete. Verified:

- **99 records processed** (all PMIDs accounted for)
- **10 include** – papers meeting all criteria (ONT + isolated phage + genome assembly + primary research + 2018–2024)
- **71 exclude** – papers failing one or more exclusion criteria
- **18 uncertain** – papers with ambiguous abstracts or unclear phage status; reserved for human review

Output written to `data/screening_decisions.jsonl` in the required format: one JSON object per line with `pmid`, `decision`, `reason`, and `criteria_failed` fields.

Key design decisions:
- Papers with truncated/incomplete abstracts marked uncertain (can't verify all criteria)
- Conservative on phage status: papers about bacterial genomes with phage genes marked uncertain
- Benchmarking/mock community papers still included if they explicitly assemble phage genomes
- Transcriptomics-only papers excluded (no genome assembly focus)

Human review needed for the 18 uncertain cases to verify phage status and sequencing technology details.
