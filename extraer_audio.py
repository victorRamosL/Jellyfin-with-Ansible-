import os

video_folder = "/opt/jellyfin/media/"

for file in os.listdir(video_folder):
    if file.endswith(".mp4") or file.endswith(".mkv"):
        video_path = os.path.join(video_folder, file)
        audio_path = video_path.rsplit(".", 1)[0] + ".wav"
        
        if not os.path.exists(audio_path):  # No convertir si ya existe
            os.system(f"ffmpeg -i '{video_path}' -ac 1 -ar 16000 -f wav '{audio_path}'")
            print(f"✅ Audio extraído: {audio_path}")
