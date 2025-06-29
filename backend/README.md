# Backend

Bu klasör, FastAPI + Whisper tabanlı transkript API'sini içerir.

## Railway Deploy

- Railway'de bu klasörü ayrı bir servis olarak deploy edin.
- Gerekli ortam değişkenlerini Railway panelinden ekleyin.
- Dockerfile ve requirements.txt hazırdır.

## Başlatma

```
# Lokal geliştirme
pip install -r requirements.txt
uvicorn main:app --reload
``` 