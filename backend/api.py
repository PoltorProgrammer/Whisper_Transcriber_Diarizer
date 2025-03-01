from fastapi import FastAPI, File, UploadFile
import shutil
import os
from process_audio import transcribe_audio

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"message": "Whisper Diarizer API is running!"}

@app.post("/transcribe/")
async def transcribe_audio_api(file: UploadFile = File(...), language: str = "English", model: str = "base"):
    # Guardar el archivo subido temporalmente
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Llamar a la función de transcripción
    transcript = transcribe_audio(file_path, language, model)

    # Eliminar archivo temporal
    os.remove(file_path)

    return {"transcript": transcript}

