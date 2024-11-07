# video_creator.py
from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip
import whisper_timestamped as whisper

def get_transcribed_text(audio_file):
    # Transcribe el audio usando Whisper para obtener palabras con timestamps
    audio = whisper.load_audio(audio_file)
    model = whisper.load_model("small", device="cpu")
    results = whisper.transcribe(model, audio, language="en")
    return results["segments"]

def create_video_with_captions(audio_file, output_path="output_video.mp4", fontsize=24, color="white", bg_color="black", resolution="horizontal"):
    # Configuración de tamaño del video
    if resolution == "horizontal":
        size = (1280, 720)
    elif resolution == "vertical":
        size = (720, 1280)

    # Obtener los segmentos de texto transcritos
    segments = get_transcribed_text(audio_file)
    
    # Crear clips de texto con timestamps usando los segmentos obtenidos
    text_clips = []
    for segment in segments:
        for word in segment["words"]:
            text_clip = (TextClip(word["text"], fontsize=fontsize, color=color, bg_color=bg_color, size=size)
                         .set_start(word["start"])
                         .set_end(word["end"])
                         .set_position("center"))
            text_clips.append(text_clip)

    # Cargar el audio y crear el clip de video compuesto
    audio_clip = AudioFileClip(audio_file)
    video = CompositeVideoClip(text_clips, size=size).set_audio(audio_clip).set_duration(audio_clip.duration)

    # Exportar el video a un archivo
    video.write_videofile(output_path, fps=24)
    print(f"Video guardado en {output_path}")
