import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig = plt.figure(figsize=(16, 24), facecolor='white')
ax  = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 16)
ax.set_ylim(0, 24)
ax.axis('off')

# ── helpers ─────────────────────────────────────────────────────────────────

def B(cx, cy, w, h, txt, fc, ec, fs=9, fw='normal', lw=1.5):
    p = FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                        boxstyle='round,pad=0.08',
                        fc=fc, ec=ec, lw=lw, zorder=3)
    ax.add_patch(p)
    ax.text(cx, cy, txt, ha='center', va='center',
            fontsize=fs, fontweight=fw, zorder=4,
            multialignment='center', color='#111111')

def A(x1, y1, x2, y2, c='#374151', lw=1.4, rad=0):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=c, lw=lw,
                               connectionstyle=f'arc3,rad={rad}'), zorder=5)

# ── colours ─────────────────────────────────────────────────────────────────
INP   = ('#DBEAFE', '#1D4ED8')
LSTM  = ('#D1FAE5', '#065F46')
POOL  = ('#FEF3C7', '#B45309')
FEAT  = ('#FCE7F3', '#9D174D')
CAT   = ('#EDE9FE', '#5B21B6')
DEN   = ('#E0E7FF', '#3730A3')
ORD   = ('#CFFAFE', '#0E7490')
OUT   = ('#D1FAE5', '#065F46')

# ── TITLE ────────────────────────────────────────────────────────────────────
ax.text(8, 23.45, 'Arsitektur Model Siamese BiLSTM v11',
        ha='center', va='center', fontsize=14, fontweight='bold', color='#111')
ax.text(8, 22.95,
        'Penilaian Jawaban Pendek Otomatis — Skenario Cross-Prompt (LOPO)',
        ha='center', va='center', fontsize=9.5, color='#555', style='italic')

# ── ROW 1 : INPUTS (y = 22.0) ───────────────────────────────────────────────
B( 3.0, 22.0, 3.2, 0.85, 'inp_q\nSoal\n(batch, seq_len, 300D)',       *INP, fs=8.5)
B( 7.5, 22.0, 3.2, 0.85, 'inp_ak\nKunci Jawaban\n(batch, seq_len, 300D)', *INP, fs=8.5)
B(11.5, 22.0, 3.2, 0.85, 'inp_a\nJawaban Siswa\n(batch, seq_len, 300D)',  *INP, fs=8.5)
B(15.0, 22.0, 2.0, 0.85, 'inp_scalar\n(10D)\nnormalized',             *INP, fs=8.5)

# arrows Inputs → BiLSTM / Dense
for x in [3.0, 7.5, 11.5]:  A(x, 21.57, x, 19.90)
A(15.0, 21.57, 15.0, 19.90)

# ── SHARED BILSTM BORDER (background) ───────────────────────────────────────
shared = FancyBboxPatch((1.2, 18.95), 11.8, 1.25,
                         boxstyle='round,pad=0.05',
                         fc='#ECFDF5', ec='#16A34A', lw=2, ls='dashed', zorder=2)
ax.add_patch(shared)
ax.text(7.1, 20.32, 'Shared BiLSTM Encoder  —  bobot dibagi antar cabang (weight sharing)',
        ha='center', va='center', fontsize=8, color='#15803D',
        fontweight='bold', zorder=4)

# ── ROW 2 : BiLSTM + Dense(32) (y = 19.5) ───────────────────────────────────
B( 3.0, 19.5, 2.8, 0.75, 'BiLSTM\n128 unit, Bidirectional\n→ (batch, seq_len, 256D)', *LSTM, fs=8, lw=0)
B( 7.5, 19.5, 2.8, 0.75, 'BiLSTM\n128 unit, Bidirectional\n→ (batch, seq_len, 256D)', *LSTM, fs=8, lw=0)
B(11.5, 19.5, 2.8, 0.75, 'BiLSTM\n128 unit, Bidirectional\n→ (batch, seq_len, 256D)', *LSTM, fs=8, lw=0)
B(15.0, 19.5, 2.0, 0.75, 'Dense(32)\nReLU\n→ (batch, 32D)',   *DEN, fs=8.5)

# arrows BiLSTM → Attention Pooling
for x in [3.0, 7.5, 11.5]:  A(x, 19.12, x, 18.05)
A(15.0, 19.12, 15.0, 18.05)

# ── ROW 3 : ATTENTION POOLING + scalar_feat (y = 17.6) ──────────────────────
B( 3.0, 17.6, 2.8, 0.85, 'Attention Pooling\n→ eq\n(256D)',  *POOL, fs=8.5)
B( 7.5, 17.6, 2.8, 0.85, 'Attention Pooling\n→ eak\n(256D)', *POOL, fs=8.5)
B(11.5, 17.6, 2.8, 0.85, 'Attention Pooling\n→ ea\n(256D)',  *POOL, fs=8.5)
B(15.0, 17.6, 2.0, 0.85, 'scalar_feat\n(32D)',                    *POOL, fs=8.5)

