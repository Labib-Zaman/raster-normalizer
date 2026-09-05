
import io
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

try:
    import rasterio
    from rasterio.io import MemoryFile
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

st.set_page_config(
    page_title="Raster Normalize",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --ink: #10233f;
    --muted: #66758a;
    --glass: rgba(255,255,255,.54);
    --glass-strong: rgba(255,255,255,.72);
    --line: rgba(255,255,255,.72);
    --blue: #147ef5;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background:
        radial-gradient(circle at 7% 12%, rgba(114,190,255,.30), transparent 27%),
        radial-gradient(circle at 92% 8%, rgba(191,226,255,.65), transparent 25%),
        radial-gradient(circle at 78% 85%, rgba(135,211,255,.28), transparent 28%),
        linear-gradient(135deg, #eef7ff 0%, #f8fbff 48%, #edf7ff 100%);
    color: var(--ink);
}
.stApp:before, .stApp:after {
    content: "";
    position: fixed;
    z-index: 0;
    border-radius: 50%;
    filter: blur(2px);
    pointer-events: none;
}
.stApp:before {
    width: 280px; height: 280px;
    left: -110px; bottom: 5%;
    background: rgba(111,180,255,.20);
}
.stApp:after {
    width: 360px; height: 360px;
    right: -160px; bottom: -100px;
    background: rgba(112,207,255,.16);
}
.block-container {
    max-width: 1180px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    position: relative;
    z-index: 1;
}
h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif;
    color: var(--ink);
}
h1 { letter-spacing: -.035em; }
.hero {
    position: relative;
    overflow: hidden;
    padding: 2.1rem 2.3rem;
    border: 1px solid var(--line);
    border-radius: 30px;
    background:
        linear-gradient(135deg, rgba(255,255,255,.72), rgba(226,243,255,.43)),
        radial-gradient(circle at 80% 20%, rgba(90,174,255,.25), transparent 32%);
    backdrop-filter: blur(28px) saturate(150%);
    -webkit-backdrop-filter: blur(28px) saturate(150%);
    box-shadow: 0 22px 60px rgba(44,100,150,.13), inset 0 1px 0 rgba(255,255,255,.9);
    margin-bottom: 1.25rem;
}
.hero:after {
    content: "";
    position: absolute;
    width: 190px; height: 190px;
    right: -55px; top: -75px;
    border-radius: 50%;
    background: rgba(255,255,255,.34);
    border: 1px solid rgba(255,255,255,.55);
}
.hero h1 {
    font-size: 2.65rem;
    margin: 0 0 .35rem 0;
}
.hero p {
    color: #52657d;
    font-size: 1.02rem;
    margin: 0;
}
.badge {
    display: inline-block;
    padding: .34rem .72rem;
    border-radius: 999px;
    background: rgba(255,255,255,.60);
    border: 1px solid rgba(255,255,255,.82);
    color: #1d6bc4;
    font-size: .73rem;
    font-weight: 700;
    letter-spacing: .06em;
    margin-bottom: .75rem;
    box-shadow: 0 5px 18px rgba(50,120,180,.08);
}
.id-pill {
    position: absolute;
    right: 22px;
    top: 20px;
    padding: .55rem .95rem;
    border-radius: 999px;
    background: rgba(255,255,255,.55);
    border: 1px solid rgba(255,255,255,.78);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    color: #18365b;
    font-weight: 700;
    font-size: .85rem;
    box-shadow: 0 8px 24px rgba(41,91,137,.10), inset 0 1px 0 rgba(255,255,255,.9);
}
.glass-card {
    background: rgba(255,255,255,.48);
    border: 1px solid rgba(255,255,255,.78);
    border-radius: 24px;
    backdrop-filter: blur(24px) saturate(145%);
    -webkit-backdrop-filter: blur(24px) saturate(145%);
    box-shadow: 0 14px 40px rgba(43,87,128,.08), inset 0 1px 0 rgba(255,255,255,.92);
}
.metric {
    background: rgba(255,255,255,.46);
    border: 1px solid rgba(255,255,255,.72);
    border-radius: 16px;
    padding: .8rem 1rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.8);
}
.metric .label {
    color: #718096;
    font-size: .72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .06em;
}
.metric .value {
    color: var(--ink);
    font-size: 1.05rem;
    font-weight: 700;
    margin-top: .15rem;
}
.formula {
    background: rgba(35,62,94,.92);
    color: #f5faff;
    padding: .85rem 1rem;
    border-radius: 14px;
    font-family: monospace;
    font-size: .88rem;
    border: 1px solid rgba(255,255,255,.18);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.12);
}
div[data-testid="stFileUploaderDropzone"] {
    border: 1.5px dashed rgba(56,139,220,.38);
    border-radius: 18px;
    background: rgba(255,255,255,.38);
}
.stButton > button, .stDownloadButton > button {
    border-radius: 14px;
    font-weight: 700;
    min-height: 2.8rem;
    border: 1px solid rgba(255,255,255,.78);
    background: rgba(255,255,255,.58);
    color: #12345b;
    box-shadow: 0 8px 22px rgba(35,93,145,.08), inset 0 1px 0 rgba(255,255,255,.9);
    backdrop-filter: blur(16px);
    transition: .18s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px);
    background: rgba(255,255,255,.78);
    box-shadow: 0 12px 28px rgba(35,93,145,.12);
}
[data-testid="stSidebar"] {
    background: rgba(244,250,255,.88);
    border-right: 1px solid rgba(255,255,255,.92);
    backdrop-filter: blur(28px) saturate(145%);
    -webkit-backdrop-filter: blur(28px) saturate(145%);
    box-shadow: 8px 0 30px rgba(45,88,130,.06);
}
[data-testid="stSidebar"] * {
    color: #17365d !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #102d50 !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small {
    color: #5b6f87 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,.78) !important;
    border: 1px solid rgba(110,150,190,.30) !important;
    border-radius: 12px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #17365d !important;
}
[data-testid="stSidebar"] [role="checkbox"] {
    color: #17365d !important;
}
[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}
.small-note {
    color: var(--muted);
    font-size: .88rem;
}
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    color: var(--ink);
    font-size: 1.08rem;
    margin: .8rem 0 .55rem;
}
.footer-id {
    text-align: right;
    color: #5f7590;
    font-size: .78rem;
    font-weight: 700;
    letter-spacing: .04em;
}
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def normalize_array(arr, method, low_pct=0.0, high_pct=100.0):
    """Normalize (bands, rows, cols), returning float32 and per-band stats."""
    data = arr.astype(np.float32, copy=True)
    out = np.full_like(data, np.nan, dtype=np.float32)
    stats = []

    for b in range(data.shape[0]):
        band = data[b]
        valid = np.isfinite(band)

        if not valid.any():
            stats.append({"min": np.nan, "max": np.nan, "mean": np.nan, "std": np.nan, "valid": 0})
            continue

        vals = band[valid]
        mn_raw = float(np.min(vals))
        mx_raw = float(np.max(vals))
        mean = float(np.mean(vals))
        std = float(np.std(vals))

        if low_pct > 0 or high_pct < 100:
            mn = float(np.percentile(vals, low_pct))
            mx = float(np.percentile(vals, high_pct))
        else:
            mn, mx = mn_raw, mx_raw

        if method == "Min-Max (0–1)":
            if mx == mn:
                out[b][valid] = 0.0
            else:
                out[b][valid] = (band[valid] - mn) / (mx - mn)
        elif method == "Min-Max (0–255)":
            if mx == mn:
                out[b][valid] = 0.0
            else:
                out[b][valid] = 255.0 * (band[valid] - mn) / (mx - mn)
        else:
            if std == 0:
                out[b][valid] = 0.0
            else:
                out[b][valid] = (band[valid] - mean) / std

        stats.append({"min": mn_raw, "max": mx_raw, "mean": mean, "std": std, "valid": int(valid.sum())})

    return out, stats


