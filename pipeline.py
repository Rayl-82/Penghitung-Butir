"""Pipeline penghitung butir kacang hijau (Tema 7).

Fungsi-fungsi di modul ini adalah versi yang dipakai ulang oleh aplikasi
Streamlit. Logikanya sama dengan notebook UTS_Kelompok07.ipynb:

    resize -> grayscale -> normalisasi cahaya -> median blur -> Otsu
    -> morfologi -> kontur -> minAreaRect -> klasifikasi luas.

Tidak ada model deep learning. Klasifikasi utuh/patah memakai ambang luas
yang dikalibrasi dari kondisi foto ideal:

    ambang = 0.65 x median luas butir pada 11 foto ideal
           = 0.65 x 407.5 px^2
           = 264.875 px^2
"""

from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Nilai kalibrasi dari notebook (sel "Kalibrasi ambang klasifikasi").
AREA_REFERENCE = 407.5
CALIB_FACTOR = 0.65
DEFAULT_THRESHOLD = CALIB_FACTOR * AREA_REFERENCE

PARAMS = {
    "resize_max": 1000,          # sisi terpanjang citra (aturan: 800-1200 px)
    "illum_norm": True,          # normalisasi pencahayaan sebelum threshold
    "illum_sigma": 25,           # sigma blur besar untuk normalisasi cahaya
    "blur_method": "median",     # "median" | "gaussian" | "none"
    "ksize": 5,                  # ukuran kernel blur (harus ganjil)
    "threshold_method": "otsu",  # "otsu" | "adaptive"
    "adaptive_block": 51,        # blockSize adaptive (ganjil, > 1)
    "adaptive_C": 7,             # konstanta C adaptive threshold
    "invert": "auto",            # "auto" | True | False
    "jenis_butir": "kacang ijo", # dipakai fallback auto_invert, sama seperti notebook
    "min_area": 40,              # luas minimum kontur (px^2) setelah resize
    "max_area_ratio": 0.10,      # kontur > 10% luas citra diabaikan
    "classify_by": "area",       # "area" | "length" (pemisahan utuh/patah)
    "calib_factor": CALIB_FACTOR,
    "area_reference": AREA_REFERENCE,
    "split_min_ratio": None,     # pengaman k-means bila tanpa kalibrasi
    "min_cluster_frac": 0.08,    # tiap klaster minimal 8% objek
    "manual_threshold": DEFAULT_THRESHOLD,
}


def imread_unicode(path: str | Path) -> np.ndarray | None:
    """Membaca citra, termasuk path dengan karakter non-ASCII."""
    path = str(path)
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        try:
            buf = np.fromfile(path, dtype=np.uint8)
            img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        except Exception:
            img = None
    return img


def resize_longest(img: np.ndarray, target: int = 1000) -> np.ndarray:
    """Perkecil citra agar sisi terpanjang <= target (tidak memperbesar)."""
    h, w = img.shape[:2]
    scale = float(target) / float(max(h, w))
    if scale < 1.0:
        img = cv2.resize(
            img,
            (int(round(w * scale)), int(round(h * scale))),
            interpolation=cv2.INTER_AREA,
        )
    return img


def apply_blur(gray: np.ndarray, method: str = "median", ksize: int = 5) -> np.ndarray:
    """Blur untuk menekan noise sebelum thresholding."""
    k = int(ksize)
    if k % 2 == 0:
        k += 1
    if method == "median":
        return cv2.medianBlur(gray, k)
    if method == "gaussian":
        return cv2.GaussianBlur(gray, (k, k), 0)
    if method == "none":
        return gray.copy()
    raise ValueError(f"blur_method tidak dikenal: {method}")


def apply_illum_norm(gray: np.ndarray, sigma: float = 25, target: int = 180) -> np.ndarray:
    """Normalisasi pencahayaan (flat-field).

    Citra dibagi dengan versi blur besar sehingga gradien cahaya/bayangan
    yang landai ikut terhapus dan Otsu tetap dapat memisahkan butir dari
    latar walau cahaya tidak merata.
    """
    bg = cv2.GaussianBlur(gray.astype(np.float32), (0, 0), sigmaX=float(sigma))
    bg = np.maximum(bg, 1.0)
    norm = gray.astype(np.float32) / bg
    norm = np.clip(norm * float(target), 0, 255).astype(np.uint8)
    return norm


def auto_invert(mask: np.ndarray, jenis_butir: str = "kacang ijo") -> bool:
    """True jika kelas putih pada mask justru latar.

    Butir selalu minoritas piksel, jadi jika kelas putih menutupi > 55%
    citra, putih adalah latar dan mask harus di-invert. Aturan tepi citra
    tidak dipakai karena vignetting pencahayaan HP membuat tepi citra gelap
    walau latar terang.
    """
    white_ratio = float((mask > 0).mean())
    if white_ratio >= 0.55:
        return True
    if white_ratio <= 0.45:
        return False
    return str(jenis_butir).lower() in (
        "kopi",
        "kacang",
        "kacang hijau",
        "kacang tanah",
    )


