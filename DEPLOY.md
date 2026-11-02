# Deploy Website ke Streamlit Community Cloud

Panduan ini untuk membuat URL publik dari aplikasi `app.py`.

## Yang perlu disiapkan

- Akun GitHub.
- Akun Streamlit Community Cloud (bisa daftar/login memakai GitHub).
- Repository GitHub **public**.

## 1. File yang perlu di-push

Untuk menjalankan website, file minimal yang dibutuhkan:

```text
app.py
pipeline.py
requirements.txt
runtime.txt
.streamlit/config.toml
demo/                 (gambar contoh)
README.md
DEPLOY.md
```

Untuk submission UTS, sertakan juga:

```text
UTS_Kelompok07.ipynb
dataset/
laporan_Kelompok07.pdf
slide_Kelompok07.pdf
```

**Jangan push:**

- `p.py` — berisi API key hard-coded dan tidak dipakai website.
- `dataset/dataset.zip` — duplikat arsip besar.
- `dataset/dataset/` — duplikat folder dataset.
- `output.zip` — arsip hasil yang tidak dibutuhkan website.
- `.streamlit/secrets.toml` — jika nanti ada secret.

File-file tersebut sudah dimasukkan ke `.gitignore`.

## 2. Buat repository GitHub

1. Buka <https://github.com/new>.
2. Isi nama repository dengan judul tema, misalnya `Penghitung-Butir-Kacang-Hijau`.
3. Pilih **Public**.
4. Jangan centang "Add a README file" agar tidak bentrok saat push.
5. Klik **Create repository**, lalu salin URL repository.

## 3. Push dari laptop

Buka PowerShell di folder proyek:

```powershell
cd "D:\New folder (11)\UTS_VisKom_Kelompok07"
```

Inisialisasi repository (folder ini belum punya `.git` sendiri):

```powershell
git init
git add .
git status
```

Periksa output `git status`: pastikan `p.py`, `dataset/dataset.zip`, `dataset/dataset/`, dan `output.zip` **tidak muncul**. Setelah itu:

```powershell
git commit -m "Website penghitung butir kacang hijau"
git branch -M main
git remote add origin https://github.com/USERNAME/Penghitung-Butir-Kacang-Hijau.git
git push -u origin main
```

Ganti `USERNAME` dengan username GitHub masing-masing.

> Catatan: folder proyek ini berada di dalam repository `D:\`. `git init` di dalam folder proyek membuat repository terpisah, sehingga hanya isi folder ini yang di-push.

## 4. Deploy di Streamlit Community Cloud

1. Buka <https://share.streamlit.io>.
2. Login dengan GitHub.
3. Klik **Create app** atau **New app**.
4. Pilih **Deploy a public app from GitHub**.
5. Isi:
   - **Repository:** `USERNAME/Penghitung-Butir-Kacang-Hijau`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** `penghitung-butir-kacang-hijau` (bisa berbeda jika sudah dipakai)
6. Klik **Deploy** dan tunggu proses build selesai (biasanya 2–5 menit).
7. Setelah muncul, uji upload gambar dan tombol contoh.

URL akhir akan berbentuk:

```text
https://penghitung-butir-kacang-hijau.streamlit.app
```

## 5. Setelah deploy

- Salin URL ke `README.md` pada bagian "Website Streamlit".
- Uji di desktop dan HP.
- Uji upload foto baru, bukan hanya gambar contoh.
- Jika aplikasi tertidur karena tidak dipakai, buka URL-nya untuk membangunkan lagi.

## Troubleshooting

**`ImportError: libGL.so.1`**

Jangan ganti `opencv-python-headless` menjadi `opencv-python` di `requirements.txt`.
Streamlit Cloud tidak menyediakan library GUI Linux yang dibutuhkan versi biasa.

**Build gagal**

Buka **Manage app → Logs** di Streamlit Cloud. Penyebab umum:

- typo pada `requirements.txt`;
- nama file utama bukan `app.py`;
- `pipeline.py` tidak ikut ter-push.

**`ModuleNotFoundError: No module named 'pipeline'`**

Pastikan `pipeline.py` berada di folder yang sama dengan `app.py` dan ikut di-push.

**Build lambat karena repository besar**

Folder `dataset/` berisi foto beresolusi tinggi. Jika build terlalu lama, buat
repository terpisah yang hanya berisi file minimal website di atas, lalu deploy
dari repository tersebut.

**Upload ditolak**

Batas upload diatur ke 50 MB di `.streamlit/config.toml`. Perkecil foto atau
ubah nilai `maxUploadSize` jika perlu.

## Keamanan

`p.py` berisi API key dalam bentuk plain text. File itu tidak dipakai oleh
website dan jangan pernah di-push ke repository publik. Sebaiknya revoke/rotate
API key tersebut di penyedia API karena sudah tersimpan di file lokal.
