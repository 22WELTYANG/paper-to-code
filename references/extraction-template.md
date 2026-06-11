# Paper Extraction

> Contract: fill EVERY section. No hyperparameter may be left blank — its
> Status MUST be `REPORTED`, `ASSUMED`, or `UNKNOWN`. The user MUST confirm
> this file before any implementation code is generated (Pause 1).

## 1. Paper Metadata

- Title:
- Authors:
- arXiv ID / source:
- Venue / year:
- Official code (if any):

## 2. Core Method / Algorithm

Convert the paper's formulas, pseudocode, and prose into structured steps.
Make explicit:

- Inputs:
- Outputs:
- Forward pass (step by step):
- Loss:
- Training loop:

Cite `paper.txt` page markers (`=== Page N ===`) for each claim where possible.

## 3. Model Architecture

Layers, dimensions, components, and parameter counts as described by the
paper. Anything inferred rather than stated MUST be marked `ASSUMED`.

## 4. Dataset and Preprocessing

- Dataset name(s):
- Data source / download:
- Train/val/test split:
- Normalization / tokenization / augmentation:

Any missing detail MUST be marked `ASSUMED` with a stated reason.

## 5. Training Objective and Loss

Exact loss formulation, weights between loss terms, regularization.

## 6. Hyperparameters

| Name | Value | Source | Status | Notes |
|---|---:|---|---|---|
| learning rate | | | | |
| batch size | | | | |
| optimizer | | | | |
| epochs | | | | |
| hidden size / model depth / dropout | | | | |
| loss weights | | | | |
| scheduler | | | | |
| random seed | | | | |

Status MUST be one of (no other values allowed):

- `REPORTED` — stated in the paper. Source MUST cite section/table/page.
- `ASSUMED` — not stated. Notes MUST read: `ASSUMED: value=..., reason=...`
- `UNKNOWN` — not stated and no defensible default; requires user input.

## 7. Reported Metrics

| Metric | Value | Dataset / Split | Source Location | Notes |
|---|---:|---|---|---|

These values anchor the comparison in `reproduction-report.md`. Record the
exact table/section/page for each.

## 8. Implementation Plan

Modules to build, in order, and which section above each one implements.

## 9. Risks and Ambiguities

List everything in the paper that is ambiguous or could plausibly be
misread. These are exactly the places a wrong implementation would come
from — be explicit.

## 10. User Confirmation Checklist

- [ ] The method description in §2–3 matches my reading of the paper.
- [ ] The dataset and preprocessing assumptions in §4 are acceptable.
- [ ] All `ASSUMED` hyperparameters in §6 are acceptable (or I corrected them).
- [ ] The reported metrics in §7 and their source locations are correct.
- [ ] I approve generating the reference implementation.
