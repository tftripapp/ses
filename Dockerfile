# Railway için tek servis Dockerfile
FROM python:3.10-slim

# Node.js kurulumu
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Backend bağımlılıkları
COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Frontend bağımlılıkları ve build
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm install
COPY frontend/ .
RUN npm run build

# Ana dizine geri dön
WORKDIR /app

# Backend dosyalarını kopyala
COPY backend/ .

# Port ayarları
EXPOSE 8000

# Başlatma komutu
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