def display_image(data):
    """Create a safe 8-bit preview from (bands, rows, cols)."""
    data = np.asarray(data, dtype=np.float32)

    if data.ndim == 2:
        data = data[None, ...]

    bands = data.shape[0]

    def stretch(x):
        finite = np.isfinite(x)
        if not finite.any():
            return np.zeros_like(x, dtype=np.uint8)
        vals = x[finite]
        lo, hi = np.percentile(vals, [2, 98])
        if hi == lo:
            lo, hi = vals.min(), vals.max()
        if hi == lo:
            return np.zeros_like(x, dtype=np.uint8)
        y = np.clip((x - lo) / (hi - lo), 0, 1)
        y[~finite] = 0
        return (y * 255).astype(np.uint8)

    if bands == 1:
        return Image.fromarray(stretch(data[0]), mode="L")
    if bands >= 3:
        rgb = np.stack([stretch(data[0]), stretch(data[1]), stretch(data[2])], axis=-1)
        return Image.fromarray(rgb, mode="RGB")
    return Image.fromarray(stretch(data[0]), mode="L")


def read_raster(uploaded):
    suffix = Path(uploaded.name).suffix.lower()
    raw = uploaded.getvalue()

    if RASTERIO_AVAILABLE and suffix in {".tif", ".tiff"}:
        with MemoryFile(raw) as mem:
            with mem.open() as src:
                data = src.read().astype(np.float32)
                profile = src.profile.copy()
                nodata = src.nodata
                crs = src.crs
                transform = src.transform
                descriptions = src.descriptions
                tags = src.tags()
        if nodata is not None:
            data[data == nodata] = np.nan
        return data, profile, nodata, crs, transform, descriptions, tags

    img = Image.open(io.BytesIO(raw))
    arr = np.asarray(img).astype(np.float32)

    # Fix the original error: Pillow can return HxWx4 (RGBA) arrays.
    # Convert all image layouts into rasterio-style (bands, rows, cols).
    if arr.ndim == 2:
        data = arr[None, ...]
    elif arr.ndim == 3:
        # H x W x C -> C x H x W
        data = np.moveaxis(arr, -1, 0)
    else:
        raise ValueError(f"Unsupported image dimensions: {arr.shape}")

    return data, None, None, None, None, None, {}


