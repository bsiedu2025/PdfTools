import streamlit as st
import numpy as np
import io
import os
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from rembg import remove
from utils import extract_pdf_previews, add_signature_to_pdf, clear_all_states
import fitz

st.set_page_config(page_title="Paraf PDF", layout="wide")
st.title("✍️ Paraf PDF Digital")

uploaded_pdf = st.file_uploader("Langkah 1: Pilih PDF", type="pdf", key="sign_pdf_uploader", on_change=clear_all_states)
if not uploaded_pdf:
    st.info("Upload PDF dulu, Bro.")
    st.stop()

pdf_bytes = uploaded_pdf.getvalue()
st.subheader("Langkah 2: Siapin Paraf Lo")
if 'signature_bytes' not in st.session_state:
    st.session_state.signature_bytes = None

tab1, tab2 = st.tabs(["✍️ Gambar Langsung", "🖼️ Upload Gambar Paraf"])
with tab1:
    col_canvas, col_config = st.columns([2, 1])
    with col_config:
        stroke_width = st.slider("Tebal Garis:", 1, 25, 3)
        stroke_color = st.color_picker("Warna Tinta:", "#000000")
    with col_canvas:
        canvas_result = st_canvas(stroke_width=stroke_width, stroke_color=stroke_color, background_color="#FFFFFF", height=200, width=400, drawing_mode="freedraw", key="canvas_draw")
    if st.button("Gunakan Gambar dari Kanvas"):
        if canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            img_array = np.array(img); white_pixels = (img_array[:, :, 0] > 240) & (img_array[:, :, 1] > 240) & (img_array[:, :, 2] > 240); img_array[white_pixels, 3] = 0
            transparent_img = Image.fromarray(img_array)
            if bbox := transparent_img.getbbox():
                buffer = io.BytesIO(); transparent_img.crop(bbox).save(buffer, format="PNG")
                st.session_state.signature_bytes = buffer.getvalue()
                st.success("Paraf dari kanvas disimpan!"); st.rerun()

with tab2:
    if uploaded_sig := st.file_uploader("Pilih file gambar...", type=["png", "jpg"]):
        if st.button("Gunakan & Hapus Background"):
            with st.spinner("Lagi ngilangin background..."):
                st.session_state.signature_bytes = remove(uploaded_sig.getvalue())
                st.success("Background dihapus!"); st.rerun()

st.markdown("---")
if st.session_state.get('signature_bytes'):
    st.subheader("Langkah 3: Atur Posisi & Ukuran Paraf")
    st.image(st.session_state.signature_bytes, width=150)
    previews = extract_pdf_previews(pdf_bytes)
    if not previews: st.stop()

    page_label = st.selectbox("Pilih halaman:", [f"Halaman {i+1}" for i in range(len(previews))])
    page_idx = int(page_label.split(" ")[-1]) - 1
    
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc: pdf_width, pdf_height = doc[page_idx].rect.width, doc[page_idx].rect.height
    preview_img = Image.open(io.BytesIO(previews[page_idx])); preview_width, preview_height = preview_img.size
    
    size_percent = st.slider("Ukuran Paraf (% lebar):", 1, 100, 20)
    opacity = st.slider("Transparansi:", 0.0, 1.0, 1.0, 0.05)
    x_pos = st.slider("Posisi Horizontal (X):", 0, preview_width - 10, int(preview_width*0.75))
    y_pos = st.slider("Posisi Vertikal (Y):", 0, preview_height - 10, int(preview_height*0.75))

    st.subheader("Preview Real-time")
    signature_img = Image.open(io.BytesIO(st.session_state.signature_bytes))
    sig_w = int(preview_width * (size_percent / 100)); sig_h = int(signature_img.height * (sig_w / signature_img.width)) if sig_w > 0 else 0
    if sig_w > 0 and sig_h > 0:
        resized_signature = signature_img.resize((sig_w, sig_h), Image.Resampling.LANCZOS)
        preview_copy = preview_img.copy().convert("RGBA")
        if opacity < 1.0:
            alpha = resized_signature.split()[-1]; alpha = alpha.point(lambda p: p * opacity); resized_signature.putalpha(alpha)
        preview_copy.paste(resized_signature, (x_pos, y_pos), resized_signature)
        st.image(preview_copy, caption="Beginilah hasilnya nanti.", use_container_width=True)
    
    if st.button("Terapkan Paraf & Download", type="primary", use_container_width=True):
        scale_x, scale_y = pdf_width / preview_width, pdf_height / preview_height
        rect_coords = (x_pos * scale_x, y_pos * scale_y, (x_pos + sig_w) * scale_x, (y_pos + sig_h) * scale_y)
        with st.spinner("Lagi nempelin paraf... ⏳"):
            final_pdf_bytes = add_signature_to_pdf(pdf_bytes, page_idx, st.session_state.signature_bytes, rect_coords)
            if final_pdf_bytes:
                st.session_state.dl_sign = {"file_name": f"{os.path.splitext(uploaded_pdf.name)[0]}_diparaf.pdf", "data": final_pdf_bytes}
                st.success("Berhasil!"); st.rerun()

if 'dl_sign' in st.session_state:
    st.download_button("✅ Sikat PDF Finalnya!", **st.session_state.dl_sign, use_container_width=True)