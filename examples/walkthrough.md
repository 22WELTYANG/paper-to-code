# Walkthrough (placeholder)

The structure below is final; sections marked TODO will be completed
end-to-end once a concrete paper is chosen with the user.

## 1. Choosing a first paper

Good first candidates:

- A single, self-contained method (one model, one loss).
- A standard public dataset with a small subset easily available.
- Metrics that are cheap to compute (accuracy, perplexity, F1).
- Avoid: multi-stage systems, closed data, results requiring large compute.

## 2. Example flow

```bash
python scripts/fetch_paper.py 1706.03762 --out runs/transformer
# agent reads runs/transformer/paper.txt and checks extraction quality
# agent writes runs/transformer/extraction.md
# >>> Pause 1: you confirm (or correct) extraction.md
# agent generates generated-repo/ per references/repo-scaffold.md
# >>> Pause 2: agent states the smoke experiment's limits
cd generated-repo
python train.py --config config.yaml
python eval.py  --config config.yaml
# agent writes reproduction-report.md
```

## 3. extraction.md sample fragment

```markdown
## 6. Hyperparameters

| Name | Value | Source | Status | Notes |
|---|---:|---|---|---|
| learning rate | custom schedule | §5.3, p.7 | REPORTED | warmup_steps=4000 |
| dropout       | 0.1             | §5.4, p.8 | REPORTED | |
| random seed   | 42              | —         | ASSUMED  | ASSUMED: value=42, reason=not stated in paper |
```

## 4. Generated repo structure

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

## 5. Smoke experiment commands

```bash
python train.py --config config.yaml   # toy subset, few steps, CPU-friendly
python eval.py  --config config.yaml
```

## 6. reproduction-report.md sample fragment

```markdown
| Metric | Paper Reported | Smoke Result | Status | Notes |
|---|---:|---:|---|---|
| BLEU (EN-DE) | 28.4 | 1.2 | [GAP / 需要完整算力] | toy subset, 50 training steps |
```

## 7. Status

TODO: this walkthrough will be completed with real outputs once the user
provides a concrete paper to run end to end.
