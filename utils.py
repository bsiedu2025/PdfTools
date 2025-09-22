# utils.py

import streamlit as st
import subprocess
import os
import tempfile
import io
import numpy as np
import aspose.words as aw
from pypdf import PdfWriter, PdfReader
from PIL import Image, ExifTags
import fitz  # PyMuPDF
from rembg import remove

# --- FUNGSI BARU UNTUK MEMBERSIHKAN WARNA ---
def sanitize_color(color):
    """Menerjemahkan berbagai format warna ke tuple RGB (0-1) yang aman untuk PyMuPDF."""
    if color is None:
        return None
    if isinstance(color, (tuple, list)) and len(color) == 3:
        return tuple(c for c in color)
    if isinstance(color, int):
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        return (r / 255.0, g / 255.0, b / 255.0)
    if isinstance(color, str):
        try:
            return fitz.utils.hex_to_rgb(color)
        except:
            return (0, 0, 0) # Fallback ke hitam jika hex tidak valid
    return (0, 0, 0)

# --- Fungsi Bantuan untuk Membersihkan State ---
def clear_all_states():
    """Membersihkan semua state download dan widget agar tidak tumpang tindih."""
    keys_to_delete = []
    for key in st.session_state.keys():
        if key.startswith("dl_") or key.startswith("page_select_") or key.startswith("sorted_list_"):
            keys_to_delete.append(key)
    for key in keys_to_delete:
        del st.session_state[key]
    if 'signature_bytes' in st.session_state:
        st.session_state.signature_bytes = None


# --- Fungsi-fungsi Inti ---
def compress_pdf_ghostscript(input_path, output_path, pdf_settings_value, extra_params=None):
    try:
        command = ['gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4', f'-dPDFSETTINGS=/{pdf_settings_value}', '-dNOPAUSE', '-dQUIET', '-dBATCH']
        if extra_params: command.extend(extra_params)
        command.extend([f'-sOutputFile={output_path}', input_path])
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=180)
        return True, "Sukses!", None
    except Exception as e: return False, str(e), str(e)

def convert_pdf_to_docx(pdf_path, docx_path):
    """Mengubah file PDF menjadi DOCX menggunakan Aspose.Words."""
    try:
        doc = aw.Document(pdf_path)
        doc.save(docx_path)
        if os.path.exists(docx_path) and os.path.getsize(docx_path) > 0:
            return True, "Sip!", None
        else:
            return False, "Konversi gagal, file output kosong.", "File output tidak terbuat."
    except Exception as e:
        print(f"Aspose conversion error: {e}")
        return False, f"Terjadi error dari library Aspose: {e}", str(e)

def merge_files_to_pdf(files, output_path):
    merger = PdfWriter()
    try:
        for file in files:
            file.seek(0)
            if file.type == "application/pdf":
                reader = PdfReader(file)
                for page in reader.pages: merger.add_page(page)
            elif file.type in ["image/png", "image/jpeg", "image/jpg"]:
                img = Image.open(file).convert("RGB")
                with io.BytesIO() as img_pdf_buffer:
                    img.save(img_pdf_buffer, format='PDF')
                    img_pdf_buffer.seek(0)
                    merger.add_page(PdfReader(img_pdf_buffer).pages[0])
        merger.write(output_path)
        merger.close()
        return True, "Mantap!", None
    except Exception as e:
        merger.close()
        return False, str(e), str(e)

def extract_pdf_previews(_pdf_bytes):
    try:
        with fitz.open(stream=_pdf_bytes, filetype="pdf") as doc:
            return [page.get_pixmap(dpi=96).tobytes("png") for page in doc]
    except Exception as e:
        st.error(f"Gagal bikin preview PDF, Bro. Error: {e}")
        return []

def create_new_pdf(pdf_bytes, page_order_indices):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    total_pages = len(reader.pages)
    for index in page_order_indices:
        if 0 <= index < total_pages:
            writer.add_page(reader.pages[index])
    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    writer.close()
    return output_buffer.getvalue()

