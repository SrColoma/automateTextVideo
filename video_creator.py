from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip, VideoFileClip
import whisper_timestamped as whisper

def get_transcribed_text(audio_file):
    # Transcribe el audio usando Whisper para obtener palabras con timestamps
    audio = whisper.load_audio(audio_file)
    model = whisper.load_model("small", device="cpu")
    results = whisper.transcribe(model, audio, language="en")
    return results["segments"]

def create_video_with_captions(audio_file, output_path="output_video.mp4", fontsize=50, color="white", bg_color="black", resolution="horizontal", background_path="./fondos/cuarto.mp4"):
    # Configuración de tamaño del video
    if resolution == "horizontal":
        size = (1280, 720)
    elif resolution == "vertical":
        size = (720, 1280)

    # Cargar el video de fondo y redimensionarlo al tamaño deseado, quitando su audio
    background_clip = VideoFileClip(background_path).resize(size).without_audio()

    # Obtener la duración del audio
    audio_clip = AudioFileClip(audio_file)
    audio_duration = audio_clip.duration

    # Repetir el video de fondo hasta que termine el audio
    background_clip = background_clip.set_duration(audio_duration).loop()

    # Obtener los segmentos de texto transcritos
    segments = get_transcribed_text(audio_file)
    
    # Crear clips de texto con timestamps usando los segmentos obtenidos
    text_clips = []
    for segment in segments:
        for word in segment["words"]:
            text_clip = (TextClip(word["text"], 
                                  fontsize=fontsize, 
                                  color=color, 
                                  method='caption',
                                  stroke_width=1, 
                                  stroke_color=bg_color, 
                                  font="Arial-Bold",)
                         .set_start(word["start"])
                         .set_end(word["end"])
                         .set_position("center"))
            text_clips.append(text_clip)

    # Crear el clip de video compuesto
    video = CompositeVideoClip([background_clip] + text_clips, size=size).set_audio(audio_clip).set_duration(audio_clip.duration)

    # Exportar el video a un archivo
    video.write_videofile(output_path, fps=24)
    print(f"Video guardado en {output_path}")