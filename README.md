# Penghitung Butir Kacang Hijau — UTS Praktikum Visi Komputer

**Kelompok 07 · Tema 7**

Proyek ini menghitung butir kacang hijau pada foto berlatar polos dan mengelompokkan hasil menjadi **utuh** atau **patah/kecil**. Proyek berisi notebook eksperimen OpenCV dan aplikasi web Streamlit untuk mencoba pipeline pada gambar baru.

## Anggota kelompok

| Nama | NPM |
|---|---|
| Rahiqul Munadhil | 2408017010049 |
| Niswatul Azimah | 2408107010003 |
| Muhammad Irfan Qadafi | 24080107010054 |
| Muhammad Nuril Alam | 2408107010081 |

## Deskripsi dan pipeline

Pipeline menggunakan pemrosesan citra klasik **OpenCV + NumPy**, bukan deep learning:

1. Perkecil gambar agar sisi terpanjang maksimal 1000 px.
2. Ubah ke grayscale dan normalisasi pencahayaan (*flat-field*).
3. Median blur (`k=5`) untuk menekan noise.
4. Otsu threshold, deteksi polaritas foreground otomatis, dan operasi morfologi.
5. `findContours` dan `contourArea` untuk mendeteksi objek; `minAreaRect` untuk mengukur dimensinya.
6. Klasifikasikan berdasarkan luas: ambang **264,875 px²** atau 65% dari median luas butir ideal (**407,5 px²**). Luas di bawah ambang dikategorikan patah/kecil.

Implementasi pipeline utama ada di `UTS_Kelompok07.ipynb`; versi modular yang dipakai website ada di `pipeline.py`.

## Dataset

Dataset terdiri dari **27 foto** dengan anotasi manual di `dataset/ground_truth.csv`.

| Kondisi | Foto | Keterangan |
|---|---:|---|
| Ideal | 11 | Butir terpisah, latar polos |
| Cahaya | 5 | Variasi pencahayaan dan bayangan |
| Rusak | 5 | Campuran utuh dan patah |
| Sulit | 6 | Butir menempel atau bertumpuk |

Dataset disimpan di `dataset/`. Foto perlu diambil sendiri dan ground truth dihitung manual sebelum pemrosesan.

## Hasil dan evaluasi

Evaluasi pada 27 foto menggunakan metrik notebook:

| Kondisi | Akurasi hitung | Foto dalam toleransi 10% |
|---|---:|---:|
| Ideal | 98,4% | 11/11 (100%) |
| Cahaya | 66,5% | 1/5 (20%) |
| Rusak | 95,0% | 5/5 (100%) |
| Sulit | 7,0% | 0/6 (0%) |
| **Rata-rata** | **71,5%** | **17/27 (63%)** |

Waktu proses rata-rata di notebook sekitar **150 ms per foto**. Hasil visual, tabel evaluasi, dan grafik tersimpan di `output/`.

### Eksperimen pembanding

| Varian | Akurasi hitung | Foto dalam toleransi |
|---|---:|---:|
| Otsu global + median blur `k=5` (default) | 71,5% | 63% |
| Adaptive Gaussian (`block=31`, `C=5`) | 73,0% | 59% |
| Gaussian blur `k=5` | 72,2% | 63% |
| Tanpa blur | 71,4% | 59% |

Adaptive threshold sedikit lebih tinggi pada rata-rata, tetapi Otsu dipilih sebagai default karena lebih banyak foto memenuhi toleransi. Keterbatasan utama adalah objek bertumpuk dapat menyatu sebagai satu kontur; pecahan besar juga dapat memiliki luas yang mirip dengan butir utuh.

## Menjalankan website secara lokal

**Prasyarat:** Python 3.12 direkomendasikan.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Buka `http://localhost:8501`. Aplikasi menerima JPG, PNG, dan WEBP; menampilkan gambar asli serta hasil berdampingan; dan menyajikan jumlah total, utuh, dan patah/kecil. Tombol **Coba contoh gambar** memuat gambar demo.

## Menjalankan notebook

```bash
pip install opencv-python numpy matplotlib jupyter
jupyter notebook UTS_Kelompok07.ipynb
```

Di Jupyter/VS Code, jalankan **Restart & Run All**. Notebook membuat tabel evaluasi, eksperimen, grafik, mask, dan gambar beranotasi di `output/`.

## Deploy website

Petunjuk push ke GitHub dan deploy ke Streamlit Community Cloud ada di [`DEPLOY.md`](DEPLOY.md). File utama Streamlit adalah `app.py`. URL publik dicantumkan di sini setelah deployment selesai.

## Struktur file utama

```text
app.py                       Aplikasi Streamlit
pipeline.py                  Pipeline OpenCV untuk website
requirements.txt             Dependency aplikasi
runtime.txt                  Target Python untuk Streamlit Cloud
.streamlit/config.toml       Tema dan batas ukuran upload
UTS_Kelompok07.ipynb         Notebook eksperimen/evaluasi
dataset/                     Foto dan ground_truth.csv
output/                      Hasil evaluasi dan visualisasi
demo/                        Foto contoh untuk website
laporan_Kelompok07.pdf       Laporan
slide_Kelompok07.pdf         Slide presentasi
DEPLOY.md                    Panduan deploy
```

## Catatan submission dan keamanan

- ZIP submission berisi kode, notebook, dataset, output, laporan, dan slide; arsip duplikat tidak diperlukan.
- `p.py` tidak digunakan website dan **tidak boleh dimasukkan ke repository/ZIP** karena berisi API key. Revoke/rotate key tersebut.
- Cantumkan sumber kode yang digunakan dalam laporan dan pastikan seluruh anggota dapat menjelaskan pipeline saat tanya jawab.
