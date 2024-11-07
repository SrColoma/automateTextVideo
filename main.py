import json
from audio_generator import generate_audio
from video_creator import create_video_with_captions
from moviepy.config import change_settings

def main():
    # Cargar la configuración desde config.json
    with open("config.json", "r") as f:
        config = json.load(f)

    # Configuración de la ruta de ImageMagick
    change_settings({"IMAGEMAGICK_BINARY": config["imagemagick_path"]})

    # Generar el audio usando F5-TTS
    audio_file = generate_audio(config["ref_audio_path"], config["ref_text"], config["gen_text"])
    print(f"Audio generado: {audio_file}")

    # Crear el video con el audio y los subtítulos sincronizados
    create_video_with_captions(
        audio_file,
        config["output_video_path"],
        fontsize=config["fontsize"],
        color=config["font_color"],
        bg_color=config["bg_color"],
        resolution=config["resolution"],
        background_path=config["background_path"]
    )

if __name__ == "__main__":
    main()