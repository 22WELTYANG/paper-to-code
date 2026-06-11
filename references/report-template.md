# Reproduction Report

> Contract: this report proves, at most, that the pipeline runs end to end.
> A smoke experiment is NOT a full reproduction, and this report MUST never
> claim that the paper's results or SOTA have been reproduced. Write it as
> an engineering record, not a press release.

## 1. Summary

The first sentence MUST state the verification level achieved, e.g.:
"This smoke experiment demonstrates that the reference implementation runs
end to end; it does not validate the paper's reported results."

## 2. Paper-Reported Results

Copy from `extraction.md` §7: metric, value, dataset/split, source location.

## 3. Smoke Experiment Setup

Exact smoke configuration: data size, batch size, epochs/steps, hardware,
runtime, random seed. State explicitly how it differs from the paper's setup.

## 4. Metric Comparison

| Metric | Paper Reported | Smoke Result | Status | Notes |
|---|---:|---:|---|---|

Status MUST be one of (no other values allowed):

- `[MATCH]` — only permitted when the setup is also comparable; results on
  toy data are at most `[PARTIAL]`, never `[MATCH]`.
- `[PARTIAL]` — directionally consistent under a reduced setup.
- `[GAP / 需要完整算力]` — verification requires full-scale compute or data.
- `[NOT TESTED]` — not measured in the smoke run.

## 5. Assumptions

Every `ASSUMED` hyperparameter and data decision, with its reason
(from `extraction.md` §6). Hyperparameters taken from the paper MUST be
listed separately from assumed ones.

## 6. Known Gaps

- Which hyperparameters came from the paper vs. were `ASSUMED`.
- Which datasets were not fully downloaded.
- Which metrics could not be verified in the smoke test.
- Whether the current results prove anything beyond "the pipeline runs".

## 7. Reproducibility Checklist

- [ ] Random seed fixed and recorded
- [ ] Exact commands recorded
- [ ] Environment / package versions recorded
- [ ] Config (paper / assumed / smoke blocks) committed
- [ ] Logs and checkpoints saved

## 8. Next Steps

Concrete actions to move from smoke toward a meaningful reproduction:
full dataset, paper hyperparameters, longer training, missing metrics,
ablations, comparison against an official repository if one exists.
