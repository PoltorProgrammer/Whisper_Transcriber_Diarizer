from pydantic import BaseModel, Field
from typing import Optional


class TranscriptionRequest(BaseModel):
    language: Optional[str] = Field("English", description="Language of the audio")
    model: Optional[str] = Field("base", description="Whisper model size to use")


class TranscriptionResponse(BaseModel):
    transcript: str = Field(..., description="Transcribed text")
    file_name: str = Field(..., description="Original filename")
