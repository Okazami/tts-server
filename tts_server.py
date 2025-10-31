from flask import Flask, request, render_template, send_from_directory, redirect, url_for, session
from gtts import gTTS
import os
import requests
from functools import wraps
import pymysql

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "ganti_dengan_secret_key_random"

ESP32_BASE = "http://192.168.1.100"   # ganti sesuai IP ESP32 kamu
is_playing = False  # flag status play audio

# ================== MySQL Connection ==================
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",       # ganti user MySQL kamu
        password="",       # ganti password MySQL kamu
        database="flask_app",
        cursorclass=pymysql.cursors.DictCursor
    )
# ======================================================

# ================= LOGIN SYSTEM ==================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()

        conn.close()

        if user:
            session["user"] = user["username"]
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Username atau password salah")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function
# =================================================

@app.route("/")
@login_required
def index():
    return render_template("index.html", user=session["user"])

# --- Text to Speech ---
@app.route("/tts", methods=["POST"])
@login_required
def tts():
    global is_playing
    text = request.form.get("text", "Halo dari Google TTS")

    # Buat file audio
    tts = gTTS(text, lang="id")
    tts.save("output.mp3")
    os.system("ffmpeg -y -i output.mp3 -ar 44100 -ac 2 -f wav static/output.wav")

    # Panggil ESP32 hanya jika belum mainkan audio
    if not is_playing:
        try:
            requests.get(f"{ESP32_BASE}/play", timeout=2)
            is_playing = True
            return "Teks sudah diubah jadi suara! ESP32 dipanggil."
        except Exception as e:
            return f"File dibuat, tapi gagal panggil ESP32: {e}"
    else:
        return "Teks sudah diubah jadi suara! (Menunggu ESP32 selesai)."

# --- Audio untuk ESP32 (TANPA login) ---
@app.route("/audio")
def audio():
    return send_from_directory("static", "output.wav", mimetype="audio/wav")

# Reset flag dari ESP32 setelah selesai (TANPA login)
@app.route("/done")
def done():
    global is_playing
    is_playing = False
    return "ESP32 selesai mainkan audio."

# --- Relay Control ---
@app.route("/relay/<state>")
@login_required
def relay(state):
    try:
        if state == "on":
            r = requests.get(f"{ESP32_BASE}/relay/on", timeout=2)
            return f"Relay dinyalakan ({r.text})"
        elif state == "off":
            r = requests.get(f"{ESP32_BASE}/relay/off", timeout=2)
            return f"Relay dimatikan ({r.text})"
        else:
            return "Perintah relay tidak dikenal"
    except Exception as e:
        return f"Gagal menghubungi ESP32: {e}"

if __name__ == "__main__":
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(host="0.0.0.0", port=5000, debug=True)
