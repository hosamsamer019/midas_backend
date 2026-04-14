# ── Stage 1: dependency installation ─────────────────────────────────────────
FROM python:3.11-slim AS deps

# System packages required to build/run Python dependencies:
#   build-essential / gcc  → compile C extensions (psycopg2, cryptography, etc.)
#   libpq-dev              → psycopg2-binary headers
#   libgl1 / libglib2.0-0  → opencv-python-headless runtime
#   tesseract-ocr          → pytesseract OCR engine
#   libgdal-dev / gdal-bin → geopandas / GDAL bindings
#   libproj-dev            → pyproj (geopandas dependency)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-ara \
    libgdal-dev \
    gdal-bin \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only the requirements file first so Docker can cache this layer.
# The pip install layer is only invalidated when requirements.txt changes.
COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt


# ── Stage 2: production image ─────────────────────────────────────────────────
FROM python:3.11-slim AS production

# Runtime-only system libraries (no build tools needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-ara \
    libgdal32 \
    libproj25 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from the deps stage
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

WORKDIR /app

# Copy application source code
COPY . .

# Collect static files at build time so the image is self-contained
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Run migrations then start gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn antibiogram.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120"]
