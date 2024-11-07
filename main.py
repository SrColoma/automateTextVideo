# main.py
from audio_generator import generate_audio
from video_creator import create_video_with_captions
from moviepy.config import change_settings

def main():
    # Configuración de la ruta de ImageMagick
    imagemagick_path = "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"
    change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})
    
    # Parámetros de configuración
    ref_audio_path = "./audiocharacters/alfredaudio.opus"
    ref_text = ""
    gen_text = "Independent game development has transformed from a niche hobby into a thriving industry. Small teams and solo developers now create innovative titles that rival major studios, thanks to accessible development tools and digital distribution platforms. This has led to unique gaming experiences that push creative boundaries while operating on smaller budgets."
    output_video_path = "./salidas/output_video.mp4"
    
    # Elegir el formato del video
    print("Selecciona el formato del video:")
    print("1: Horizontal (YouTube)")
    print("2: Vertical (Shorts)")
    choice = input("Elige una opción (1 o 2): ")
    
    if choice == "1":
        resolution = "horizontal"
    elif choice == "2":
        resolution = "vertical"
    else:
        print("Opción no válida, se usará el formato horizontal por defecto.")
        resolution = "horizontal"
    
    # Generar el audio usando F5-TTS
    audio_file = generate_audio(ref_audio_path, ref_text, gen_text)
    print(f"Audio generado: {audio_file}")
    
    # Crear el video con el audio y los subtítulos sincronizados
    create_video_with_captions(audio_file, output_video_path, resolution=resolution)

if __name__ == "__main__":
    main()