# arrows Pooling → Feature block (end at y=16.32, top of feature box)
for x in [3.0, 7.5, 11.5]:  A(x, 17.17, x, 16.32, c='#7C3AED')
A(15.0, 17.17, 15.0, 16.32, c='#7C3AED')

# ── ROW 4 : FEATURE COMPUTATION (y = 15.0, h = 2.6) ────────────────────────
feat_txt = (
    "Komputasi Fitur (sebelum Concatenate)\n"
    "\n"
    "  eq  (256D)          —  representasi soal / pertanyaan\n"
    "  eak (256D)          —  representasi kunci jawaban\n"
    "  ea  (256D)          —  representasi jawaban siswa\n"
    "  |eak − ea| (256D)    —  abs_diff  : selisih absolut kunci – jawaban\n"
    "  eak ⊙ ea  (256D)    —  had_prod  : Hadamard product kunci × jawaban\n"
    "  cos(eak, ea) (1D)   —  cos_sim_ak_a : kemiripan kunci–jawaban\n"
    "  cos(eq,  ea) (1D)   —  cos_sim_q_a  : kemiripan soal–jawaban\n"
    "  1−cos(eq, ea) (1D)  —  orisinalitas : penalti menyalin soal\n"
    "  scalar_feat (32D)   —  fitur scalar ternormalisasi (coverage, panjang, dsb)"
)
B(8.0, 15.0, 14.5, 2.6, feat_txt, *FEAT, fs=8.2)

# arrow Feature → Concat
A(8.0, 13.70, 8.0, 13.30, c='#7C3AED', lw=2.0)

# ── ROW 5 : CONCATENATE (y = 12.85, h = 0.9) ────────────────────────────────
B(8.0, 12.85, 14.5, 0.9,
  'CONCATENATE\n'
  '[eq + eak + ea + abs_diff + had_prod + cos_sim_ak_a + cos_sim_q_a + orisinalitas + scalar_feat]\n'
  '→ 1315 dimensi',
  *CAT, fs=8.5, fw='bold')

# arrow Concat → Dense(512)
A(8.0, 12.40, 8.0, 11.60, lw=2.0)

# ── ROW 6 : DENSE HEAD ───────────────────────────────────────────────────────
B(8.0, 11.17, 11.0, 0.85, 'Dense(512, ReLU)  →  BatchNorm  →  Dropout(0.40)', *DEN, fs=9)
A(8.0, 10.74, 8.0, 10.22, lw=1.8)
B(8.0,  9.80,  7.0, 0.75, 'Dense(64, ReLU)', *DEN, fs=9)
A(8.0,  9.42,  8.0,  8.95, lw=1.8)

# ── ROW 7 : ORDINAL OUTPUT ───────────────────────────────────────────────────
B(8.0, 8.52, 10.0, 0.85,
  'Dense(9, sigmoid)  —  Ordinal Output\n'
  'P(grade > k),  k = 1 … 9',
  *ORD, fs=9)

A(8.0, 8.07, 8.0, 7.52, lw=1.8)

# ── ROW 8 : DECODE ───────────────────────────────────────────────────────────
B(8.0, 7.10, 10.0, 0.80,
  'Decoding Ordinal\ngrade = Σ(σ(k) > 0.5) + 1',
  '#FEF9C3', '#92400E', fs=9)

A(8.0, 6.70, 8.0, 6.22, lw=1.8)

# ── ROW 9 : FINAL OUTPUT ─────────────────────────────────────────────────────
B(8.0, 5.80, 7.0, 0.80,
  'Prediksi Skor: 1 – 10',
  *OUT, fs=11, fw='bold', lw=2.5)

# ── Dimension annotation on the side ────────────────────────────────────────
ax_right = 15.85
for (y, txt) in [
    (22.0,  '300D × 3 input'),
    (19.5,  '256D × seq'),
    (17.6,  '256D (pooled)'),
    (15.0,  '1315D total'),
    (12.85, '1315D'),
    (11.17, '512D'),
    (9.80,  '64D'),
    (8.52,  '9D (ordinal)'),
]:
    pass   # labels already in boxes; skip side annotations for cleanliness

plt.savefig(
    r'd:\Kuliah\Semester 8\Skripsi\Kode\arsitektur_siamese_bilstm_v11.png',
    dpi=150, bbox_inches='tight', facecolor='white'
)
print('OK — saved arsitektur_siamese_bilstm_v11.png')
