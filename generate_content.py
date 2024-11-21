import os
import random
from audio_generator import generate_audio
from video_creator import create_video_with_captions
from moviepy.config import change_settings
from spider import capture_reddit_post
from spider import create_post_txt
from spider import create_custom_screenshot
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
                     audio_fondo, 
                     random_personaje, 
                     random_fondo, 
                     random_audio_fondo, 
                     tamano_fuente, 
                     resolucion,
                     translate,
                     customTittle,
                     manual_title, 
                     manual_content
                     ):
    
    # Cargar archivos de las carpetas 'audiocharacters', 'fondos' y 'audiobackgrounds'
    audio_folder = 'audiocharacters'
    video_folder = 'fondos'
    background_audio_folder = 'audiobackgrounds'

    audio_files = get_files_from_folder(audio_folder, ['.wav', '.mp3', '.ogg', '.flac', '.opus'])
    video_files = get_files_from_folder(video_folder, ['.mp4', '.avi', '.mov', '.flv', '.wmv', '.mkv'])
    background_audio_files = get_files_from_folder(background_audio_folder, ['.wav', '.mp3', '.ogg', '.flac', '.opus'])

    # Configurar ImageMagick
    change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})
    
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

    # Seleccionar audio de fondo (específico o aleatorio)
    if random_audio_fondo:
        background_audio_path = get_random_file(background_audio_files, background_audio_folder)
    else:
        background_audio_path = os.path.join(background_audio_folder, audio_fondo) if audio_fondo else None

    # Validar que se hayan seleccionado archivos necesarios
    if not personaje_path or not fondo_path:
        return "Error: No se ha seleccionado un personaje o fondo válido.", None
    
    # Capturar el contenido del post de Reddit o usar contenido manual
    if not manual_title and not manual_content:
        # Comportamiento original
        capture_reddit_post(url_post, 'title_screenshot.png', 'post_content.txt', translate, customTittle)
    else:
        # Usar contenido manual
        create_post_txt('post_content.txt', manual_title, manual_content)
        create_custom_screenshot(manual_title, 'title_screenshot.png')

    # Leer el contenido del post
    gen_text = ""
    with open('post_content.txt', 'r', encoding='utf-8') as file:
        gen_text = file.read()

    # Generar el audio usando F5-TTS
    audio_file = generate_audio(personaje_path, gen_text)
    print(f"Audio generado: {audio_file}")
    
    # Crear el video con el audio y los subtítulos sincronizados
    create_video_with_captions(
        audio_file,
        output_path,
        fontsize=tamano_fuente,
        resolution=resolucion,
        background_path=fondo_path,
        background_audio_path=background_audio_path,
        background_audio_volume=0.02  # Volumen por defecto para el audio de fondo
    )
    
    return f"Video generado exitosamente en: {output_path}", output_path
