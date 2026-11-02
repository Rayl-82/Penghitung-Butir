"""Website demo UTS Visi Komputer Kelompok 07.

Menjalankan pipeline OpenCV dari notebook untuk menghitung butir kacang
hijau, lalu menampilkan gambar asli dan hasil deteksi berdampingan.
"""

from __future__ import annotations

import base64
import html
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageOps

from pipeline import imread_unicode, run_pipeline_image

BASE_DIR = Path(__file__).resolve().parent
DEMO_DIR = BASE_DIR / "demo"

TEAM = [
    "Rahiqul Munadhil",
    "Niswatul Azimah",
    "Muhammad Irfan Qadafi",
    "Muhammad Nuril Alam",
]
NPMS = [
    "2408017010049",
    "2408107010003",
    "24080107010054",
    "2408107010081",
]

PAGE_TITLE = "Penghitung Butir Kacang Hijau"


def find_demo_image() -> Path | None:
    """Pilih satu gambar contoh untuk hero dan tombol demo."""
    if not DEMO_DIR.exists():
        return None
    preferred = DEMO_DIR / "uji_demo2.jpeg"
    if preferred.exists():
        return preferred
    for suffix in ("*.jpeg", "*.jpg", "*.png", "*.webp"):
        files = sorted(DEMO_DIR.glob(suffix))
        if files:
            return files[0]
    return None


DEMO_IMAGE = find_demo_image()


def load_uploaded_image(uploaded_file) -> np.ndarray:
    """Baca upload, betulkan orientasi EXIF, lalu kembalikan array BGR."""
    with Image.open(uploaded_file) as image:
        image = ImageOps.exif_transpose(image)

        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGBA")
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.getchannel("A"))
            image = background
        else:
            image = image.convert("RGB")

        rgb = np.array(image)

    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def image_data_uri(path: Path) -> str:
    """Ubah gambar lokal menjadi data URI untuk hero HTML."""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{encoded}"


