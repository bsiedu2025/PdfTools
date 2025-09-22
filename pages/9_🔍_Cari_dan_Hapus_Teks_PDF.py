# pages/9_🔍_Cari_dan_Hapus_Teks_PDF.py

import streamlit as st
import os
from utils import remove_watermark_text, clear_all_states

st.set_page_config(page_title="Cari & Hapus Teks", layout="wide")

st.title("🔍 Penghapus Teks Watermark PDF")
st.markdown("Masukkan satu atau beberapa kata/kalimat yang ingin dihapus dari seluruh halaman PDF.")
st.info("Fitur ini bekerja dengan cara 'menulis ulang' PDF tanpa menyertakan teks watermark.")

uploaded_file = st.file_uploader(
    "Pilih PDF yang mau diedit...",
    type="pdf",
    key="watermark_uploader",
    on_change=clear_all_states
)

if uploaded_file:
    st.info(f"File: **{uploaded_file.name}**")

    # --- PERBAIKAN: Ganti st.text_input menjadi st.text_area ---
    text_to_remove_input = st.text_area(
        "Masukkan teks yang ingin dihapus (satu per baris):",
        height=100,
        placeholder="Contoh:\nHERMAN WAHYUDI\n2179001490\nCONFIDENTIAL"
    )
    
    if st.button("🚀 Hapus Watermark Sekarang!", type="primary", use_container_width=True):
        # Ubah input dari text area menjadi sebuah list, hilangkan baris kosong
        watermark_list = [line.strip() for line in text_to_remove_input.split('\n') if line.strip()]

        if not watermark_list:
            st.warning("Tolong masukkan teks watermark yang mau dihapus dulu, Bro.")
        else:
            with st.spinner("Lagi nyari dan ngehapus semua teks di seluruh dokumen... 🕵️"):
                pdf_bytes = uploaded_file.getvalue()
                
                success, result_bytes, message = remove_watermark_text(pdf_bytes, watermark_list)
                
                if success:
                    st.session_state.dl_watermark_removed = {
                        "file_name": f"no_watermark_{uploaded_file.name}",
                        "data": result_bytes
                    }
                    st.success(message)
                    st.rerun()
                else:
                    st.warning(message)

if 'dl_watermark_removed' in st.session_state:
    info = st.session_state.dl_watermark_removed
    st.download_button(
        "✅ Download PDF Tanpa Watermark",
        **info,
        mime="application/pdf",
        use_container_width=True
    )

st.markdown("---")
st.caption("**Catatan Penting:** Metode 'tulis ulang' ini sangat kuat, tapi hasilnya paling bagus untuk dokumen dengan layout simpel. Kalau PDF-nya super kompleks, ada kemungkinan beberapa formatnya bergeser.")