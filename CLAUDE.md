# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Skripsi (thesis) on **Automated Essay Scoring (AES)** for Indonesian-language essays using a Siamese BiLSTM model with FastText embeddings. The dataset contains 1,229 student answers across 17 essay prompts (IDPSJ), graded 1–10.

Training is done on **Kaggle** (GPU required). Local work is limited to preprocessing and notebook editing.

## Pipeline Execution Order

Notebooks must be run in this sequence:

```
preprocessing.ipynb
    ↓  datafinal_preprocessed.csv
fasttext.ipynb
    ↓  Embedding/5/{answers,questions,answerkeys}_emb.npy + metadata.pkl
cross_prompt_injection.ipynb
    ↓  Embedding/5/final_{answers,questions,answerkeys}_emb.npy + final_metadata.pkl
balancing_data.ipynb
    ↓  Embedding/5/final_* (overwritten with Mixup-augmented data)
siamese_bilstm_final.ipynb  [runs on Kaggle]
```

The `IndoBERT/` folder has a parallel pipeline (`cross_prompt_injection.ipynb` → `balancing_data.ipynb`) for IndoBERT embeddings, currently unused in training.

## Embedding Storage Convention

Questions and answerkeys are **stored compactly** — one row per IDPSJ (not per sample) — to save storage:

```
answers_emb.npy       → (n_samples, seq_len, 300)  — one per answer
questions_emb.npy     → (n_idpsj,   seq_len, 300)  — one per prompt
answerkeys_emb.npy    → (n_idpsj,   seq_len, 300)  — one per prompt
metadata.pkl          → DataFrame: IDJwb, IDPSJ, grade, psj_idx, is_synthetic
```

**Reconstruction** (required before indexing with sample indices):
```python
questions_emb  = uniq_q_emb[metadata['psj_idx'].values]   # (n_samples, seq_len, 300)
answerkeys_emb = uniq_ak_emb[metadata['psj_idx'].values]
```

`psj_idx` is a 0-indexed integer mapping IDPSJ → row in the compact array (IDPSJ 1 → 0, IDPSJ 17 → 16). **Never use raw IDPSJ values or metadata row indices to index questions/answerkeys arrays.**

## Embedding Versions (`Embedding/` folder)

| Version | Description |
|---------|-------------|
| 1 | Original data → CPI + Mixup |
| 2 | GenAI-augmented + Mixup |
| 3 | Original → SMOTE |
| 4 | Original (no augmentation) |
| 5 | GenAI-augmented → CPI + Mixup **(active)** |

## Augmentation Logic

**Cross-Prompt Injection (CPI)** — `cross_prompt_injection.ipynb`:
- Fills grade "holes" (grade classes with 0 samples in a given IDPSJ)
- Borrows answer embeddings from donor IDPSJs that have the target grade
- Does NOT modify questions/answerkeys arrays (they stay per-IDPSJ)
- Target count = `ceil(max_class_count / 2)` per IDPSJ

**Mixup** — `balancing_data.ipynb`:
- Intra-class Mixup on `answers_emb` only for minority classes within each IDPSJ
- λ ~ Beta(0.4, 0.4) clipped to [0.5, 1.0]
- Does NOT mix questions/answerkeys

Both steps tag synthetic rows with `is_synthetic=True` in metadata. CPI rows have `IDJwb` prefix `cpi_`, Mixup rows have prefix `syn_`.

## LOPO Evaluation

`siamese_bilstm_final.ipynb` uses **Leave-One-Prompt-Out** cross-validation:
- **Test**: original data only from the held-out IDPSJ (`is_synthetic == False`)
- **Val**: original data only from the next IDPSJ in sorted order
- **Train**: all data (original + synthetic) from the remaining 15 IDPSJs

Filtering test/val:
```python
# Prefer is_synthetic column (new pipeline); fallback to IDJwb prefix (old pkl files)
if 'is_synthetic' in metadata.columns:
    is_real = ~metadata['is_synthetic'].values
else:
    is_real = ~metadata['IDJwb'].astype(str).str.startswith(('syn_', 'cpi_')).values
```

## Model Architecture (`siamese_bilstm_final.ipynb`)

**Inputs**: `(question, answerkey, answer)` sequences — each shape `(batch, seq_len, 300)`.

**Encoding**: Two separate BiLSTMs (`return_sequences=True`) + attention pooling → pooled vectors `eq`, `eak`, `ea` of shape `(batch, 256)`.

**Features merged**:
- `eq, ea, eak` — pooled representations
- `abs_diff = |eak - ea|` — element-wise difference
- `had_prod = eak ⊙ ea` — Hadamard product
- `cos_sim_ak_a`, `cos_sim_q_a` — cosine similarities
- `orisinalitas = 1 - cos_sim_q_a` — penalises copying the question
- `coverage_recall`, `coverage_precision`, `coverage_f1` — soft token-level alignment (ROUGE-in-embedding-space) via similarity matrix `sim[i,j] = dot(ak_token_i, a_token_j)`

**Head**: Dense(512) → BN → Dropout(0.3) → Dense(256) → BN → Dropout(0.15) → Dense(64) → Dense(1, linear)

**Loss**: MSE | **Optimizer**: AdamW (lr=1e-3, decay=1e-4) | **Training**: sample weights (inverse class frequency per fold)

## Key Data Files

| File | Description |
|------|-------------|
| `datafinal.csv` | Raw dataset (1229 samples, 17 IDPSJ, grades 1–10) |
| `datafinal_preprocessed.csv` | After preprocessing pipeline |
| `Embedding/5/` | Active embedding version (FastText, 300D) |
| `Pre-trained FastText Model/cc.id.300.bin` | Indonesian FastText model (~6GB, not in git) |
| `Model/1/`, `Model/2/` | Saved `.keras` model checkpoints per fold |

## Preprocessing Steps (`preprocessing.ipynb`)

Text goes through four stages: lowercase + normalize whitespace → sentence tokenization (regex-based, handles numbering/bullets) → symbol normalization (`:=` → "adalah", `/` → "atau", etc.) → punctuation removal. Output is a list of clean sentences per field.

FastText embedding uses **P95 token length** as `seq_len` (not max), to avoid excessive padding from outliers. OOV tokens get `epsilon=1e-7` instead of zero to avoid masking mid-sequence.
