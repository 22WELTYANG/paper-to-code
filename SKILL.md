---
name: paper-to-code
description: >
  Turn a research paper (arXiv URL, arXiv ID, or local PDF) into a confirmed
  method extraction, a runnable reference implementation, a small smoke
  experiment, and an honest reproduction report. Use when the user says
  "reproduce this paper", "paper to code", "implement this arXiv method",
  "turn this PDF into code", "write a repo based on this paper",
  "复现这篇论文", "实现 arXiv 上的方法", "把这个 PDF 变成代码",
  "根据论文写一个 repo", or pastes an arXiv link and asks whether it can run
  ("能跑吗" / "can this run").
---

# paper-to-code

Given a paper, produce: (1) a structured extraction the user confirms,
(2) a runnable reference implementation, (3) a small smoke experiment, and
(4) an honest report comparing smoke results against paper-reported metrics.

The promise is deliberately modest: a reference implementation plus an
honest minimal experiment — never "one-click SOTA reproduction".

## Why extraction confirmation comes before code

Confirming `extraction.md` first prevents generating a large volume of wrong
code based on a misreading of the paper. The most dangerous failure mode in
paper reproduction is not code that crashes — it is code that **looks like it
works but whose method, data, and metrics silently diverge from what the
paper actually says**. A crash is visible immediately; a silent divergence
can absorb days of debugging and produce confidently wrong conclusions.
Pausing on a one-page extraction converts the cost of a misreading from
"throw away an entire repository" into "edit one document". This pause is
the core trust mechanism of this project. Never bypass it.

## IRON RULES

1. NEVER pretend the paper reports a hyperparameter it does not. Every
   missing value is marked `ASSUMED: value=..., reason=...` (or `UNKNOWN`).
2. NEVER present the smoke experiment as a full reproduction. A smoke
   experiment is not a full reproduction — it only proves the code runs.
3. NEVER claim that SOTA or the paper's results have been reproduced.
4. NEVER generate implementation code before the user confirms
   `extraction.md` (Pause 1). Do not bypass the extraction confirmation.
5. NEVER start the smoke run without first stating its limitations (Pause 2).
6. If the method does not fit this MVP (multi-model systems, massive
   pipelines, closed data), degrade honestly: deliver pseudocode or a
   clearly labelled partial implementation, and say so.
7. Every metric the smoke run cannot verify is labelled
   `[GAP / 需要完整算力]` or `[NOT TESTED]` in the report.

## Templates (always use; do not improvise structure)

- `references/extraction-template.md` → structure of `extraction.md`
- `references/repo-scaffold.md` → contract for the generated repository
- `references/report-template.md` → structure of `reproduction-report.md`

## Workflow

### Stage 0 — Scope and honesty check

Before fetching anything, assess: can the core method be implemented as a
single reference module with a toy-data smoke run? Good fits: an
architecture, a loss, a training technique. Poor fits: multi-stage systems,
RLHF-scale pipelines, closed datasets. If it is a poor fit, say so now and
offer the honest downgrade (IRON RULE 6). Tell the user up front what this
run will and will not demonstrate.

### Stage 1 — Fetch and parse the paper

```bash
python scripts/fetch_paper.py <arxiv-url|arxiv-id|path/to.pdf> --out runs/<slug>
```

Produces `paper.pdf`, `paper.txt`, `metadata.json`. Then READ `paper.txt`
and check quality: if many pages carry warnings or the text is garbled
(two-column and math-heavy papers often are), tell the user and ask whether
they can provide the LaTeX source or a cleaner PDF before continuing. Do not
silently extract from broken text.

### Stage 2 — Produce `extraction.md`

Fill `references/extraction-template.md` completely. Four content classes
are mandatory:

1. Core method/algorithm — formulas, pseudocode, and prose converted into
   structured steps: inputs, outputs, loss, forward pass, training loop.
2. Dataset and preprocessing — names, sources, splits, normalization /
   tokenization / augmentation; missing pieces marked `ASSUMED`.
3. Hyperparameters — the full table; every missing entry written as
   `ASSUMED: value=..., reason=...`.
4. Reported metrics — name, value, table/section/page source; these anchor
   the final report.

Cite `=== Page N ===` markers from `paper.txt` wherever possible.

### ■ Pause 1 — Wait for user confirmation of extraction.md

STOP. Present `extraction.md`, direct the user to §9 (risks and
ambiguities) and §10 (confirmation checklist), and ask for corrections or
confirmation. Generate no implementation code until the user explicitly
confirms. If the user corrects anything, update `extraction.md` and confirm
again.

### Stage 3 — Generate the reproduction repository

Precondition: the user has confirmed `extraction.md`.

Follow `references/repo-scaffold.md` exactly: required files, CLI contract,
and the three-block config (`paper:` / `assumed:` / `smoke:`) that keeps
paper-reported, assumed, and smoke-test setups permanently distinguishable.
Default to a toy dataset or tiny subset. Reference `extraction.md` sections
in code docstrings so every design decision is traceable to the paper.

### Stage 4 — Explain smoke experiment limitations

Tell the user, before running anything: the upcoming run uses small batches,
few epochs, and toy data or a tiny subset. It exists to prove the code runs
end to end. It does not — and cannot — reproduce the paper's metrics.

### ■ Pause 2 — Notify before the smoke run

Confirm the user wants the smoke run executed now, or let them run it
themselves.

### Stage 5 — Run the smoke experiment

```bash
python train.py --config config.yaml
python eval.py  --config config.yaml
```

Acceptance: both commands exit cleanly; a training log is produced; at least
one checkpoint or result file is saved; at least one metric is printed. If
something fails, fix the code — never relax the acceptance criteria.

### Stage 6 — Generate `reproduction-report.md`

Fill `references/report-template.md`. Compare paper-reported metrics with
smoke results line by line, using only the four status labels (`[MATCH]`,
`[PARTIAL]`, `[GAP / 需要完整算力]`, `[NOT TESTED]`). The report MUST state
plainly: which hyperparameters came from the paper and which were `ASSUMED`;
which datasets were not fully downloaded; which metrics the smoke test
cannot verify; and that the current result proves pipeline viability, not
reproduction. Do not exaggerate results.

### Stage 7 — Suggest next iteration

Offer concrete, prioritized next steps: full dataset, paper
hyperparameters, longer training, missing metrics, ablations, comparison
against an official repository if one exists.
