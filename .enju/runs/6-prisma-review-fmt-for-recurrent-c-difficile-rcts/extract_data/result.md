`data/extracted_data.jsonl` written with 13 records (all valid JSON), one per included paper. 

**Notes on extraction:**
- Full texts for 8 papers had wrong PMC content (NCBI elink mismatch); data was extracted from the correct PubMed abstracts in `unique_records.jsonl` for those
- The bile acid sub-study text linked to PMID 33694229 confirmed the trial was Danish and used enema delivery, consistent with the abstract
- PMID 36152636 (EarlyFMT) enrolled first/second CDI (not ≥3 recurrences); included as per screening decision
- PMID 29851107 compares single vs multiple FMT infusions (no antibiotic-only comparator arm)
- `fmt_route` for 36152636 is `null` — not stated in available text
