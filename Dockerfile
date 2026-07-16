FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Tesseract is only required for image-based resumes.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-chi-sim \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install -r requirements.txt

RUN groupadd --system cvopenmic \
    && useradd --system --gid cvopenmic --create-home cvopenmic

# Copy runtime Python modules explicitly by type so local secrets such as .env
# cannot enter the image while newly added application modules remain available.
COPY --chown=cvopenmic:cvopenmic *.py ./
COPY --chown=cvopenmic:cvopenmic .streamlit ./.streamlit

USER cvopenmic

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)"]

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