def segment(
    gray: np.ndarray,
    method: str = "otsu",
    adaptive_block: int = 51,
    adaptive_C: int = 7,
    invert: str | bool = "auto",
    morph: bool = True,
    jenis_butir: str = "kacang ijo",
) -> np.ndarray:
    """Segmentasi butir (foreground putih) menjadi mask biner 0/255."""
    if method == "otsu":
        _, mask = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
    elif method == "adaptive":
        block = int(adaptive_block)
        if block % 2 == 0:
            block += 1
        block = max(3, block)
        mask = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block,
            float(adaptive_C),
        )
    else:
        raise ValueError(f"threshold_method tidak dikenal: {method}")

    if invert == "auto":
        if auto_invert(mask, jenis_butir):
            mask = cv2.bitwise_not(mask)
    elif bool(invert):
        mask = cv2.bitwise_not(mask)

    if morph:
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    return mask


def extract_objects(
    mask: np.ndarray,
    min_area: float = 40,
    max_area_ratio: float = 0.05,
) -> list[dict]:
    """Cari kontur butir dan hitung fiturnya.

    Fitur: luas (contourArea), panjang & lebar (minAreaRect), solidity.
    """
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    h, w = mask.shape[:2]
    max_area = max_area_ratio * h * w
    objects = []

    for contour in contours:
        area = float(cv2.contourArea(contour))
        if area < min_area or area > max_area:
            continue

        rect = cv2.minAreaRect(contour)          # ((cx, cy), (w, h), angle)
        rw, rh = rect[1]
        if rw <= 0 or rh <= 0:
            continue

        length = float(max(rw, rh))
        width = float(min(rw, rh))
        hull_area = float(cv2.contourArea(cv2.convexHull(contour)))
        solidity = area / hull_area if hull_area > 0 else 0.0
        x, y, bw, bh = cv2.boundingRect(contour)

        objects.append(
            {
                "contour": contour,
                "area": area,
                "length": length,
                "width": width,
                "aspect": length / max(width, 1e-6),
                "solidity": solidity,
                "rect": rect,
                "bbox": (x, y, bw, bh),
                "center": (int(rect[0][0]), int(rect[0][1])),
            }
        )

    return objects


