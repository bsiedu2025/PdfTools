# app.py

import streamlit as st

# Konfigurasi halaman utama
st.set_page_config(
    page_title="PDF Tool Gaul - Halaman Utama",
    page_icon="🛠️",
    layout="wide"
)

# Tampilan halaman utama
st.title("🛠️ Selamat Datang di PDF Tool Gaul, Bro!")
st.sidebar.success("Pilih alat yang mau lo pake di atas.")

st.markdown(
    """
    Ini adalah kumpulan alat buat ngurusin file PDF lo sehari-hari.
    Semua fitur ada di sidebar kiri yang udah muncul otomatis, tinggal pilih aja mana yang lo butuhin.

    **Alat yang tersedia:**
    - **Paraf PDF**: Tempel paraf digital ke file PDF lo.
    - **Kecilin PDF**: Kompres ukuran file PDF biar lebih enteng.
    - **Gabungin File**: Satukan beberapa file PDF atau gambar jadi satu PDF.
    - **Atur Halaman PDF**: Hapus atau susun ulang halaman di dalam PDF.
    - **Ubah PDF ke Word**: Konversi file PDF jadi dokumen .docx.

    Semoga ngebantu kerjaan lo ya, Bro!
    """
)