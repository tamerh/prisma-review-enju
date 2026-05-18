Screening is not sound — it does not match this run's input. Fatal data-integrity issue:

- Input `data/unique_records.jsonl` = 99 records. Your `data/screening_decisions.jsonl` = 170 decisions (145 exclude / 21 uncertain / 4 include). A faithful screen of 99 inputs yields exactly 99 decisions, one per PMID.
- The 170/145/21/~5 distribution and the included PMIDs (38360595, 36779715, 34772986, …) are identical to the documented prior PoC in `README.md`/`goal.md`. This indicates the decisions were reproduced from the documentation/spec text in context rather than derived by screening the actual deduped records.

Required changes — re-screen strictly:
1. Read ONLY `data/unique_records.jsonl`. Screen exactly the records in that file.
2. Output exactly one decision object per input PMID — the line count of `screening_decisions.jsonl` MUST equal the line count of `unique_records.jsonl` (99), and every `pmid` must come from that file.
3. Do NOT read or reuse any counts, PMIDs, or PRISMA numbers from `README.md`, `goal.md`, `breakdown.md`, or any prior run — those describe a different, larger dataset. Decide each record solely from its own title/abstract against the inclusion/exclusion criteria.
4. Self-check before submitting: assert len(decisions) == len(unique_records) and that every decided pmid is present in unique_records.jsonl.