def add_signature_to_pdf(pdf_bytes, page_num, signature_bytes, rect_coords):
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            page = doc.load_page(page_num)
            rect = fitz.Rect(rect_coords)
            page.insert_image(rect, stream=signature_bytes)
            return doc.write()
    except Exception as e:
        st.error(f"Gagal nambahin paraf ke PDF: {e}")
        return None
        
def get_exif_data(image: Image.Image):
    """Membaca dan mem-format data EXIF dari sebuah gambar."""
    try:
        exif_data = image.getexif()
        if not exif_data:
            return {"Info": "Tidak ada data EXIF di file ini."}

        decoded_exif = {}
        for tag_id, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            if tag_name in ['Make', 'Model', 'DateTimeOriginal', 'FNumber', 'ExposureTime', 'ISOSpeedRatings']:
                decoded_exif[str(tag_name)] = str(value)
        
        return decoded_exif if decoded_exif else {"Info": "Tidak ada metadata standar yang ditemukan."}
    except Exception:
        return {"Error": "Gagal membaca metadata."}
        
# utils.py

# ... (semua fungsi lain di atasnya biarkan seperti semula) ...

# --- FUNGSI HAPUS WATERMARK (FINAL DENGAN SEMUA FITUR) ---
def remove_watermark_text(pdf_bytes, watermark_texts):
    """
    Membaca semua elemen (teks, gambar, grafik) dan menulisnya kembali,
    menghapus semua teks yang cocok dengan daftar watermark_texts.
    """
    try:
        original_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        new_doc = fitz.open()
        text_found_and_removed = False
        
        # Ubah semua watermark yang dicari ke huruf kecil
        watermark_texts_lower = [text.lower().strip() for text in watermark_texts if text.strip()]

        for page in original_doc:
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            
            # 1. Salin GAMBAR
            for img in page.get_images(full=True):
                xref = img[0]
                if xref == 0: continue
                try:
                    bbox = page.get_image_bbox(img)
                    if bbox:
                        img_bytes_data = original_doc.extract_image(xref)["image"]
                        new_page.insert_image(bbox, stream=img_bytes_data)
                except Exception as e:
                    print(f"Skipping an image due to error: {e}")

            # 2. Salin GRAFIK VEKTOR (termasuk garis tabel)
            for shape in page.get_drawings():
                try:
                    s_color = sanitize_color(shape.get('color'))
                    f_color = sanitize_color(shape.get('fill'))
                    new_page.draw_rect(shape['rect'], color=s_color, fill=f_color, width=shape.get('width', 1))
                except Exception as e:
                    print(f"Skipping a drawing shape due to error: {e}")

            # 3. Salin TEKS (kecuali watermark) dengan metode Shape
            shape = new_page.new_shape()
            text_blocks = page.get_text("dict")["blocks"]
            for block in text_blocks:
                if block['type'] == 0:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            
                            # Cek apakah teks span mengandung SALAH SATU dari watermark
                            is_watermark = False
                            for wt in watermark_texts_lower:
                                if wt in span["text"].lower():
                                    is_watermark = True
                                    break
                            
                            if not is_watermark:
                                text_color = sanitize_color(span["color"])
                                try:
                                    shape.insert_text(
                                        fitz.Point(span['origin']),
                                        span["text"],
                                        fontname=span["font"],
                                        fontsize=span["size"],
                                        color=text_color
                                    )
                                except Exception:
                                    shape.insert_text(
                                        fitz.Point(span['origin']),
                                        span["text"],
                                        fontname="helv",
                                        fontsize=span["size"],
                                        color=text_color
                                    )
                            else:
                                text_found_and_removed = True
            
            shape.commit()
        
        if not text_found_and_removed:
            original_doc.close(); new_doc.close()
            return False, None, "Tidak ada teks watermark yang cocok ditemukan di dalam PDF."

        final_pdf_bytes = new_doc.write()
        original_doc.close(); new_doc.close()
        return True, final_pdf_bytes, "Berhasil menghapus teks watermark yang ditemukan dari PDF."

    except Exception as e:
        return False, None, f"Terjadi error saat memproses: {e}"