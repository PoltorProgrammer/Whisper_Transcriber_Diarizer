# -*- coding: utf-8 -*-
"""
# Whisper Diarizer
"""

# @title Download dependences

import importlib.util
import subprocess

def install_if_missing(package, install_name=None):
    """
    Checks if a package is installed, and installs it if missing.

    Parameters:
    - package: The module name used in Python (e.g., "torch")
    - install_name: The name used for installation (e.g., "torch" or "git+https://github.com/openai/whisper.git")
    """
    if importlib.util.find_spec(package) is None:
        install_name = install_name or package
        print(f"Installing {install_name}...")
        subprocess.call(["pip", "install", install_name])
    else:
        print(f"{package} is already installed.")

# Check and install packages
install_if_missing("whisper", "git+https://github.com/openai/whisper.git")
install_if_missing("speechbrain")
install_if_missing("torch")
install_if_missing("torchvision")
install_if_missing("torchaudio")
install_if_missing("numpy")
install_if_missing("ffmpeg")
install_if_missing("pyannote", "git+https://github.com/pyannote/pyannote-audio")  # Changed from "pyannote.audio" to "pyannote"

# @title Main Code

import os
import subprocess
import datetime
import torch
import numpy as np
import whisper
import wave
import contextlib
from pyannote.audio import Audio
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pyannote.core import Segment
from sklearn.cluster import AgglomerativeClustering

# Upload the file
from google.colab import files
uploaded = files.upload()
path = next(iter(uploaded))

print(f"Uploaded file: {path}")

# Check if the file is actually a WAV file
def is_wav_file(filepath):
    try:
        with wave.open(filepath, 'r') as f:
            print(f"✅ {filepath} is a valid WAV file.")
            return True
    except wave.Error as e:
        print(f"❌ {filepath} is NOT a valid WAV file: {e}")
        return False

# Convert non-WAV files to WAV
converted_path = "converted_audio.wav"
if not is_wav_file(path):
    print("🔄 Converting file to WAV format...")
    subprocess.call(['ffmpeg', '-i', path, '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', converted_path, '-y'])
    path = converted_path

# Verify conversion
if not is_wav_file(path):
    raise ValueError("🚨 Conversion failed! The file is not a valid WAV format.")

print(f"✅ Using file: {path}")

# User-configurable parameters
num_speakers = 3  # Change to None for automatic estimation
language = 'any'  # Can be 'any' or 'English'
model_size = 'large-v2'  # ['tiny', 'base', 'small', 'medium', 'large']

# Load Whisper model
print("⏳ Loading Whisper model...")
model = whisper.load_model(model_size)
print("✅ Whisper model loaded.")

# Transcribe with automatic language detection if 'any' is selected
print("⏳ Transcribing audio...")
result = model.transcribe(path, language=None if language == "any" else "en")
segments = result.get("segments", [])

if not segments:
    raise ValueError("🚨 No speech detected in the audio file!")

print(f"✅ Transcription complete. Detected {len(segments)} segments.")

# Determine audio duration
with contextlib.closing(wave.open(path, 'r')) as f:
    frames = f.getnframes()
    rate = f.getframerate()
    duration = frames / float(rate)

print(f"📏 Audio duration: {duration:.2f} seconds")

# Load speaker embedding model
print("⏳ Loading speaker embedding model...")
embedding_model = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=torch.device("cuda"))
audio = Audio()
print("✅ Speaker embedding model loaded.")

# Function to extract speaker embeddings
def segment_embedding(segment):
    try:
        start, end = segment["start"], min(duration, segment["end"])
        clip = Segment(start, end)
        waveform, sample_rate = audio.crop(path, clip)

        if not isinstance(waveform, torch.Tensor):
            waveform = torch.tensor(waveform)

        if waveform.ndim == 1:  # Convert 1D tensor to 3D
            waveform = waveform.unsqueeze(0).unsqueeze(0)
        elif waveform.ndim == 2:  # Convert [channels, samples] to [1, channels, samples]
            waveform = waveform.unsqueeze(0)

        if waveform.shape[1] > 1:
            waveform = waveform.mean(dim=1, keepdim=True)

        waveform = waveform.to(torch.float32)

        assert waveform.shape[1] == 1, "🚨 Waveform must be mono (1 channel)"

        return embedding_model(waveform)
    except Exception as e:
        print(f"🚨 Error processing segment {segment['start']} - {segment['end']}: {e}")
        return np.zeros(192)  # Return a dummy embedding

# Compute embeddings
embeddings = np.zeros((len(segments), 192))
for i, segment in enumerate(segments):
    print(f"🎤 Processing segment {i+1}/{len(segments)}: {segment['start']} - {segment['end']}")
    embeddings[i] = segment_embedding(segment)

# Handle NaN values
embeddings = np.nan_to_num(embeddings)

# Perform speaker clustering
print("⏳ Performing speaker clustering...")
clustering = AgglomerativeClustering(n_clusters=num_speakers).fit(embeddings)
labels = clustering.labels_
print("✅ Speaker clustering complete.")

# Assign speaker labels
for i in range(len(segments)):
    segments[i]["speaker"] = f"SPEAKER {labels[i] + 1}"

# Format timestamps
def format_time(seconds):
    return str(datetime.timedelta(seconds=round(seconds)))

# Save transcript
print("💾 Saving transcript...")
with open("transcript.txt", "w") as f:
    for i, segment in enumerate(segments):
        if i == 0 or segments[i - 1]["speaker"] != segment["speaker"]:
            f.write(f"\n{segment['speaker']} [{format_time(segment['start'])}]\n")
        f.write(segment["text"].strip() + " ")

print("✅ Transcription completed! Saved as transcript.txt.")
