from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
import shutil
import os
from app.core.config import settings
from app.services.transcription import transcribe_audio
from app.api.models import TranscriptionResponse, TranscriptionRequest
import uuid

router = APIRouter()


@router.get("/")
async def health_check():
    """Endpoint to check if API is running"""
    return {"status": "healthy", "message": "Whisper Diarizer API is running!"}


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: Optional[str] = settings.DEFAULT_LANGUAGE,
    model: Optional[str] = settings.DEFAULT_MODEL,
):
    """
    Transcribe an audio file using Whisper
    """
    # Generate unique filename to avoid collisions
    file_id = str(uuid.uuid4())
    temp_file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    try:
        # Save uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process the audio file
        transcript = transcribe_audio(temp_file_path, language, model)
        
        # Clean up file in background after response is sent
        background_tasks.add_task(os.remove, temp_file_path)
        
        return {"transcript": transcript, "file_name": file.filename}
    
    except Exception as e:
        # Make sure to clean up if there's an error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