def _kmeans_1d(values: np.ndarray, iters: int = 60) -> tuple[np.ndarray, np.ndarray]:
    """K-means 1 dimensi untuk 2 klaster (implementasi numpy)."""
    v = np.asarray(values, dtype=np.float64).reshape(-1, 1)
    centers = np.array([[float(v.min())], [float(v.max())]], dtype=np.float64)
    labels = np.zeros(len(v), dtype=int)

    for _ in range(iters):
        dist = np.abs(v - centers.reshape(1, 2))
        new_labels = np.argmin(dist, axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        for j in range(2):
            if np.any(labels == j):
                centers[j, 0] = float(v[labels == j].mean())

    return centers.ravel(), labels


def classify_objects(
    objects: list[dict],
    by: str = "area",
    manual_threshold: float | None = None,
    split_min_ratio: float | None = None,
    min_cluster_frac: float = 0.08,
) -> tuple[float | None, dict]:
    """Pisahkan butir utuh vs patah.

    Utama: jika manual_threshold diisi (hasil kalibrasi dari kondisi ideal),
    klasifikasi hanya membandingkan luas/panjang objek dengan ambang tetap.

    Fallback: bila tanpa kalibrasi, dipakai 2 klaster k-means pada log(luas)
    atau log(panjang); klaster bernilai lebih besar = butir utuh.
    """
    if not objects:
        return None, {"split": False, "reason": "tidak ada objek", "ratio": None}

    if by == "area":
        values = np.array([o["area"] for o in objects], dtype=np.float64)
        auto_ratio = 1.6
    elif by == "length":
        values = np.array([o["length"] for o in objects], dtype=np.float64)
        auto_ratio = 1.25
    else:
        raise ValueError("classify_by harus 'area' atau 'length'")

    if manual_threshold is not None:
        threshold = float(manual_threshold)
        for obj, value in zip(objects, values):
            obj["whole"] = bool(value >= threshold)
        return threshold, {
            "split": True,
            "reason": "ambang kalibrasi",
            "ratio": None,
        }

    if len(values) < 4 or np.isclose(values.min(), values.max()):
        for obj in objects:
            obj["whole"] = True
        return None, {
            "split": False,
            "reason": "objek terlalu sedikit/seragam",
            "ratio": None,
        }

    logv = np.log1p(values)
    centers, labels = _kmeans_1d(logv)
    low = float(min(centers))
    high = float(max(centers))
    ratio = float(np.expm1(high) / max(np.expm1(low), 1e-6))
    frac_low = float(np.mean(labels == int(np.argmin(centers))))
    min_ratio = float(split_min_ratio) if split_min_ratio is not None else auto_ratio

    if ratio < min_ratio or not (min_cluster_frac <= frac_low <= 1 - min_cluster_frac):
        for obj in objects:
            obj["whole"] = True
        return None, {
            "split": False,
            "reason": f"rasio {ratio:.2f} < {min_ratio:.2f} / klaster tidak seimbang",
            "ratio": ratio,
        }

    threshold = float(np.expm1((low + high) / 2.0))
    for obj, value in zip(objects, values):
        obj["whole"] = bool(value >= threshold)
    return threshold, {
        "split": True,
        "reason": "k-means 2 klaster",
        "ratio": ratio,
    }


def draw_results(
    img: np.ndarray,
    objects: list[dict],
    threshold: float | None = None,
    by: str = "area",
) -> np.ndarray:
    """Gambar kotak minAreaRect + ringkasan jumlah pada citra."""
    out = img.copy()
    n_whole = sum(1 for obj in objects if obj["whole"])
    n_broken = len(objects) - n_whole

    for obj in objects:
        color = (60, 200, 60) if obj["whole"] else (40, 40, 220)  # BGR
        box = cv2.boxPoints(obj["rect"])
        cv2.drawContours(out, [np.round(box).astype(np.int32)], 0, color, 2)
        cv2.circle(out, obj["center"], 2, color, -1)

    text = f"Total: {len(objects)} | Utuh: {n_whole} | Patah: {n_broken}"
    cv2.putText(
        out,
        text,
        (12, 34),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        4,
        cv2.LINE_AA,
    )
    cv2.putText(
        out,
        text,
        (12, 34),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (20, 20, 20),
        1,
        cv2.LINE_AA,
    )

    if threshold is not None:
        label = f"ambang {by}: {threshold:.1f}"
        y = out.shape[0] - 14
        cv2.putText(
            out,
            label,
            (12, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            3,
            cv2.LINE_AA,
        )
        cv2.putText(
            out,
            label,
            (12, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (20, 20, 20),
            1,
            cv2.LINE_AA,
        )
    return out


def run_pipeline_image(
    image: np.ndarray,
    params: dict | None = None,
    verbose: bool = False,
    name: str = "gambar",
) -> dict:
    """Jalankan seluruh pipeline pada array citra BGR."""
    if image is None or getattr(image, "size", 0) == 0:
        raise ValueError("Citra kosong atau tidak terbaca.")

    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.ndim == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    p = dict(PARAMS)
    if params:
        p.update(params)

    t0 = time.perf_counter()
    original_shape = image.shape[:2]
    working = resize_longest(image.copy(), p["resize_max"])
    gray = cv2.cvtColor(working, cv2.COLOR_BGR2GRAY)
    norm = (
        apply_illum_norm(gray, p["illum_sigma"])
        if p.get("illum_norm", True)
        else gray
    )
    blur = apply_blur(norm, p["blur_method"], p["ksize"])
    mask = segment(
        blur,
        p["threshold_method"],
        p["adaptive_block"],
        p["adaptive_C"],
        p["invert"],
        jenis_butir=p.get("jenis_butir", "kacang ijo"),
    )
    objects = extract_objects(mask, p["min_area"], p["max_area_ratio"])
    threshold, info = classify_objects(
        objects,
        p["classify_by"],
        p["manual_threshold"],
        p["split_min_ratio"],
        p["min_cluster_frac"],
    )
    annotated = draw_results(working, objects, threshold, p["classify_by"])
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    n_whole = sum(1 for obj in objects if obj["whole"])

    if verbose:
        print(
            f"{name}: total={len(objects)}, utuh={n_whole}, "
            f"patah={len(objects) - n_whole}, waktu={elapsed_ms:.1f} ms"
        )

    return {
        "file": name,
        "path": None,
        "image": working,
        "gray": gray,
        "norm": norm,
        "blur": blur,
        "mask": mask,
        "objects": objects,
        "annotated": annotated,
        "threshold": threshold,
        "info": info,
        "total": len(objects),
        "whole": n_whole,
        "broken": len(objects) - n_whole,
        "elapsed_ms": elapsed_ms,
        "original_shape": original_shape,
        "processed_shape": working.shape[:2],
        "params": p,
    }


def run_pipeline(
    path: str | Path,
    params: dict | None = None,
    verbose: bool = False,
) -> dict:
    """Jalankan seluruh pipeline pada satu file citra."""
    original = imread_unicode(path)
    if original is None:
        raise FileNotFoundError(f"Citra tidak terbaca: {path}")

    result = run_pipeline_image(
        original,
        params=params,
        verbose=verbose,
        name=Path(path).name,
    )
    result["path"] = Path(path)
    return result
