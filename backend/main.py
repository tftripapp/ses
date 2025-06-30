from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import whisper
import yt_dlp
import os
import uuid
import asyncio
from datetime import datetime
import aiofiles
from typing import Optional, List
import json

app = FastAPI(title="Modern Transcription API", version="1.0.0")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domain'ler belirtin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Whisper modelini yükle
model = whisper.load_model("base")

# Transkript verilerini saklamak için basit dict (production'da database kullanın)
transcriptions = {}

class TranscriptionRequest(BaseModel):
    url: Optional[str] = None
    language: Optional[str] = None

class TranscriptionResponse(BaseModel):
    id: str
    status: str
    text: Optional[str] = None
    segments: Optional[List] = None
    language: Optional[str] = None
    created_at: str
    duration: Optional[float] = None

@app.get("/api")
async def api_root():
    return {"message": "Modern Transcription API", "version": "1.0.0"}

@app.post("/api/transcribe", response_model=TranscriptionResponse)
async def transcribe_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: Optional[str] = None
):
    """Dosya yükleme ve transkript işlemi"""
    
    # Dosya türü kontrolü
    allowed_types = [
        "audio/mpeg", "audio/wav", "audio/m4a", "audio/flac",
        "video/mp4", "video/avi", "video/mov", "video/mkv"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Desteklenmeyen dosya türü")
    
    # Benzersiz ID oluştur
    transcription_id = str(uuid.uuid4())
    
    # Geçici dosya yolu
    temp_file_path = f"temp_{transcription_id}_{file.filename}"
    
    try:
        # Dosyayı kaydet
        async with aiofiles.open(temp_file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Transkript işlemini başlat
        transcriptions[transcription_id] = {
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "filename": file.filename
        }
        
        # Background task olarak transkript işlemini çalıştır
        background_tasks.add_task(
            process_transcription,
            transcription_id,
            temp_file_path,
            language
        )
        
        return TranscriptionResponse(
            id=transcription_id,
            status="processing",
            created_at=transcriptions[transcription_id]["created_at"]
        )
        
    except Exception as e:
        # Hata durumunda geçici dosyayı temizle
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transcribe-url", response_model=TranscriptionResponse)
async def transcribe_url(
    background_tasks: BackgroundTasks,
    request: TranscriptionRequest
):
    """URL'den video/audio indirme ve transkript işlemi"""
    
    if not request.url:
        raise HTTPException(status_code=400, detail="URL gerekli")
    
    transcription_id = str(uuid.uuid4())
    
    transcriptions[transcription_id] = {
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "url": request.url
    }
    
    # Background task olarak URL'den indirme ve transkript işlemini çalıştır
    background_tasks.add_task(
        process_url_transcription,
        transcription_id,
        request.url,
        request.language
    )
    
    return TranscriptionResponse(
        id=transcription_id,
        status="processing",
        created_at=transcriptions[transcription_id]["created_at"]
    )

@app.get("/api/transcriptions/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription(transcription_id: str):
    """Transkript durumunu ve sonucunu getir"""
    
    if transcription_id not in transcriptions:
        raise HTTPException(status_code=404, detail="Transkript bulunamadı")
    
    transcription = transcriptions[transcription_id]
    
    return TranscriptionResponse(
        id=transcription_id,
        status=transcription["status"],
        text=transcription.get("text"),
        segments=transcription.get("segments"),
        language=transcription.get("language"),
        created_at=transcription["created_at"],
        duration=transcription.get("duration")
    )

@app.get("/api/transcriptions")
async def list_transcriptions():
    """Tüm transkriptleri listele"""
    return list(transcriptions.values())

@app.delete("/api/transcriptions/{transcription_id}")
async def delete_transcription(transcription_id: str):
    """Transkript sil"""
    
    if transcription_id not in transcriptions:
        raise HTTPException(status_code=404, detail="Transkript bulunamadı")
    
    del transcriptions[transcription_id]
    return {"message": "Transkript silindi"}

async def process_transcription(transcription_id: str, file_path: str, language: Optional[str] = None):
    """Dosya transkript işlemi"""
    try:
        # Whisper ile transkript
        result = model.transcribe(
            file_path,
            language=language,
            verbose=True
        )
        
        # Sonuçları kaydet
        transcriptions[transcription_id].update({
            "status": "completed",
            "text": result["text"],
            "segments": result["segments"],
            "language": result["language"],
            "duration": result.get("duration")
        })
        
    except Exception as e:
        transcriptions[transcription_id].update({
            "status": "error",
            "error": str(e)
        })
    finally:
        # Geçici dosyayı temizle
        if os.path.exists(file_path):
            os.remove(file_path)

async def process_url_transcription(transcription_id: str, url: str, language: Optional[str] = None):
    """URL'den indirme ve transkript işlemi"""
    temp_file_path = f"temp_{transcription_id}_download"
    
    try:
        # yt-dlp ile video/audio indir
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': temp_file_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # İndirilen dosya yolunu bul
        downloaded_file = f"{temp_file_path}.mp3"
        
        if not os.path.exists(downloaded_file):
            raise Exception("Dosya indirilemedi")
        
        # Transkript işlemini çalıştır
        await process_transcription(transcription_id, downloaded_file, language)
        
    except Exception as e:
        transcriptions[transcription_id].update({
            "status": "error",
            "error": str(e)
        })
    finally:
        # Geçici dosyaları temizle
        for file_path in [temp_file_path, f"{temp_file_path}.mp3"]:
            if os.path.exists(file_path):
                os.remove(file_path)

# EN SONDA: Frontend static dosyalarını serve et (API route'larından sonra!)
try:
    app.mount("/", StaticFiles(directory="frontend/out", html=True), name="static")
except Exception as e:
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
