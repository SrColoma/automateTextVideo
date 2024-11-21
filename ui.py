import os
import gradio as gr
import random
from audio_generator import generate_audio
from video_creator import create_video_with_captions
from moviepy.config import change_settings
from generate_content import generate_content
from utils import get_files_from_folder

# Cargar archivos de las carpetas 'audiocharacters' y 'fondos'y 'audiobackgrounds'
audio_folder = 'audiocharacters'
video_folder = 'fondos'
background_audio_folder = 'audiobackgrounds'

audio_files = get_files_from_folder(audio_folder, ['.wav', '.mp3', '.ogg', '.flac', '.opus'])
video_files = get_files_from_folder(video_folder, ['.mp4', '.avi', '.mov', '.flv', '.wmv', '.mkv'])
background_audio_files = get_files_from_folder(background_audio_folder, ['.wav', '.mp3', '.ogg', '.flac', '.opus'])


# Funciones para las vistas previas
def actualizar_audio_preview(personaje):
    if personaje:
        return os.path.join(audio_folder, personaje)
    return None

def actualizar_video_preview(fondo):
    if fondo:
        return os.path.join(video_folder, fondo)
    return None

def actualizar_audio_fondo_preview(audio_fondo):
    if audio_fondo:
        return os.path.join(background_audio_folder, audio_fondo)
    return None



# Interfaz con Gradio
with gr.Blocks() as interfaz:
    with gr.Row():
        # Columna Izquierda
        with gr.Column():
            # En la Sección 0: Post, después de max_comentarios
            with gr.Group():
                gr.Markdown("### Sección 0: Post")
                url_post = gr.Textbox(label="URL del Post")
                max_comentarios = gr.Number(label="Número máximo de comentarios", value=10)
                translate = gr.Checkbox(label="Traducir página antes de capturar")
                custom_tittle = gr.Checkbox(label="Fondo de título custom")

            # Sección 1: Preconfiguración
            with gr.Group():
                gr.Markdown("### Sección 1: Preconfiguración")
                imagemagick_path = gr.Textbox(label="Ruta de ImageMagick", value="C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe")
                output_path = gr.Textbox(label="Ruta de salida de video", value="./salidas/output_video.mp4")

            # En la Columna Izquierda, antes de la Sección 2
            with gr.Group():
                gr.Markdown("### Sección 2: Manual")
                manual_title = gr.Textbox(label="Título personalizado", placeholder="Ingrese un título personalizado (opcional)")
                manual_content = gr.Textbox(label="Contenido personalizado", placeholder="Ingrese un contenido personalizado (opcional)", lines=8)

        # Columna Derecha
        with gr.Column():
            # Sección 2: Parámetros de Edición
            with gr.Group():
                gr.Markdown("### Sección 3: Parámetros de Edición")
                with gr.Row():
                    personaje = gr.Dropdown(choices=audio_files, label="Seleccionar Personaje", value=None)
                    random_personaje = gr.Checkbox(label="Tomar aleatoriamente")
                personaje_audio_preview = gr.Audio(label="Vista previa del audio", interactive=False)

                with gr.Row():
                    fondo = gr.Dropdown(choices=video_files, label="Seleccionar Video Fondo", value=None)
                    random_fondo = gr.Checkbox(label="Tomar aleatoriamente")
                fondo_video_preview = gr.Video(
                    label="Vista previa del video",
                    interactive=False,
                    height=200,
                    width=300
                )

                with gr.Row():
                    audio_fondo = gr.Dropdown(choices=background_audio_files, label="Seleccionar Audio de Fondo", value=None)
                    random_audio_fondo = gr.Checkbox(label="Tomar aleatoriamente")
                audio_fondo_preview = gr.Audio(label="Vista previa del audio de fondo", interactive=False)

            # Sección 3: Configuración Avanzada
            with gr.Group():
                gr.Markdown("### Sección 4: Configuración Avanzada")
                tamano_fuente = gr.Slider(label="Tamaño de Fuente", minimum=10, maximum=100, step=1, value=44)
                resolucion = gr.Dropdown(choices=["1920x1080", "1280x720", "1080x1920", "720x1280"], label="Resolución", value="720x1280")

    # Conectar las funciones de vista previa
    personaje.change(fn=actualizar_audio_preview, inputs=personaje, outputs=personaje_audio_preview)
    fondo.change(fn=actualizar_video_preview, inputs=fondo, outputs=fondo_video_preview)
    audio_fondo.change(fn=actualizar_audio_fondo_preview, inputs=audio_fondo, outputs=audio_fondo_preview)

    # Sección 4: Generar Video
    with gr.Group():
        gr.Markdown("### Sección 5: Generar Video")
        generar_btn = gr.Button("Generar Video")
        with gr.Row():
            with gr.Column(scale=2):
                resultado = gr.Textbox(label="Resultado", interactive=False)
            with gr.Column(scale=1):
                video_generado = gr.Video(
                    label="Vista previa del video generado",
                    interactive=False,
                    height=200,
                    width=300
                )

        # Conectar la función de generación con el botón
        generar_btn.click(
            generate_content,
            inputs=[
                url_post, max_comentarios, imagemagick_path, output_path,
                personaje, fondo, audio_fondo, random_personaje, random_fondo, random_audio_fondo,
                tamano_fuente, resolucion, translate, custom_tittle, 
                manual_title, manual_content  # Añadidos estos dos nuevos inputs
            ],
            outputs=[resultado, video_generado]
        )

# Lanzar la interfaz
interfaz.launch()