import os
import random
from audio_generator import generate_audio
from video_creator import create_video_with_captions
from moviepy.config import change_settings
from spider import capture_reddit_post
from utils import get_files_from_folder

# Función auxiliar para seleccionar archivo aleatorio
def get_random_file(files_list, folder_path):
    if not files_list:
        return None
    random_file = random.choice(files_list)
    return os.path.join(folder_path, random_file)

def generate_content(url_post, 
                     max_comentarios, 
                     imagemagick_path, 
                     output_path, 
                     personaje, 
                     fondo, 
                     random_personaje, 
                     random_fondo, 
                     tamano_fuente, 
                     resolucion):
    

    # Cargar archivos de las carpetas 'audiocharacters' y 'fondos'
    audio_folder = 'audiocharacters'
    video_folder = 'fondos'

    audio_files = get_files_from_folder(audio_folder, ['.wav', '.mp3', '.ogg', '.flac', '.opus'])
    video_files = get_files_from_folder(video_folder, ['.mp4', '.avi', '.mov', '.flv', '.wmv', '.mkv'])
    
    # Configurar ImageMagick
    change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})
    
    # Construir rutas completas para los archivos seleccionados
    audio_file_path = os.path.join("audiocharacters", personaje)
    video_file_path = os.path.join("fondos", fondo)
    
    # Seleccionar personaje (aleatorio o especificado)
    if random_personaje:
        personaje_path = get_random_file(audio_files, audio_folder)
    else:
        personaje_path = os.path.join(audio_folder, personaje) if personaje else None

    # Seleccionar fondo (aleatorio o especificado)
    if random_fondo:
        fondo_path = get_random_file(video_files, video_folder)
    else:
        fondo_path = os.path.join(video_folder, fondo) if fondo else None

    # Validar que se hayan seleccionado archivos
    if not personaje_path or not fondo_path:
        return "Error: No se ha seleccionado un personaje o fondo válido.", None
    
    #call the spider to get the post content
    capture_reddit_post(url_post, screenshot_output='title_screenshot.png', text_output='post_content.txt')

    gen_text = ""
    with open('post_content.txt', 'r', encoding='utf-8') as file:
        gen_text = file.read()

    # Generar el audio usando F5-TTS
    audio_file = generate_audio(audio_file_path, gen_text)
    print(f"Audio generado: {audio_file}")
    
    # Crear el video con el audio y los subtítulos sincronizados
    create_video_with_captions(
        audio_file,
        output_path,
        fontsize=tamano_fuente,
        resolution=resolucion,
        background_path=video_file_path
    )
    
    return f"Video generado exitosamente en: {output_path}"