# Modern Audio/Video Transcription App

Modern tasarımlı, ses ve video dosyalarından transkript oluşturan web uygulaması.

## Özellikler

- 🎵 **Ses Dosyası Desteği**: MP3, WAV, M4A, FLAC
- 🎬 **Video Dosyası Desteği**: MP4, AVI, MOV, MKV
- 🌐 **Web URL Desteği**: YouTube, Vimeo vb. linklerden transkript
- 📝 **Çoklu Format**: TXT, SRT, VTT formatlarında indirme
- 🎨 **Modern UI**: Responsive ve kullanıcı dostu arayüz
- ⚡ **Hızlı İşlem**: Whisper AI ile optimize edilmiş transkript
- 🌍 **Çoklu Dil**: 99+ dil desteği

## Teknolojiler

- **Backend**: Python FastAPI, Whisper AI
- **Frontend**: React, Tailwind CSS
- **Deployment**: Railway
- **Database**: PostgreSQL (Railway)

## Railway Deploy

### Kolay Deploy (Tek Servis)

1. **GitHub'a Yükle**: Bu projeyi GitHub repository'nize yükleyin
2. **Railway'e Bağla**: Railway'de "Deploy from GitHub repo" seçin
3. **Otomatik Deploy**: Railway otomatik olarak Dockerfile'ı algılar ve deploy eder
4. **Domain Al**: Railway size otomatik bir domain verir

### Environment Variables (Opsiyonel)

Railway panelinden şu değişkenleri ekleyebilirsiniz:

```env
NEXT_PUBLIC_API_URL=https://your-app.railway.app
WHISPER_MODEL=base
```

### Deploy Sonrası

- Uygulama otomatik olarak `https://your-app.railway.app` adresinde çalışır
- Frontend ve backend tek serviste çalışır
- API endpoint'leri `/api/` prefix'i ile erişilebilir

## Lokal Geliştirme

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (ayrı terminal)
cd frontend
npm install
npm run dev
```

## API Endpoints

- `POST /api/transcribe` - Dosya yükleme ve transkript
- `POST /api/transcribe-url` - URL'den transkript
- `GET /api/transcriptions` - Transkript listesi
- `GET /api/transcriptions/{id}` - Transkript detayı
- `DELETE /api/transcriptions/{id}` - Transkript silme

## Lisans

MIT License 