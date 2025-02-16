import deepspeech
import numpy as np
import wave
import os

# Cargar el modelo de DeepSpeech
model_path = "deepspeech-0.9.3-models.pbmm"
scorer_path = "deepspeech-0.9.3-models.scorer"
model = deepspeech.Model(model_path)
model.enableExternalScorer(scorer_path)

def transcribir_audio(audio_file):
    with wave.open(audio_file, "rb") as w:
        frames = np.frombuffer(w.readframes(w.getnframes()), np.int16)
        return model.stt(frames)

video_folder = "/opt/jellyfin/media/"

for file in os.listdir(video_folder):
    if file.endswith(".wav"):
        text = transcribir_audio(os.path.join(video_folder, file))
        text_path = os.path.join(video_folder, file.replace(".wav", ".txt"))
        
        with open(text_path, "w") as f:
            f.write(text)
        
        print(f"✅ Transcripción guardada: {text_path}")
