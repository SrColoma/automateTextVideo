from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip, VideoFileClip, ImageClip
import whisper_timestamped as whisper

def get_transcribed_text(audio_file):
    # Transcribe el audio usando Whisper para obtener palabras con timestamps
    audio = whisper.load_audio(audio_file)
    model = whisper.load_model("small", device="cpu")
    results = whisper.transcribe(model, audio, language="en")
    return results["segments"]

def create_video_with_captions(audio_file, output_path="output_video.mp4", fontsize=50, resolution="1920x1080", background_path="./fondos/cuarto.mp4"):
    # Separar la resolución en ancho y alto
    width, height = map(int, resolution.split('x'))
    size = (width, height)

    # Cargar el video de fondo y redimensionarlo al tamaño deseado, quitando su audio
    background_clip = VideoFileClip(background_path).resize(size).without_audio()

    # Cargar y configurar la imagen del título
    try:
        title_image = ImageClip("title_screenshot.png")
        # Redimensionar la imagen manteniendo la proporción si es necesario
        if title_image.size[0] > width * 0.8:  # Si la imagen es más ancha que el 80% del video
            title_image = title_image.resize(width=int(width * 0.8))  # Redimensionar al 80% del ancho
        # Centrar la imagen
        title_pos = ('center', 'center')
        title_image = title_image.set_position(title_pos).set_duration(1)  # Duración de 1 segundo
    except Exception as e:
        print(f"Error al cargar la imagen del título: {e}")
        title_image = None

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
                                color="white", 
                                method='caption',
                                stroke_width=1, 
                                stroke_color="black", 
                                font="Arial-Bold",)
                        .set_start(word["start"])
                        .set_end(word["end"])
                        .set_position("center"))
            text_clips.append(text_clip)

    # Crear la lista de clips para el video compuesto
    video_clips = [background_clip]
    if title_image is not None:
        video_clips.append(title_image)
    video_clips.extend(text_clips)

    # Crear el clip de video compuesto
    video = CompositeVideoClip(video_clips, size=size).set_audio(audio_clip).set_duration(audio_clip.duration)

    # Exportar el video a un archivo
    video.write_videofile(output_path, fps=24)
    print(f"Video guardado en {output_path}")