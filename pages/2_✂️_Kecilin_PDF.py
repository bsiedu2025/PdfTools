# pages/2_✂️_Kecilin_PDF.py

import streamlit as st
import os
import tempfile
from utils import compress_pdf_ghostscript, clear_all_states

st.set_page_config(page_title="Kecilin PDF", layout="wide")
st.title("✂️ Aplikasi Pengecil Ukuran PDF Super")
st.markdown("Upload PDF-mu dan pilih level kompresi. Makin kecil, kualitas gambar mungkin makin turun ya! 😉")

# --- OPSI KOMPRESI BARU YANG LEBIH ADVANCE ---
quality_options_detailed = {
    "1. Ebook (Optimal)": {
        "description": "Kualitas baik, ukuran sedang (~150dpi). Pilihan seimbang terbaik.",
        "pdf_settings": "ebook",
        "params": []
    },
    "2. Standar (Kecil)": {
        "description": "Kualitas cukup, ukuran kecil (~72dpi). Pas buat kirim email.",
        "pdf_settings": "screen",
        "params": []
    },
    "3. Sangat Kecil (Agresif)": {
        "description": "Ukuran jadi kecil banget! Kualitas gambar diturunkan jadi 72dpi.",
        "pdf_settings": "screen",
        "params": [
            "-dColorImageResolution=72",
            "-dGrayImageResolution=72",
            "-dMonoImageResolution=72"
        ]
    },
    "4. Ekstrem (Gambar Hancur)": {
        "description": "Level paling ganas! Ukuran super mini, kualitas gambar anjlok (resolusi rendah, kompresi JPEG tinggi).",
        "pdf_settings": "screen",
        "params": [
            "-dColorImageResolution=50",
            "-dGrayImageResolution=50",
            "-dMonoImageResolution=50",
            "-dJPEGQ=20" # Kualitas JPEG sangat rendah
        ]
    },
    "Lainnya: Kualitas Cetak (Besar)": {
        "description": "Kualitas gambar bagus buat dicetak (~300dpi). Ukuran file biasanya lebih besar.",
        "pdf_settings": "printer",
        "params": []
    }
}

uploaded_file = st.file_uploader(
    "Pilih PDF yang mau dikecilin...",
    type="pdf",
    key="compress_uploader",
    on_change=clear_all_states
)

if uploaded_file:
    original_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    st.info(f"File: **{uploaded_file.name}** | Ukuran Asli: **{original_size_mb:.2f} MB**")

    # Selectbox dengan pilihan yang lebih detail
    selected_quality_label = st.selectbox(
        "Pilih Level Kompresi:",
        options=list(quality_options_detailed.keys()),
        index=0
    )
    # Tampilkan deskripsi untuk level yang dipilih
    st.caption(quality_options_detailed[selected_quality_label]["description"])

    if st.button("🚀 Gaskeun Kecilin!", type="primary", use_container_width=True):
        selected_config = quality_options_detailed[selected_quality_label]
        input_path, output_path = None, None
        try:
            with st.spinner("Sabar ya, lagi di-press... ⏳"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
                    tmp_in.write(uploaded_file.getvalue())
                    input_path = tmp_in.name
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_out:
                    output_path = tmp_out.name
                
                # Panggil fungsi kompresi dengan parameter advance
                success, msg, _ = compress_pdf_ghostscript(
                    input_path,
                    output_path,
                    selected_config["pdf_settings"],
                    selected_config["params"]
                )
                
                if success and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    with open(output_path, "rb") as f:
                        st.session_state.dl_compress = {
                            "file_name": f"kecil_{uploaded_file.name}",
                            "data": f.read()
                        }
                    st.success("Berhasil dikecilin!")
                    st.rerun()
                else:
                    st.error(f"Gagal, Bro: {msg}")
        finally:
            if input_path and os.path.exists(input_path): os.remove(input_path)
            if output_path and os.path.exists(output_path): os.remove(output_path)

if 'dl_compress' in st.session_state:
    info = st.session_state.dl_compress
    new_size_mb = len(info["data"]) / (1024 * 1024)
    st.success(f"Mantap! Ukuran baru: **{new_size_mb:.2f} MB**")
    st.download_button(
        "✅ Download PDF Kecilnya",
        **info,
        mime="application/pdf",
        use_container_width=True
    )