def render_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        :root {
            --bg: #F7F5EF;
            --surface: #FFFFFF;
            --ink: #1E2A1C;
            --muted: #66705F;
            --border: #DDE3D5;
            --green: #3D6B35;
            --green-dark: #2D5227;
            --green-soft: #E9F0E3;
            --red: #B54A32;
            --red-soft: #F8E9E4;
            --wheat: #C6A15B;
        }

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .stApp {
            background: var(--bg);
            color: var(--ink);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.2rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3, p, label {
            color: var(--ink);
        }

        [data-testid="stHeader"] {
            background: rgba(247, 245, 239, 0.86);
            backdrop-filter: blur(8px);
        }

        #MainMenu { visibility: hidden; }

        .hero {
            display: grid;
            grid-template-columns: minmax(0, 1.15fr) minmax(300px, 0.85fr);
            gap: clamp(2rem, 5vw, 5rem);
            align-items: center;
            padding: 1rem 0 3.2rem;
            border-bottom: 1px solid var(--border);
        }

        .eyebrow {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            color: var(--muted);
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        .eyebrow-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--green);
            box-shadow: 0 0 0 4px var(--green-soft);
        }

        .hero h1 {
            font-family: 'Instrument Serif', Georgia, serif;
            font-size: clamp(3.2rem, 5.5vw, 5.4rem);
            font-weight: 400;
            line-height: 0.94;
            letter-spacing: -0.025em;
            margin: 0.7rem 0 1.2rem;
            max-width: 100%;
        }

        .hero h1 em {
            color: var(--green);
            font-style: italic;
        }

        .lede {
            max-width: 56ch;
            margin: 0 0 1.4rem;
            color: #4D5848;
            font-size: 1.02rem;
            line-height: 1.65;
        }

        .chips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .chip {
            padding: 0.34rem 0.7rem;
            border: 1px solid #D5E2CC;
            border-radius: 999px;
            background: var(--green-soft);
            color: var(--green-dark);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
        }

        .hero-visual {
            position: relative;
            margin: 0;
        }

        .hero-visual img {
            display: block;
            width: 100%;
            max-height: 380px;
            object-fit: cover;
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 18px 45px rgba(45, 66, 38, 0.12);
        }

        .photo-tag {
            position: absolute;
            top: 12px;
            left: 12px;
            z-index: 2;
            padding: 0.26rem 0.62rem;
            border: 1px solid var(--border);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.93);
            color: var(--green-dark);
            font-size: 0.6rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .hero-visual figcaption {
            margin-top: 0.7rem;
            color: var(--muted);
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        .section-head {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            margin: 2.3rem 0 0.9rem;
        }

        .section-num {
            flex: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 2rem;
            height: 2rem;
            padding: 0 0.5rem;
            border: 1px solid #CFDCC6;
            border-radius: 999px;
            background: var(--green-soft);
            color: var(--green-dark);
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.08em;
        }

        .section-head h2 {
            margin: 0;
            font-size: 1.12rem;
            font-weight: 800;
            letter-spacing: -0.01em;
        }

        .section-head p {
            margin: 0.18rem 0 0;
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.5;
        }

        [data-testid="stFileUploader"] label p {
            font-size: 0.82rem;
            font-weight: 700;
        }

        [data-testid="stFileUploaderDropzone"] {
            padding: 2.1rem 1.5rem;
            border: 1.5px dashed #B8C7AD;
            border-radius: 18px;
            background: var(--surface);
            transition: border-color 0.2s ease, background 0.2s ease;
        }

        [data-testid="stFileUploaderDropzone"]:hover {
            border-color: var(--green);
            background: #FBFDF8;
        }

        [data-testid="stFileUploaderDropzone"] button {
            border: 1px solid #C9D8BF;
            border-radius: 999px;
            background: var(--green-soft);
            color: var(--green-dark);
            font-weight: 700;
        }

        [data-testid="stFileUploaderDropzone"] button,
        [data-testid="stFileUploaderDropzone"] button p {
            color: var(--green-dark) !important;
        }

        [data-testid="stToolbar"],
        [data-testid="stStatusWidget"] {
            display: none;
        }

        .stButton > button {
            border: none;
            border-radius: 999px;
            background: var(--green);
            color: #FFFFFF;
            font-weight: 700;
            padding: 0.55rem 1.15rem;
            transition: background 0.2s ease, transform 0.2s ease;
        }

        .stButton > button,
        .stButton > button p,
        .stButton > button span,
        .stButton > button div {
            color: #FFFFFF !important;
        }

        .stButton > button:hover {
            border: none;
            background: var(--green-dark);
            color: #FFFFFF;
            transform: translateY(-1px);
        }

        .sample-note {
            margin: 0.35rem 0 0;
            color: var(--muted);
            font-size: 0.78rem;
        }

        .empty-state {
            margin-top: 0.9rem;
            padding: 2rem 2rem 1.7rem;
            border: 1px solid var(--border);
            border-radius: 22px;
            background: var(--surface);
        }

        .empty-kicker, .result-kicker {
            color: var(--green);
            font-size: 0.67rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        .empty-state h3 {
            margin: 0.35rem 0 0.5rem;
            font-family: 'Instrument Serif', Georgia, serif;
            font-size: 2rem;
            font-weight: 400;
        }

        .empty-state > p {
            max-width: 62ch;
            margin: 0;
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.6;
        }

        .tips {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin-top: 1.4rem;
            padding-top: 1.3rem;
            border-top: 1px solid var(--border);
        }

        .tip {
            display: flex;
            align-items: flex-start;
            gap: 0.7rem;
        }

        .tip span {
            padding-top: 0.1rem;
            color: var(--green);
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 0.72rem;
            font-weight: 700;
        }

        .tip p {
            margin: 0;
            color: var(--muted);
            font-size: 0.8rem;
            line-height: 1.55;
        }

        .tip strong { color: var(--ink); }

        .result-head {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1.2rem;
            margin: 1.9rem 0 0.35rem;
        }

        .result-head h2 {
            margin: 0.25rem 0 0.3rem;
            font-family: 'Instrument Serif', Georgia, serif;
            font-size: clamp(2rem, 3.5vw, 2.8rem);
            font-weight: 400;
            line-height: 1.05;
        }

        .result-head h2 strong {
            color: var(--green-dark);
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 800;
        }

        .result-sub {
            margin: 0;
            color: var(--muted);
            font-size: 0.88rem;
        }

        .sep {
            margin: 0 0.35rem;
            color: #B4BFAE;
        }

        .time-pill {
            padding: 0.38rem 0.72rem;
            border: 1px solid var(--border);
            border-radius: 999px;
            background: var(--surface);
            color: var(--muted);
            font-size: 0.7rem;
            font-weight: 700;
            white-space: nowrap;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
            margin: 1.2rem 0 1.7rem;
        }

        .metric-card {
            padding: 1.05rem 1.2rem 1.15rem;
            border: 1px solid var(--border);
            border-radius: 18px;
            background: var(--surface);
            box-shadow: 0 6px 20px rgba(45, 66, 38, 0.04);
        }

        .metric-card.total {
            border-color: var(--green-dark);
            background: var(--green-dark);
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.67rem;
            font-weight: 800;
            letter-spacing: 0.11em;
            text-transform: uppercase;
        }

        .metric-value {
            margin-top: 0.35rem;
            font-size: 2.45rem;
            font-weight: 800;
            line-height: 1;
            font-variant-numeric: tabular-nums;
        }

        .metric-card.total .metric-label { color: #D7E6CE; }
        .metric-card.total .metric-value { color: #FFFFFF; }
        .metric-card.good .metric-value { color: var(--green); }
        .metric-card.bad .metric-value { color: var(--red); }

        .image-label {
            margin: 0 0 0.45rem 2px;
            color: var(--muted);
            font-size: 0.67rem;
            font-weight: 800;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }

        [data-testid="stImage"] img {
            border: 1px solid var(--border);
            border-radius: 16px;
        }

        .legend-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.9rem;
            margin-top: 1rem;
            padding-top: 0.8rem;
            border-top: 1px solid var(--border);
        }

        .legend-items {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 600;
        }

        .legend-dot {
            display: inline-block;
            width: 9px;
            height: 9px;
            margin-right: 0.35rem;
            border-radius: 2px;
        }

        .legend-dot.whole { background: #3CC83C; }
        .legend-dot.broken { background: #DC2828; }

        .legend-meta {
            color: var(--muted);
            font-size: 0.73rem;
        }

        [data-testid="stExpander"] {
            margin-top: 1.6rem;
            border: 1px solid var(--border);
            border-radius: 16px;
            background: var(--surface);
        }

        [data-testid="stExpander"] summary { font-weight: 700; }

        [data-testid="stAlert"] { border-radius: 14px; }

        .site-footer {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 2rem;
            margin-top: 3.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
        }

        .footer-kicker {
            color: var(--green);
            font-size: 0.64rem;
            font-weight: 800;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }

        .footer-names {
            margin-top: 0.28rem;
            font-size: 0.92rem;
            font-weight: 700;
        }

        .footer-npm {
            margin-top: 0.18rem;
            color: var(--muted);
            font-size: 0.7rem;
            letter-spacing: 0.02em;
        }

        .footer-note {
            color: var(--muted);
            font-size: 0.7rem;
            line-height: 1.65;
            text-align: right;
        }

        @media (max-width: 820px) {
            .block-container {
                padding-top: 3.4rem;
            }

            .hero {
                grid-template-columns: 1fr;
                gap: 2rem;
                padding: 0.5rem 0 2.2rem;
            }

            .hero h1 {
                max-width: 14ch;
            }

            .hero-visual {
                max-width: 460px;
            }

            .metric-grid {
                grid-template-columns: 1fr 1fr;
            }

            .metric-card.total {
                grid-column: span 2;
            }

            .tips {
                grid-template-columns: 1fr;
            }

            .site-footer {
                align-items: flex-start;
                flex-direction: column;
                gap: 1.1rem;
            }

            .footer-note {
                text-align: left;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title=f"{PAGE_TITLE} | Kelompok 07",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_styles()

if "sample_path" not in st.session_state:
    st.session_state.sample_path = None

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
if DEMO_IMAGE is not None:
    try:
        hero_visual = f"""
        <figure class="hero-visual">
            <span class="photo-tag">Contoh input</span>
            <img src="{image_data_uri(DEMO_IMAGE)}" alt="Contoh foto butir kacang hijau di latar polos">
            <figcaption>Kacang hijau · latar polos · foto dari atas</figcaption>
        </figure>
        """
    except OSError:
        hero_visual = ""
else:
    hero_visual = ""

st.html(
    f"""
    <div class="hero">
        <div class="hero-copy">
            <div class="eyebrow">
                <span class="eyebrow-dot"></span>
                UTS Praktikum Visi Komputer · Kelompok 07
            </div>
            <h1>Penghitung Butir<br><em>Kacang Hijau</em></h1>
            <p class="lede">
                Unggah foto butir di latar polos. Pipeline OpenCV akan menghitung
                total butir, lalu memisahkan yang utuh dari yang patah berdasarkan
                luas area.
            </p>
            <div class="chips">
                <span class="chip">Tema 7</span>
                <span class="chip">OpenCV</span>
                <span class="chip">Otsu + Contour</span>
            </div>
        </div>
        {hero_visual}
    </div>
    """
)

# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------
st.html(
    """
    <div class="section-head">
        <span class="section-num">01</span>
        <div>
            <h2>Unggah gambar</h2>
            <p>Foto dari atas, latar polos, dan cahaya merata memberi hasil terbaik.</p>
        </div>
    </div>
    """
)

uploaded_file = st.file_uploader(
    "Pilih foto butir",
    type=["jpg", "jpeg", "png", "webp"],
    help=(
        "Gunakan foto dari atas dengan latar polos. Skala butir sebaiknya "
        "mirip contoh agar ambang luas tetap akurat."
    ),
)

action_col, sample_col = st.columns([3, 1.15])
with action_col:
    st.caption("Format JPG, PNG, atau WEBP · maksimal 50 MB")
with sample_col:
    if DEMO_IMAGE is not None and st.button("Coba contoh gambar", use_container_width=True):
        st.session_state.sample_path = str(DEMO_IMAGE)
        st.rerun()

if st.session_state.sample_path:
    sample_name = Path(st.session_state.sample_path).name
    st.html(
        f'<p class="sample-note">Menampilkan contoh <strong>{html.escape(sample_name)}</strong>. '
        "Unggah gambar di atas untuk menggantinya.</p>"
    )

# ---------------------------------------------------------------------------
# Proses gambar
# ---------------------------------------------------------------------------
input_image = None
source_name = ""

if uploaded_file is not None:
    st.session_state.sample_path = None
    try:
        input_image = load_uploaded_image(uploaded_file)
        source_name = uploaded_file.name
    except Exception:
        st.error(
            "Gambar tidak bisa dibaca. Coba file JPG, PNG, atau WEBP lain "
            "yang tidak rusak."
        )
elif st.session_state.sample_path:
    sample_path = Path(st.session_state.sample_path)
    if sample_path.exists():
        input_image = imread_unicode(sample_path)
        source_name = sample_path.name
        if input_image is None:
            st.error("Contoh gambar tidak bisa dibaca.")
    else:
        st.session_state.sample_path = None

if input_image is None:
    st.html(
        """
        <div class="empty-state">
            <div class="empty-kicker">Belum ada gambar</div>
            <h3>Mulai dengan satu foto butir</h3>
            <p>
                Unggah foto kacang hijau yang ditabur di latar polos. Butir yang
                terpisah dan tidak menumpuk memberi hasil paling akurat.
            </p>
            <div class="tips">
                <div class="tip">
                    <span>01</span>
                    <p><strong>Latar kontras.</strong> Gunakan kertas putih atau alas polos yang berbeda dengan warna butir.</p>
                </div>
                <div class="tip">
                    <span>02</span>
                    <p><strong>Foto dari atas.</strong> Jaga jarak kamera agar butir mengisi frame seperti contoh.</p>
                </div>
                <div class="tip">
                    <span>03</span>
                    <p><strong>Cahaya merata.</strong> Hindari bayangan keras yang bisa menyatukan butir.</p>
                </div>
            </div>
        </div>
        """
    )
else:
    try:
        with st.spinner("Menghitung butir..."):
            result = run_pipeline_image(input_image, name=source_name)
    except Exception as exc:
        st.error(f"Gagal memproses gambar: {exc}")
    else:
        total = int(result["total"])
        whole = int(result["whole"])
        broken = int(result["broken"])
        elapsed_ms = float(result["elapsed_ms"])
        threshold = (
            float(result["threshold"])
            if result["threshold"] is not None
            else float(result["params"]["manual_threshold"])
        )
        proc_h, proc_w = result["processed_shape"]

        st.html(
            f"""
            <div class="result-head">
                <div>
                    <div class="result-kicker">02 · Hasil deteksi</div>
                    <h2><strong>{total}</strong> butir terdeteksi</h2>
                    <p class="result-sub">
                        {whole} utuh <span class="sep">·</span>
                        {broken} patah/kecil <span class="sep">/</span>
                        {html.escape(source_name)}
                    </p>
                </div>
                <span class="time-pill">Selesai · {elapsed_ms:.0f} ms</span>
            </div>
            """
        )

        if total == 0:
            st.warning(
                "Tidak ada butir yang terdeteksi. Pastikan latar cukup kontras, "
                "butir tidak menumpuk, dan skala foto tidak terlalu kecil."
            )

        st.html(
            f"""
            <div class="metric-grid">
                <div class="metric-card total">
                    <div class="metric-label">Total butir</div>
                    <div class="metric-value">{total}</div>
                </div>
                <div class="metric-card good">
                    <div class="metric-label">Utuh</div>
                    <div class="metric-value">{whole}</div>
                </div>
                <div class="metric-card bad">
                    <div class="metric-label">Patah / kecil</div>
                    <div class="metric-value">{broken}</div>
                </div>
            </div>
            """
        )

        left, right = st.columns(2, gap="medium")
        with left:
            st.html('<div class="image-label">Gambar asli</div>')
            st.image(
                cv2.cvtColor(result["image"], cv2.COLOR_BGR2RGB),
                width="stretch",
            )
        with right:
            st.html('<div class="image-label">Hasil deteksi</div>')
            st.image(
                cv2.cvtColor(result["annotated"], cv2.COLOR_BGR2RGB),
                width="stretch",
            )

        st.html(
            f"""
            <div class="legend-row">
                <div class="legend-items">
                    <span><i class="legend-dot whole"></i>Utuh</span>
                    <span><i class="legend-dot broken"></i>Patah / kecil</span>
                </div>
                <span class="legend-meta">
                    Ambang luas {threshold:.1f} px² · diproses pada {proc_w} × {proc_h} px
                </span>
            </div>
            """
        )

# ---------------------------------------------------------------------------
# Penjelasan
# ---------------------------------------------------------------------------
with st.expander("Cara kerja & batasan"):
    st.markdown(
        """
**Pipeline**

1. Foto diperkecil sampai sisi terpanjang 1000 px.
2. Grayscale, normalisasi cahaya, lalu median blur untuk menekan noise.
3. Otsu threshold + morfologi memisahkan butir dari latar.
4. `findContours` + `contourArea` menemukan tiap butir; `minAreaRect`
   mengukur panjang dan lebarnya.
5. Butir dengan luas **≥ 264,875 px²** dianggap utuh, di bawahnya patah/kecil.

**Kalibrasi**

Ambang berasal dari median luas 603 butir pada 11 foto kondisi ideal
(407,5 px²), dikalikan faktor 0,65. Nilai ini sama dengan yang dipakai di
notebook `UTS_Kelompok07.ipynb`.

**Hasil evaluasi**

- 27 foto uji: 11 ideal, 5 cahaya, 5 rusak, 6 sulit.
- Akurasi hitung kondisi ideal: **98,4%**; 100% foto ideal lulus toleransi 10%.
- Rata-rata waktu proses di notebook: sekitar 150 ms per foto.

**Batasan**

Klasifikasi hanya memakai luas area, sehingga pecahan besar yang ukurannya
mendekati butir utuh bisa terbaca sebagai utuh. Butir yang saling menempel
atau menumpuk juga dapat menyatu menjadi satu kontur. Pipeline ini tidak
memakai deep learning.
        """
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.html(
    f"""
    <div class="site-footer">
        <div>
            <div class="footer-kicker">Kelompok 07 · UTS Praktikum Visi Komputer 2026</div>
            <div class="footer-names">{' · '.join(TEAM)}</div>
            <div class="footer-npm">{' · '.join(NPMS)}</div>
        </div>
        <div class="footer-note">
            OpenCV · NumPy · Streamlit<br>
            Tanpa deep learning
        </div>
    </div>
    """
)
