import json
from gradio_client import Client, handle_file

def generate_audio(ref_audio_path, gen_text):
    # Load client configuration from clients.json
    with open("clients.json", "r") as f:
        clients = json.load(f)

    # Try each client in the list until one succeeds
    for i, client_config in enumerate(clients):
        try:
            client = Client(client_config["url"])
            # result = client.predict(
            #     ref_audio_orig=handle_file(ref_audio_path),
            #     ref_text="",
            #     gen_text=gen_text,
            #     model="F5-TTS",
            #     remove_silence = False,
            #     cross_fade_duration = 0.15,
            #     speed = 1,
            #     api_name="/infer"
            # )
            result = client.predict(
                ref_audio_input=handle_file(ref_audio_path),
                ref_text_input="",
                gen_text_input=gen_text,
                remove_silence = False,
                cross_fade_duration_slider = 0.15,
                speed_slider = 1,
                api_name="/basic_tts"
            )
            audio_file = result[0]  # Path to the generated audio file
            print(f"Audio generated using client {i+1}.")
            return audio_file
        except:
            # If the current client fails, print an error message and try the next one
            print(f"Error using client {i+1}. Trying the next client.")
            continue

    # If no client succeeded, raise an error
    raise Exception("Unable to generate audio using any of the available clients.")