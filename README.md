# Automatic Short Answer Grading — Siamese BiLSTM + FastText

Kode skripsi untuk sistem **Automatic Short Answer Grading (ASAG)** jawaban singkat berbahasa Indonesia menggunakan model **Siamese BiLSTM** dengan embedding FastText 300 dimensi.

- **Dataset**: 1.229 jawaban siswa, 17 soal esai (IDPSJ), nilai 1–10
- **Model**: Siamese BiLSTM dengan ordinal regression (9 sigmoid output)
- **Evaluasi**: 15 IDPSJ (train), 1 IDPSJ (val), 2 IDPSJ (test)

---

## Urutan Pipeline

```
preprocessing.ipynb
    ↓  datafinal_preprocessed.csv
fasttext.ipynb
    ↓  Embedding/{answers,questions,answerkeys}_emb.npy + metadata.pkl
cross_prompt_injection.ipynb
    ↓  final_{answers,questions,answerkeys}_emb.npy + final_metadata.pkl
balancing_data.ipynb
    ↓  final_* (overwrite dengan Mixup)
siamese_bilstm_direct.ipynb      # jalankan di Kaggle (GPU)
```

---

## Notebook

| File | Keterangan |
|------|------------|
| `preprocessing.ipynb` | Preprocessing teks: lowercase, tokenisasi kalimat, normalisasi simbol, hapus tanda baca |
| `fasttext.ipynb` | Embedding FastText 300D; analisis distribusi panjang token; simpan embedding per sampel |
| `cross_prompt_injection.ipynb` | Augmentasi Cross-Prompt Injection: isi grade yang tidak ada di suatu IDPSJ dengan jawaban dari IDPSJ lain |
| `balancing_data.ipynb` | Augmentasi Mixup intra-class: penyeimbangan distribusi grade per IDPSJ |
| `siamese_bilstm_direct.ipynb` | Model utama Siamese BiLSTM v11; analisis fold terbaik & terburuk |
| `siamese_bilstm_direct_no_cross.ipynb` | Ablasi: evaluasi in-prompt (tanpa cross-prompt, train & test pada IDPSJ yang sama) |

---

## Catatan

- **File embedding (`.npy`, `.pkl`), model (`.keras`), dan dataset** tidak disertakan karena ukurannya terlalu besar.
- Data dan embedding tersedia di Kaggle (diperlukan untuk menjalankan `siamese_bilstm_direct.ipynb`).
- Pre-trained FastText (`cc.id.300.bin`, ~6 GB) dapat diunduh dari [fasttext.cc/docs/en/crawl-vectors.html](https://fasttext.cc/docs/en/crawl-vectors.html).
- Training dan inferensi dilakukan di **Kaggle** (GPU diperlukan). Preprocessing dapat dijalankan secara lokal.
