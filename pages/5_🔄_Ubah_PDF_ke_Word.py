# pages/5_🔄_Ubah_PDF_ke_Word.py

import streamlit as st
import os
import tempfile
from utils import convert_pdf_to_docx, clear_all_states

st.set_page_config(page_title="Ubah PDF ke Word", layout="wide")
# PERBAIKAN: Menghapus spasi di awal judul
st.title("🔄 Ubah PDF ke Dokumen Word (.docx)")
st.markdown("Upload file PDF-mu buat diubah jadi format DOCX.")
st.warning("ℹ️ **Info Penting:** Hasil terbaik biasanya buat PDF yang isinya teks dominan dan layoutnya simpel.")

uploaded_file = st.file_uploader(
    "Pilih PDF...",
    type="pdf",
    key="word_uploader",
    on_change=clear_all_states
)

if uploaded_file:
    st.info(f"File: **{uploaded_file.name}**")
    # PERBAIKAN: Menghapus / dan spasi ekstra di tombol
    if st.button("🪄 Ubah ke Word!", type="primary", use_container_width=True):
        with st.spinner("Lagi ngubah...⏳"):
            input_path, output_path = None, None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
                    tmp_in.write(uploaded_file.getvalue())
                    input_path = tmp_in.name
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_out:
                    output_path = tmp_out.name
                
                success, msg, _ = convert_pdf_to_docx(input_path, output_path)
                
                if success:
                    with open(output_path, "rb") as f:
                        st.session_state.dl_word = {
                            "file_name": f"word_{os.path.splitext(uploaded_file.name)[0]}.docx",
                            "data": f.read()
                        }
                    st.success("Berhasil diubah!")
                    st.rerun()
                else:
                    st.error(f"Gagal, Bro: {msg}")
            finally:
                if input_path and os.path.exists(input_path):
                    os.remove(input_path)
                if output_path and os.path.exists(output_path):
                    os.remove(output_path)

if 'dl_word' in st.session_state:
    st.download_button(
        "✅ Download File Word",
        **st.session_state.dl_word,
        use_container_width=True,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )