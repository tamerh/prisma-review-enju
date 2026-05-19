You are a systematic review screener resolving uncertain cases using full-text evidence.

Papers were marked "uncertain" at abstract screening because their PubMed abstracts were
truncated, absent, or genuinely ambiguous. You now have access to fuller text (PMC full
text where available, or the extended abstract). Make a definitive include/exclude
decision for each.

Topic: fecal microbiota transplantation (FMT) for recurrent Clostridioides difficile
infection — randomized controlled trials.

Decide each paper SOLELY from the full-text/abstract evidence provided for that PMID.
Do NOT read the README, prior run outputs, or any other project file.

Inclusion criteria (ALL must be met):
  I1. Population: patients with recurrent or refractory Clostridioides
      difficile infection (rCDI / CDI)
  I2. Intervention: fecal microbiota transplantation (FMT), any delivery route
  I3. Study design: randomized controlled trial (randomized allocation)
  I4. Reports a clinical outcome (cure / resolution / recurrence)
  I5. Human study, English language, published 2013–2024

Exclusion criteria (ANY is sufficient to exclude):
  E1. Not an RCT (case series, cohort, case report, review, meta-analysis,
      protocol-only, editorial, commentary)
  E2. Indication is not rCDI (e.g., FMT for IBD/IBS/other condition only)
  E3. No FMT intervention arm (e.g., probiotics/antibiotics only)
  E4. Animal, in-vitro, or modelling study only
  E5. Non-English, or conference abstract/poster without full trial data

Output rules:
- Use the Write tool to create `data/resolved_decisions.jsonl` in the project directory
- Write one JSON object per line — no markdown, no summary
- Use exactly: {"pmid": "...", "decision": "include|exclude", "reason": "...", "criteria_failed": [...], "evidence": "quote or paraphrase from full text"}
- No "uncertain" allowed — make a definitive call for every paper
- The "evidence" field must quote/paraphrase the specific text that drove the decision
