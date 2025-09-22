import streamlit as st
import os
import tempfile
from streamlit_sortables import sort_items
from utils import merge_files_to_pdf, clear_all_states

st.set_page_config(page_title="Gabungin File", layout="wide")
st.title("➕ Gabungin File Jadi Satu PDF")
st.markdown("Upload dua atau lebih file PDF, JPG, atau PNG.")

uploaded_files = st.file_uploader("Pilih file...", type=["pdf", "png", "jpg"], accept_multiple_files=True, key="merge_uploader", on_change=clear_all_states)

if uploaded_files and len(uploaded_files) >= 2:
    st.subheader("Atur Urutan File")
    sorted_filenames = sort_items([f.name for f in uploaded_files])
    file_map = {f.name: f for f in uploaded_files}
    reordered_files = [file_map[name] for name in sorted_filenames]
    
    if st.button(f"🚀 Gabungin {len(reordered_files)} File!", type="primary", use_container_width=True):
        with st.spinner("Lagi nyatuin file-file... ⏳"):
            output_path=None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_out:
                    output_path = tmp_out.name
                success, msg, _ = merge_files_to_pdf(reordered_files, output_path)
                if success:
                    with open(output_path, "rb") as f:
                        st.session_state.dl_merge = {"file_name": "hasil_gabungan.pdf", "data": f.read()}
                    st.success("Berhasil!"); st.rerun()
                else:
                    st.error(f"Gagal, Bro: {msg}")
            finally:
                if output_path: os.remove(output_path)

if 'dl_merge' in st.session_state:
    st.download_button("✅ Download Hasil Gabungan", **st.session_state.dl_merge, use_container_width=True)