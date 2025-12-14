from flask import Flask, request, jsonify
from gtts import gTTS
import os
import subprocess
import time

app = Flask(__name__)

# Path Output untuk Apache (Sesuaikan di server)
OUTPUT_DIR = "/var/www/html/static"

@app.route("/generate", methods=["POST"])
def generate():
    text = request.form.get("text", "")
    if not text: return jsonify({"status": "error", "message": "Teks kosong"})

    filename = f"audio_{int(time.time())}.wav"
    mp3_path = os.path.join(OUTPUT_DIR, "temp.mp3")
    wav_path = os.path.join(OUTPUT_DIR, filename)

    try:
        tts = gTTS(text, lang='id', slow=False)
        tts.save(mp3_path)
        # Convert ke 16kHz Mono
        subprocess.run(["ffmpeg", "-y", "-i", mp3_path, "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le", "-f", "wav", wav_path], check=True)
        if os.path.exists(mp3_path): os.remove(mp3_path)
        return jsonify({"status": "success", "filename": filename})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    app.run(host="127.0.0.1", port=5000)