def write_geotiff(data, profile, nodata_value=-9999.0):
    out = np.where(np.isfinite(data), data, nodata_value).astype(np.float32)

    if RASTERIO_AVAILABLE:
        if profile is None:
            profile = {
                "driver": "GTiff",
                "height": out.shape[1],
                "width": out.shape[2],
                "count": out.shape[0],
                "dtype": "float32",
            }
        else:
            profile = profile.copy()
            profile.update(
                driver="GTiff",
                dtype="float32",
                count=out.shape[0],
                height=out.shape[1],
                width=out.shape[2],
                nodata=nodata_value,
                compress="deflate",
                predictor=2,
            )

        mem = io.BytesIO()
        with MemoryFile() as mf:
            with mf.open(**profile) as dst:
                dst.write(out)
            mem.write(mf.read())
        return mem.getvalue()

    # Fallback: Pillow can write a single float band, but not a multi-band float TIFF reliably.
    if out.shape[0] == 1:
        img = Image.fromarray(out[0], mode="F")
        buf = io.BytesIO()
        img.save(buf, format="TIFF")
        return buf.getvalue()
    raise RuntimeError("Rasterio is required for multi-band TIFF export.")


# ---------- Header ----------
st.markdown("""
<div class="hero">
  <div class="id-pill">ID: 230430</div>
  <div class="badge">GIS</div>
  <h1>Raster Normalize</h1>
  <p>Normalize raster pixel values in your browser — preview the result and export a GIS-ready GeoTIFF.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ⚙️ Normalization")
    method = st.selectbox(
        "Method",
        ["Min-Max (0–1)", "Min-Max (0–255)", "Z-score (mean 0, SD 1)"],
    )

    st.markdown("**Percentile clipping**")
    use_clip = st.checkbox("Ignore extreme values", value=False)
    if use_clip:
        low_pct = st.slider("Lower percentile", 0.0, 20.0, 2.0, 0.5)
        high_pct = st.slider("Upper percentile", 80.0, 100.0, 98.0, 0.5)
    else:
        low_pct, high_pct = 0.0, 100.0

    st.markdown("---")
    st.markdown("### 🗺️ Output")
    st.caption("Values are normalized band-by-band. GeoTIFF CRS, transform, NoData and metadata are preserved when Rasterio is available.")

    if method == "Min-Max (0–1)":
        formula = "(x − min) / (max − min)"
    elif method == "Min-Max (0–255)":
        formula = "255 × (x − min) / (max − min)"
    else:
        formula = "(x − mean) / standard deviation"

    st.markdown("**Formula**")
    st.markdown(f'<div class="formula">{formula}</div>', unsafe_allow_html=True)

# ---------- Upload ----------
st.markdown("### 1. Upload raster")
uploaded = st.file_uploader(
    "Drag & drop your raster here",
    type=["tif", "tiff", "png", "jpg", "jpeg", "bmp"],
    help="GeoTIFF is recommended for GIS work.",
)

if not uploaded:
    st.markdown("""
    <div class="card">
        <h3>Start with a raster</h3>
        <p class="small-note">
        Supported: GeoTIFF, TIFF, PNG, JPG, JPEG and BMP. For spatial analysis,
        use GeoTIFF so coordinate reference information can be retained.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

try:
    data, profile, nodata, crs, transform, descriptions, tags = read_raster(uploaded)

    # Show metadata cards
    rows, cols = data.shape[1], data.shape[2]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric"><div class="label">Bands</div><div class="value">{data.shape[0]}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric"><div class="label">Dimensions</div><div class="value">{cols:,} × {rows:,}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric"><div class="label">Data type</div><div class="value">{data.dtype}</div></div>', unsafe_allow_html=True)
    with c4:
        crs_text = str(crs) if crs else "Not georeferenced"
        st.markdown(f'<div class="metric"><div class="label">CRS</div><div class="value">{crs_text}</div></div>', unsafe_allow_html=True)

    st.markdown("### 2. Compare")
    before_col, after_col = st.columns(2)

    with before_col:
        st.markdown("**Original raster**")
        st.image(display_image(data), use_container_width=True)

    normalized, stats = normalize_array(data, method, low_pct, high_pct)

    with after_col:
        st.markdown("**Normalized raster**")
        st.image(display_image(normalized), use_container_width=True)

    st.markdown("### 3. Band statistics")
    import pandas as pd
    table = []
    for i, s in enumerate(stats):
        table.append({
            "Band": i + 1,
            "Original min": s["min"],
            "Original max": s["max"],
            "Mean": s["mean"],
            "Std. dev.": s["std"],
            "Valid pixels": s["valid"],
        })
    st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)

    # Downloads
    st.markdown("### 4. Export")
    tiff_bytes = write_geotiff(normalized, profile)

    # Preview PNG is deliberately a visual product, not the analytical raster.
    preview = display_image(normalized)
    png_buf = io.BytesIO()
    preview.save(png_buf, format="PNG")

    base = Path(uploaded.name).stem

    def size_label(n):
        if n >= 1024**3:
            return f"{n / 1024**3:.1f}GB"
        if n >= 1024**2:
            return f"{n / 1024**2:.1f}MB"
        if n >= 1024:
            return f"{n / 1024:.1f}KB"
        return f"{n}B"

    # Requested output naming:
    # Original file name_Normalized_file size_id
    tiff_size = size_label(len(tiff_bytes))
    png_size = size_label(len(png_buf.getvalue()))
    tiff_name = f"{base}_Normalized_{tiff_size}_230430.tif"
    png_name = f"{base}_Normalized_{png_size}_230430.png"

    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "⬇️ Download normalized GeoTIFF",
            data=tiff_bytes,
            file_name=tiff_name,
            mime="image/tiff",
            use_container_width=True,
        )
        st.caption(tiff_name)
    with d2:
        st.download_button(
            "⬇️ Download preview PNG",
            data=png_buf.getvalue(),
            file_name=png_name,
            mime="image/png",
            use_container_width=True,
        )
        st.caption(png_name)

    st.success("Normalization complete. The GeoTIFF contains the normalized numeric values; the PNG is for visual display.")

except Exception as e:
    st.error(f"Could not process this raster: {e}")
    st.info("If this is a GeoTIFF, make sure Rasterio is installed. The included requirements.txt installs it.")

st.markdown("---")
st.markdown('<div class="footer-id">RASTER NORMALIZE • ID: 230430</div>', unsafe_allow_html=True)
