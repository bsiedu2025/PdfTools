# pages/7_🎨_Editor_Foto_Lengkap.py

import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import io
import os
from utils import clear_all_states

st.set_page_config(page_title="Editor Foto Lengkap", layout="wide")

# --- Fungsi Bantuan untuk Halaman Ini ---
def apply_enhancement(image, enhancement, factor):
    """Menerapkan peningkat kecerahan, kontras, dll."""
    enhancers = {
        "Kecerahan": ImageEnhance.Brightness,
        "Kontras": ImageEnhance.Contrast,
        "Ketajaman": ImageEnhance.Sharpness,
        "Warna": ImageEnhance.Color,
    }
    if enhancement in enhancers:
        enhancer = enhancers[enhancement](image)
        return enhancer.enhance(factor)
    return image

def apply_filter(image, filter_name):
    """Menerapkan filter gambar."""
    filters = {
        "BLUR": ImageFilter.BLUR,
        "CONTOUR": ImageFilter.CONTOUR,
        "DETAIL": ImageFilter.DETAIL,
        "EDGE_ENHANCE": ImageFilter.EDGE_ENHANCE,
        "EDGE_ENHANCE_MORE": ImageFilter.EDGE_ENHANCE_MORE,
        "EMBOSS": ImageFilter.EMBOSS,
        "FIND_EDGES": ImageFilter.FIND_EDGES,
        "SHARPEN": ImageFilter.SHARPEN,
        "SMOOTH": ImageFilter.SMOOTH,
        "SMOOTH_MORE": ImageFilter.SMOOTH_MORE,
    }
    if filter_name in filters:
        return image.filter(filters[filter_name])
    return image

# --- Tampilan Utama Aplikasi ---
st.title("🎨 Editor Foto Lengkap")
st.markdown("Upload satu gambar lalu gunakan semua alat di sidebar kiri untuk mengedit.")

# Inisialisasi session state untuk menyimpan gambar
if 'edited_image' not in st.session_state:
    st.session_state.edited_image = None
if 'original_image' not in st.session_state:
    st.session_state.original_image = None

# Fungsi untuk mereset semua state saat file baru diupload
def reset_image_states():
    st.session_state.edited_image = None
    st.session_state.original_image = None
    clear_all_states()

uploaded_file = st.file_uploader(
    "Upload satu gambar untuk diedit...",
    type=["png", "jpg", "jpeg"],
    key="editor_uploader",
    on_change=reset_image_states
)

# Jika ada file baru diupload, set state awal
if uploaded_file is not None and st.session_state.original_image is None:
    st.session_state.original_image = Image.open(uploaded_file).convert("RGBA")
    st.session_state.edited_image = st.session_state.original_image.copy()

# --- Sidebar untuk Kontrol Edit ---
with st.sidebar:
    st.header("Alat Editor")
    if st.session_state.edited_image is not None:
        # --- Bagian Transformasi ---
        with st.expander("🔄 Transformasi", expanded=True):
            if st.button("Putar Kiri 90°", use_container_width=True):
                st.session_state.edited_image = st.session_state.edited_image.rotate(90, expand=True)
                st.rerun()
            if st.button("Putar Kanan 90°", use_container_width=True):
                st.session_state.edited_image = st.session_state.edited_image.rotate(-90, expand=True)
                st.rerun()
            if st.button("Balik Horizontal", use_container_width=True):
                st.session_state.edited_image = st.session_state.edited_image.transpose(Image.FLIP_LEFT_RIGHT)
                st.rerun()
            if st.button("Balik Vertikal", use_container_width=True):
                st.session_state.edited_image = st.session_state.edited_image.transpose(Image.FLIP_TOP_BOTTOM)
                st.rerun()

        # --- Bagian Penyesuaian Warna ---
        with st.expander("🎨 Penyesuaian Warna"):
            brightness = st.slider("Kecerahan", 0.1, 3.0, 1.0, 0.1)
            contrast = st.slider("Kontras", 0.1, 3.0, 1.0, 0.1)
            color = st.slider("Warna", 0.0, 3.0, 1.0, 0.1)
            
            if st.button("Terapkan Penyesuaian Warna", use_container_width=True):
                img = st.session_state.edited_image
                img = apply_enhancement(img, "Kecerahan", brightness)
                img = apply_enhancement(img, "Kontras", contrast)
                img = apply_enhancement(img, "Warna", color)
                st.session_state.edited_image = img
                st.rerun()
        
        # --- Bagian Filter ---
        with st.expander("✨ Filter Gambar"):
            filter_name = st.selectbox("Pilih Filter", ["NONE", "BLUR", "CONTOUR", "DETAIL", "EDGE_ENHANCE", "EMBOSS", "SHARPEN", "SMOOTH"])
            if st.button("Terapkan Filter", use_container_width=True):
                if filter_name != "NONE":
                    st.session_state.edited_image = apply_filter(st.session_state.edited_image, filter_name)
                    st.rerun()
        
        # --- Bagian Mode Gambar ---
        with st.expander("⚪ Mode Gambar"):
             if st.button("Ubah ke Grayscale (Hitam Putih)", use_container_width=True):
                 st.session_state.edited_image = st.session_state.edited_image.convert("L").convert("RGBA")
                 st.rerun()

        # --- Tombol Reset & Download ---
        st.markdown("---")
        if st.button("Reset ke Gambar Asli", use_container_width=True):
            st.session_state.edited_image = st.session_state.original_image.copy()
            st.rerun()
        
        # Siapkan file untuk di-download
        buf = io.BytesIO()
        st.session_state.edited_image.save(buf, format="PNG")
        st.download_button(
            "✅ Download Hasil Edit",
            data=buf.getvalue(),
            file_name=f"edit_{uploaded_file.name}.png",
            mime="image/png",
            use_container_width=True
        )
    else:
        st.info("Upload gambar dulu di area utama untuk memulai.")


# --- Area Utama untuk Menampilkan Gambar ---
if st.session_state.edited_image:
    st.image(st.session_state.edited_image, caption="Gambar Hasil Edit", use_container_width=True)
else:
    st.info("Area ini akan menampilkan gambar yang sedang lo edit.")