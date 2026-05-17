# Automated Essay Scoring — Siamese BiLSTM + FastText

Kode skripsi untuk sistem **Automated Essay Scoring (AES)** esai berbahasa Indonesia menggunakan model **Siamese BiLSTM** dengan embedding FastText 300 dimensi.

- **Dataset**: 1.229 jawaban siswa, 17 soal esai (IDPSJ), nilai 1–10
- **Model**: Siamese BiLSTM dengan ordinal regression (9 sigmoid output)
- **Evaluasi**: Leave-One-Prompt-Out (LOPO) cross-validation

---

## Urutan Pipeline

```
preprocessing.ipynb
    ↓  datafinal_preprocessed.csv
fasttext.ipynb
    ↓  Embedding/5/{answers,questions,answerkeys}_emb.npy + metadata.pkl
augmentasi_gen_ai.ipynb          # opsional: augmentasi data via GenAI
    ↓  aug_datafix.csv
cross_prompt_injection.ipynb
    ↓  Embedding/5/final_{answers,questions,answerkeys}_emb.npy + final_metadata.pkl
balancing_data.ipynb
    ↓  Embedding/5/final_* (overwrite dengan Mixup)
siamese_bilstm_final.ipynb       # training LOPO — jalankan di Kaggle (GPU)
```

---

## File Utama

| File | Keterangan |
|------|------------|
| `datafinal.csv` | Dataset mentah (1.229 sampel) |
| `datafinal_preprocessed.csv` | Setelah preprocessing |
| `siamese_bilstm_final.ipynb` | Model utama, evaluasi LOPO |
| `siamese_bilstm_direct.ipynb` | Versi pengembangan + analisis thesis |
| `siamese_bilstm_lms.ipynb` | Versi produksi untuk LMS (ensemble, all-data) |
| `Test/` | Hasil metrik dan visualisasi per percobaan |

## Notebook Eksperimen

| File | Keterangan |
|------|------------|
| `siamese_bilstm_no_mask.ipynb` | Ablasi tanpa attention masking |
| `siamese_bilstm_direct_no_cross.ipynb` | Ablasi tanpa Cross-Prompt Injection |
| `siamese_bilstm_direct_no_seed.ipynb` | Ablasi tanpa multi-seed ensemble |
| `hyperparameter-tunning.ipynb` | Grid search hyperparameter |
| `optuna_hyperparameter_tuning.ipynb` | Tuning via Optuna |
| `faiss_regression.ipynb` | Eksperimen retrieval-based scoring |
| `indobert.ipynb` | Pipeline alternatif dengan IndoBERT |

---

## Catatan

- **File embedding (`.npy`, `.pkl`) dan model (`.keras`) tidak disertakan** karena ukurannya ratusan MB.  
  Dataset embedding dan model tersedia di Kaggle: [link dataset Kaggle].
- Pre-trained FastText (`cc.id.300.bin`, ~6 GB) dapat diunduh dari [fasttext.cc/docs/en/crawl-vectors.html](https://fasttext.cc/docs/en/crawl-vectors.html).
- Training dilakukan di **Kaggle** (GPU diperlukan). Preprocessing dan pengeditan notebook dapat dilakukan secara lokal.
