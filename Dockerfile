# Pake base image Python yang enteng
FROM python:3.9-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install Ghostscript dan dependensi baru, termasuk ffmpeg
RUN apt-get update && \
    apt-get install -y \
    ghostscript \
    libgdiplus \
    libc6-dev \
    libx11-dev \
    libicu-dev \
    ffmpeg \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install library Python
RUN pip install -r requirements.txt

# Download model default untuk rembg dan whisper
RUN python -c "from rembg import new_session; new_session('u2net')"
RUN python -c "import whisper; whisper.load_model('base')"

COPY . .

EXPOSE 8503

CMD ["streamlit", "run", "app.py", "--server.port=8503", "--server.address=0.0.0.0"]