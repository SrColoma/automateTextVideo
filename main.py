import os
import gradio as gr
from audio_generator import generate_audio
from video_creator import create_video_with_captions
from moviepy.config import change_settings

# Función para obtener archivos de una carpeta específica
def get_files_from_folder(folder_path, extensions):
    return [f for f in os.listdir(folder_path) if any(f.endswith(ext) for ext in extensions)]

# Función principal para generar audio y video
def generate_content(imagemagick_path, ref_audio_file, gen_text, output_video_path,
                     fontsize, resolution, background_file):
    # Configurar ImageMagick
    change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})
    
    # Construir rutas completas para los archivos seleccionados
    audio_file_path = os.path.join("audiocharacters", ref_audio_file)
    video_file_path = os.path.join("fondos", background_file)
    
    # Generar el audio usando F5-TTS
    audio_file = generate_audio(audio_file_path, gen_text)
    print(f"Audio generado: {audio_file}")
    
    # Crear el video con el audio y los subtítulos sincronizados
    create_video_with_captions(
        audio_file,
        output_video_path,
        fontsize=fontsize,
        resolution=resolution,
        background_path=video_file_path
    )
    
    return f"Video generado exitosamente en: {output_video_path}"

# Interfaz de usuario con Gradio
def main_interface():
    # Rutas de las carpetas
    audio_folder = "audiocharacters"
    video_folder = "fondos"

    # Obtener archivos de las carpetas
    audio_files = get_files_from_folder(audio_folder, ['.wav', '.mp3', '.ogg', '.flac', '.opus'])
    video_files = get_files_from_folder(video_folder, ['.mp4', '.wav', '.avi', '.mov', '.flv', '.wmv', '.mkv'])

    with gr.Blocks() as demo:
        gr.Markdown("# Generador de Video con Audio y Subtítulos")
        
        # Campos para la configuración
        imagemagick_path = gr.Textbox(label="Ruta de ImageMagick", value="C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe")
        
        # Selección de archivos desde menús desplegables
        ref_audio_file = gr.Dropdown(label="Seleccionar Archivo de Audio", choices=audio_files)
        background_file = gr.Dropdown(label="Seleccionar Fondo de Video", choices=video_files)
        
        # Campos de texto
        gen_text = gr.Textbox(label="Texto Generado", placeholder="Ingresa el texto que deseas generar...")
        
        # Parámetros adicionales
        output_video_path = gr.Textbox(label="Ruta de Video de Salida", value="./salidas/output_video.mp4")
        fontsize = gr.Slider(label="Tamaño de Fuente", minimum=10, maximum=100, value=50)
        
        # Cambiado a un menú desplegable para la resolución
        resolution = gr.Dropdown(choices=["1920x1080", "1280x720", "1080x1920", "720x1280"], label="Resolución")
        
        # Botón para generar video
        generate_btn = gr.Button("Generar Video")
        
        # Mensaje de salida
        output_message = gr.Textbox(label="Resultado", interactive=False)
        
        # Acción al hacer clic en el botón
        generate_btn.click(
            generate_content,
            inputs=[imagemagick_path, ref_audio_file, gen_text, output_video_path,
                    fontsize, resolution, background_file],
            outputs=output_message
        )

    demo.launch()

if __name__ == "__main__":
    main_interface()
