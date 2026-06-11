# Generated Reproduction Repository Scaffold

This document is the contract for the repository generated in Stage 3.
Follow it exactly unless the user explicitly asks otherwise.

## Required Files

```text
generated-repo/
├── model/
│   ├── __init__.py
│   └── model.py
├── data/
│   ├── __init__.py
│   └── dataset.py
├── train.py
├── eval.py
├── config.yaml
├── requirements.txt
├── README.md
└── reproduction-report.md
```

## File Responsibilities

- `model/model.py` — the method/architecture from `extraction.md` §2–3.
  Docstrings MUST reference the extraction section (and paper page) each
  design decision comes from.
- `data/dataset.py` — dataset loading and preprocessing per §4. MUST include
  a toy dataset or tiny-subset mode, used by default.
- `train.py` — training loop. MUST run the smoke experiment via
  `--config config.yaml`, write a training log, and save at least one
  checkpoint or result file.
- `eval.py` — computes at least one metric from §7 on the smoke setup;
  prints results and writes them where the report can pick them up.
- `config.yaml` — see Config Contract below.
- `requirements.txt` — minimal. No heavyweight frameworks unless the method
  genuinely requires one.
- `README.md` — how to run the smoke experiment; what this repo is and,
  just as importantly, what it is not.
- `reproduction-report.md` — generated from `references/report-template.md`.

## Minimum CLI Contract

```bash
python train.py --config config.yaml
python eval.py  --config config.yaml
```

Both commands MUST run without errors on the smoke setup, on CPU, in minutes.

## Config Contract

`config.yaml` MUST keep three blocks separate, so smoke values can never be
mistaken for paper values:

```yaml
paper:    # values as reported by the paper (extraction.md §6, REPORTED)
  ...
assumed:  # values the paper does not report; each entry carries its reason
  ...
smoke:    # deliberately scaled-down values used by the smoke experiment
  ...
```

`train.py` and `eval.py` read the `smoke` block by default.

## Smoke Experiment Requirements

- Toy dataset or tiny subset; small batch; few epochs/steps.
- Must finish on a laptop CPU.
- Acceptance criteria:
  - both CLI commands exit without error;
  - a training log is produced;
  - at least one checkpoint or result file is saved;
  - at least one metric is printed;
  - `reproduction-report.md` is generated or updated.

## What This Repository Must Not Claim

- That it reproduces the paper's results.
- That it matches SOTA.
- That smoke-experiment metrics are comparable to paper metrics — the scale,
  data, and budget are different by design. A smoke experiment is NOT a full
  reproduction.
- That `ASSUMED` values match the authors' actual settings.
