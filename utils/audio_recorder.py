import os
from datetime import datetime
from config import Config


def save_audio_file(file):

    os.makedirs("static/audio/answers", exist_ok=True)

    filename = f"answer_{datetime.utcnow().timestamp()}.webm"

    path = os.path.join("static/audio/answers", filename)

    file.save(path)

    return path