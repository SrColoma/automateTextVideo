# audio_generator.py
from gradio_client import Client, handle_file

def generate_audio(ref_audio_path, ref_text, gen_text, model="F5-TTS", remove_silence=False, cross_fade_duration=0.15, speed=1):
    client = Client("mrfakename/E2-F5-TTS")
    result = client.predict(
        ref_audio_orig=handle_file(ref_audio_path),
        ref_text=ref_text,
        gen_text=gen_text,
        model=model,
        remove_silence=remove_silence,
        cross_fade_duration=cross_fade_duration,
        speed=speed,
        api_name="/infer"
    )
    audio_file = result[0]  # Ruta al archivo de audio generado
    return audio_file
