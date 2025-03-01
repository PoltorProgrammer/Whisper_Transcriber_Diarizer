import time

def transcribe_audio(file_path, language="English", model="base"):
    print(f"Simulando transcripción para {file_path} con {model} en {language}...")
    
    # Simulación de procesamiento (en test ligero solo se agrega un delay)
    time.sleep(2)
    
    transcript = f"[Simulación] Transcripción para {file_path}\nIdioma: {language}\nModelo: {model}\n\n[Texto generado...]"
    
    return transcript
