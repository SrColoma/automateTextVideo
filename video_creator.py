from moviepy.editor import TextClip, CompositeVideoClip, CompositeAudioClip, AudioFileClip, VideoFileClip, ImageClip, ColorClip
import whisper_timestamped as whisper

def get_transcribed_text(audio_file):
    # Transcribe el audio usando Whisper para obtener palabras con timestamps
    audio = whisper.load_audio(audio_file)
    model = whisper.load_model("small", device="cpu")
    results = whisper.transcribe(model, audio, language="en")
    return results["segments"]

def create_video_with_captions(
    audio_file,
    output_path="output_video.mp4",
    fontsize=50,
    resolution="1920x1080",
    background_path="./fondos/cuarto.mp4",
    background_audio_path=None,
    background_audio_volume=0.02
):
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
        title_image = title_image.set_position(title_pos).set_duration(5)  # Duración de 5 segundos
    except Exception as e:
        print(f"Error al cargar la imagen del título: {e}")
        title_image = None

    # Obtener la duración del audio principal
    audio_clip = AudioFileClip(audio_file)
    audio_duration = audio_clip.duration

    # Ajustar la duración del video de fondo para que coincida con el audio principal
    background_clip = background_clip.set_duration(audio_duration)

    # Cargar el audio de fondo si se proporciona y ajustar su volumen
    if background_audio_path:
        background_audio_clip = AudioFileClip(background_audio_path).volumex(background_audio_volume)
        # Recortar el audio de fondo para que coincida físicamente con la duración del audio principal
        background_audio_clip = background_audio_clip.subclip(0, min(audio_duration, background_audio_clip.duration))
        # Agregar un desvanecimiento al final del audio de fondo
        background_audio_clip = background_audio_clip.audio_fadeout(1.5)
        # Combinar el audio principal y el audio de fondo
        final_audio = CompositeAudioClip([background_audio_clip, audio_clip])
    else:
        final_audio = audio_clip

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

    # Crear un clip de fondo negro para el desvanecimiento final
    fade_out_clip = ColorClip(size=size, color=(0, 0, 0)).set_duration(1.5)

    # Combinar todos los clips de video
    video = CompositeVideoClip(video_clips, size=size).set_audio(final_audio)
    video_with_fadeout = CompositeVideoClip([video, fade_out_clip.set_start(audio_duration)])

    # Exportar el video a un archivo
    video_with_fadeout.write_videofile(output_path, fps=24)
    print(f"Video guardado en {output_path}")
