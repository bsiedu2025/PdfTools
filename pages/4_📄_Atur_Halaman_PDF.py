import streamlit as st
import os
from streamlit_sortables import sort_items
from utils import extract_pdf_previews, create_new_pdf, clear_all_states

st.set_page_config(page_title="Atur Halaman PDF", layout="wide")
st.title("📄 Atur Halaman PDF")
st.markdown("Upload satu file PDF buat hapus atau ubah urutan halamannya.")

uploaded_file = st.file_uploader("Pilih satu PDF...", type="pdf", key="manage_uploader", on_change=clear_all_states)
if uploaded_file:
    pdf_bytes = uploaded_file.getvalue()
    previews = extract_pdf_previews(pdf_bytes)
    if not previews: st.stop()
    
    st.subheader("Pilih & Atur Urutan Halaman")
    selected_indices = []
    cols = st.columns(5)
    for i, prev in enumerate(previews):
        with cols[i % 5]:
            st.image(prev, use_container_width=True)
            if st.checkbox(f"Halaman {i+1}", key=f"page_select_{i}", value=True):
                selected_indices.append(i)
    
    if selected_indices:
        sorted_labels = sort_items([f"Halaman {i+1}" for i in selected_indices])
        if st.button("🚀 Proses PDF!", type="primary", use_container_width=True):
            final_indices = [int(label.split(" ")[-1]) - 1 for label in sorted_labels]
            new_pdf_bytes = create_new_pdf(pdf_bytes, final_indices)
            st.session_state.dl_manage = {"file_name": f"{os.path.splitext(uploaded_file.name)[0]}_diatur.pdf", "data": new_pdf_bytes}
            st.success("Beres diatur ulang!"); st.rerun()

if 'dl_manage' in st.session_state:
    st.download_button("✅ Sikat PDF Barunya!", **st.session_state.dl_manage, use_container_width=True)