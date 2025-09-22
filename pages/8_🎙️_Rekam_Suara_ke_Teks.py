# pages/8_🎙️_Rekam_Suara_ke_Teks.py

import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import numpy as np
import whisper
import io
import av
import tempfile
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Rekam Suara ke Teks", layout="wide")

# --- Fungsi dan Class Bantuan ---

@st.cache_resource
def load_whisper_model():
    """Memuat model Whisper dengan cache."""
    return whisper.load_model("base")

def transcribe_audio(audio_bytes):
    """Mengubah byte audio menjadi teks menggunakan Whisper."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        model = load_whisper_model()
        result = model.transcribe(tmp_file_path, fp16=False)
        os.remove(tmp_file_path)
        return result.get('text', "Tidak ada teks yang terdeteksi.")
    except Exception as e:
        st.error(f"Waduh, ada error pas transkripsi, Bro: {e}")
        return None

class AudioFrameProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.audio_frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.audio_frames.append(frame)
        return frame

def frames_to_wav(frames) -> bytes:
    """Menggabungkan frame audio dari webrtc menjadi format WAV."""
    if not frames:
        return None

    sound_chunk = np.concatenate([frame.to_ndarray() for frame in frames], axis=1).T
    
    buffer = io.BytesIO()
    with io.BytesIO() as wav_buffer:
        sample_rate = 48000
        bits_per_sample = 16
        num_channels = 1
        num_frames = sound_chunk.shape[0]
        
        wav_header = b'RIFF' + (36 + num_frames * num_channels * bits_per_sample // 8).to_bytes(4, 'little') + b'WAVEfmt ' + (16).to_bytes(4, 'little') + (1).to_bytes(2, 'little') + num_channels.to_bytes(2, 'little') + sample_rate.to_bytes(4, 'little') + (sample_rate * num_channels * bits_per_sample // 8).to_bytes(4, 'little') + (num_channels * bits_per_sample // 8).to_bytes(2, 'little') + bits_per_sample.to_bytes(2, 'little') + b'data' + (num_frames * num_channels * bits_per_sample // 8).to_bytes(4, 'little')

        buffer.write(wav_header)
        buffer.write(sound_chunk.astype(np.int16).tobytes())
        return buffer.getvalue()

# --- Tampilan Halaman Streamlit ---
st.title("🎙️ Rekam Suara ke Teks (dengan Visualisasi)")
st.markdown("Tekan tombol **START** untuk mulai merekam. Selama merekam, status akan menjadi `RUNNING`.")
st.info("Setelah selesai, tekan **STOP**. Grafik gelombang suara akan muncul di bawah.")

# Reset state jika belum ada
if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = None
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = None

webrtc_ctx = webrtc_streamer(
    key="audio-recorder",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioFrameProcessor,
    media_stream_constraints={"video": False, "audio": True},
)

# --- PERBAIKAN: Tambahkan notifikasi jika rekaman kosong ---
if not webrtc_ctx.state.playing and webrtc_ctx.audio_processor:
    if not webrtc_ctx.audio_processor.audio_frames:
        st.session_state.ran_once = True
    
    if 'ran_once' not in st.session_state:
        st.session_state.audio_bytes = frames_to_wav(webrtc_ctx.audio_processor.audio_frames)
        st.session_state.ran_once = True

if 'ran_once' in st.session_state and not st.session_state.audio_bytes and not webrtc_ctx.state.playing:
    st.warning("Rekaman terlalu singkat atau tidak ada suara terdeteksi. Coba rekam lagi ya, Bro.")

if st.session_state.audio_bytes:
    st.subheader("Hasil Rekaman")
    st.audio(st.session_state.audio_bytes, format='audio/wav')

    st.subheader("Grafik Gelombang Suara")
    try:
        wav_file = io.BytesIO(st.session_state.audio_bytes)
        wav_file.seek(44)
        audio_data = np.frombuffer(wav_file.read(), dtype=np.int16)
        
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.plot(audio_data, color='#FF4B4B')
        ax.set_ylabel("Amplitudo")
        ax.set_yticks([]); ax.set_xticks([])
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.spines['left'].set_visible(False)
        st.pyplot(fig)
    except Exception as e:
        st.warning(f"Gagal membuat grafik: {e}")

    if st.button("Ubah ke Teks", type="primary", use_container_width=True):
        with st.spinner("Sabar ya, AI lagi dengerin rekaman lo... 🧠"):
            transcribed_text = transcribe_audio(st.session_state.audio_bytes)
            if transcribed_text is not None:
                st.session_state.transcribed_text = transcribed_text

if st.session_state.transcribed_text:
    st.subheader("Hasil Transkripsi:")
    st.text_area("Teks dari suara lo:", value=st.session_state.transcribed_text, height=200)

if st.button("Reset / Rekam Ulang"):
    st.session_state.pop('audio_bytes', None)
    st.session_state.pop('transcribed_text', None)
    st.session_state.pop('ran_once', None)
    st.rerun()