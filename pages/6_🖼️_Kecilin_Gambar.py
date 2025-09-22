# pages/6_🖼️_Kecilin_Gambar.py

import streamlit as st
from PIL import Image
import io
import os
import zipfile
from utils import clear_all_states, get_exif_data 

def process_image(img_bytes, original_filename, resize_method, params, output_format, jpeg_quality):
    """
    Mengubah ukuran dan format satu gambar, sambil mempertahankan DPI.
    """
    img = Image.open(io.BytesIO(img_bytes))
    original_format = img.format if img.format else "PNG"
    
    # --- PERBAIKAN: Baca info DPI dari gambar asli ---
    dpi_info = img.info.get('dpi')

    # Hitung dimensi baru
    original_width, original_height = img.size
    if resize_method == "Persentase":
        scale = params['scale'] / 100.0
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
    else: # Berdasarkan Dimensi Maksimal
        max_width = params['max_width']
        max_height = params['max_height']
        ratio = min(max_width / original_width, max_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)

    if new_width == 0 or new_height == 0:
        new_width, new_height = 1, 1

    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    final_output_format = output_format if output_format != "Sama seperti asli" else original_format
    
    output_buffer = io.BytesIO()
    file_extension = "png"
    save_params = {}

    # --- PERBAIKAN: Siapkan parameter DPI untuk disimpan ---
    if dpi_info:
        save_params['dpi'] = dpi_info

    if final_output_format.upper() == "JPEG":
        if resized_img.mode in ("RGBA", "P"):
            resized_img = resized_img.convert("RGB")
        save_params['quality'] = jpeg_quality
        resized_img.save(output_buffer, format="JPEG", **save_params)
        file_extension = "jpg"
    else:
        resized_img.save(output_buffer, format="PNG", **save_params)
        file_extension = "png"
        
    base_name = os.path.splitext(original_filename)[0]
    new_filename = f"resized_{base_name}.{file_extension}"
    return new_filename, output_buffer.getvalue()


# --- Tampilan Halaman Streamlit ---
st.set_page_config(page_title="Kecilin Gambar", layout="wide")
st.title("🖼️ Perkecil Resolusi & Ukuran Gambar")
st.markdown("Upload satu atau beberapa gambar untuk diubah ukurannya.")

uploaded_files = st.file_uploader(
    "Pilih gambar...",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
    key="image_resizer_uploader",
    on_change=clear_all_states
)

if uploaded_files:
    st.subheader("Info Gambar Asli")
    for file in uploaded_files:
        # Pindahkan seek(0) untuk memastikan file bisa dibaca ulang
        file.seek(0)
        img = Image.open(file)
        dpi = img.info.get('dpi', ('N/A', 'N/A'))
        dpi_x = dpi[0] if isinstance(dpi, tuple) else dpi
        st.markdown(f"- **{file.name}**: `{img.width} x {img.height}` pixel | Resolusi: `{dpi_x}` DPI")
        with st.expander(f"Detail untuk: {file.name}"):
            dpi = img.info.get('dpi', ('N/A', 'N/A'))
            dpi_x = dpi[0] if isinstance(dpi, tuple) else dpi
            st.markdown(f"- **Dimensi**: `{img.width} x {img.height}` pixel")
            st.markdown(f"- **Resolusi**: `{dpi_x}` DPI")
            
            # Panggil fungsi untuk baca metadata dan tampilkan
            st.markdown("- **Metadata Tambahan:**")
            exif_data = get_exif_data(img)
            st.json(exif_data)
    st.markdown("---")

    st.subheader("Opsi Pengecilan")
    resize_method = st.radio("Metode Ubah Ukuran:", ("Persentase", "Dimensi Maksimal"), horizontal=True)

    params = {}
    if resize_method == "Persentase":
        params['scale'] = st.slider("Skala Ukuran (%):", 1, 100, 50)
    else:
        col1, col2 = st.columns(2)
        with col1:
            params['max_width'] = st.number_input("Lebar Maksimal (pixel):", min_value=10, value=1024)
        with col2:
            params['max_height'] = st.number_input("Tinggi Maksimal (pixel):", min_value=10, value=1024)

    st.subheader("Opsi Output")
    col_fmt, col_q = st.columns(2)
    with col_fmt:
        output_format = st.selectbox("Format Output:", ("Sama seperti asli", "JPEG", "PNG"))
    with col_q:
        jpeg_quality = st.slider("Kualitas JPEG:", 1, 100, 85, disabled=(output_format != "JPEG"))

    st.markdown("---")
    
    if st.button(f"🚀 Proses {len(uploaded_files)} Gambar!", type="primary", use_container_width=True):
        with st.spinner("Sabar ya, lagi proses semua gambar... ⏳"):
            try:
                if len(uploaded_files) == 1:
                    uploaded_file = uploaded_files[0]
                    uploaded_file.seek(0)
                    new_filename, new_image_bytes = process_image(
                        uploaded_file.getvalue(), uploaded_file.name, resize_method, params, output_format, jpeg_quality
                    )
                    st.session_state.dl_resize_img_single = {"file_name": new_filename, "data": new_image_bytes}
                else:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for uploaded_file in uploaded_files:
                            uploaded_file.seek(0)
                            new_filename, new_image_bytes = process_image(
                                uploaded_file.getvalue(), uploaded_file.name, resize_method, params, output_format, jpeg_quality
                            )
                            zipf.writestr(new_filename, new_image_bytes)
                    st.session_state.dl_resize_img_zip = {"file_name": "gambar_resized.zip", "data": zip_buffer.getvalue()}

                st.success("Sip! Semua gambar berhasil diproses.")
                st.rerun()

            except Exception as e:
                st.error(f"Waduh, ada error, Bro: {e}")

if 'dl_resize_img_single' in st.session_state:
    info = st.session_state.dl_resize_img_single
    st.download_button(label=f"✅ Download {info['file_name']}", **info, use_container_width=True)

if 'dl_resize_img_zip' in st.session_state:
    info = st.session_state.dl_resize_img_zip
    st.download_button(label="✅ Download Semua Gambar (.zip)", **info, mime="application/zip", use_container_width=True)