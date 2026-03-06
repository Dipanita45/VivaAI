import os
from sarvamai import SarvamAI
from sarvamai.play import save
from config import Config


def get_client():
    return SarvamAI(api_subscription_key=Config.SARVAM_API_KEY)


def generate_voice(text):
    client = get_client()

    response = client.text_to_speech.convert(
        text=text,
        target_language_code="en-IN",
        model="bulbul:v3"
    )

    os.makedirs(Config.AUDIO_FOLDER, exist_ok=True)

    # Use a timestamp-based filename to avoid cache issues
    import time
    filename = f"question_{int(time.time())}.wav"
    path = os.path.join(Config.AUDIO_FOLDER, filename)

    save(response, path)

    # Return URL-safe path (always use forward slashes)
    return "/" + path.replace("\\", "/")