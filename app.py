from flask import Flask, request, render_template, send_from_directory, redirect, url_for, session, jsonify, send_file
from gtts import gTTS
import os
import requests
from functools import wraps
import pymysql
import time
import subprocess
from datetime import datetime # <--- Tambahan untuk waktu realtime

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "ganti_dengan_secret_key_random"

# Pastikan IP ESP32 sesuai
ESP32_BASE = "http://10.152.15.21"
is_playing = False

# ================== MySQL Connection ==================
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
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
        return render_template("login.html", error="Username atau password salah")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated
# =================================================

@app.route("/")
@login_required
def index():
    return render_template("index.html", user=session["user"])

# ================== TTS SYSTEM (MODIFIKASI UTAMA) ==================
@app.route("/tts", methods=["POST"])
@login_required
def tts():
    global is_playing
    text = request.form.get("text", "")

    # 1. Validasi Input
    if not text.strip():
        # Return JSON error (bukan string biasa) agar JS bisa baca
        return jsonify({"status": "error", "message": "Teks tidak boleh kosong"})

    # 2. Ambil Waktu Realtime
    waktu_sekarang = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 3. Simpan ke Database
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Kita masukkan waktu ke kolom created_at
            cursor.execute(
                "INSERT INTO messages (content, status, created_at) VALUES (%s, %s, %s)", 
                (text, "pending", waktu_sekarang)
            )
        conn.commit()
        conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database Error: {e}"})

    # 4. Proses Audio
    mp3_file = "output.mp3"
    wav_file = os.path.join("static", "output.wav")

    try:
        tts_obj = gTTS(text, lang="id")
        tts_obj.save(mp3_file)
        
        # Convert ke WAV
        subprocess.run([
            "ffmpeg", "-y", "-i", mp3_file, 
            "-ar", "44100", "-ac", "2", 
            "-acodec", "pcm_s16le", 
            "-f", "wav", wav_file
        ], check=True)
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Gagal memproses audio: {e}"})

    # 5. Trigger ESP32
    if not is_playing:
        try:
            requests.get(f"{ESP32_BASE}/play", timeout=0.5)
            is_playing = True
        except requests.exceptions.RequestException:
            # ESP32 mungkin offline, tapi pesan tetap tersimpan & sukses di web
            pass

    # 6. RETURN JSON SUKSES (Agar halaman tidak reload)
    return jsonify({
        "status": "success", 
        "message": "Pesan berhasil dikirim ke antrian!",
        "time": waktu_sekarang
    })

@app.route("/audio")
def audio():
    try:
        return send_from_directory("static", "output.wav", mimetype="audio/wav")
    except Exception as e:
        return f"File audio belum siap: {e}", 404

@app.route("/done")
def done():
    global is_playing
    is_playing = False
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE messages SET status=%s WHERE status=%s ORDER BY id ASC LIMIT 1", ("done", "pending"))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")
    return "OK"
# =================================================

# ================== HISTORY PAGE ==================
@app.route("/history")
@login_required
def history():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Ambil created_at juga
        cursor.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 20")
        messages = cursor.fetchall()
    conn.close()
    return render_template("history.html", messages=messages)

# ================== RELAY & STATUS ==================
relay_status = "off" 

@app.route("/relay/on")
@login_required
def relay_on():
    global relay_status
    try:
        requests.get(f"{ESP32_BASE}/relay/on", timeout=2)
        relay_status = "on"
        return jsonify({"status": "on"})
    except:
        return jsonify({"status": "error"})

@app.route("/relay/off")
@login_required
def relay_off():
    global relay_status
    try:
        requests.get(f"{ESP32_BASE}/relay/off", timeout=2)
        relay_status = "off"
        return jsonify({"status": "off"})
    except:
        return jsonify({"status": "error"})

@app.route("/relay/status")
def relay_status_route():
    return jsonify({"status": relay_status})

@app.route("/realtime_status")
def realtime_status():
    pending = 0
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS ct FROM messages WHERE status=%s", ("pending",))
            result = cursor.fetchone()
            if result:
                pending = result["ct"]
        conn.close()
    except Exception:
        pending = 0

    status = {
        "is_playing": is_playing,
        "pending": pending,
        "relay": relay_status,
        "time": int(time.time())
    }
    return jsonify(status)

if __name__ == "__main__":
    if not os.path.exists("static"):
        os.makedirs("static")
    # threaded=True WAJIB ADA
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)