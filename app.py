from flask import Flask, request, render_template, send_from_directory, redirect, url_for, session, jsonify
import os
import pymysql
import time
import subprocess
from datetime import datetime
import asyncio
import edge_tts
from functools import wraps

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "rahasia_default")

# Suara Cowok
VOICE_MALE = "id-ID-ArdiNeural"

# ================== DATABASE CONNECTION (CLOUD READY) ==================
import sqlite3 # Tambahkan import ini di atas

# Ganti fungsi koneksi database jadi ini:
def get_db_connection():
    # Database akan dibuat otomatis bernama database.db
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Tambahkan fungsi ini untuk bikin tabel otomatis saat pertama jalan
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Buat tabel users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Buat tabel messages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    # Buat user admin default jika belum ada
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
    
    conn.commit()
    conn.close()

# Panggil init_db() di bagian paling bawah sebelum app.run:
if __name__ == "__main__":
    init_db() # <--- Tambahkan ini
    if not os.path.exists("static"): os.makedirs("static")
    app.run(...)
# =======================================================================

# --- Login & Routes Standar (Sama seperti sebelumnya) ---
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

@app.route("/")
@login_required
def index():
    return render_template("index.html", user=session["user"])

# Fungsi Async TTS
async def generate_audio_edge(text, output_file):
    communicate = edge_tts.Communicate(text, VOICE_MALE)
    await communicate.save(output_file)

# ================== TTS INPUT ==================
@app.route("/tts", methods=["POST"])
@login_required
def tts():
    text = request.form.get("text", "")
    if not text.strip():
        return jsonify({"status": "error", "message": "Teks kosong"})

    waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 1. Simpan ke DB
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO messages (content, status, created_at) VALUES (%s, %s, %s)", (text, "pending", waktu))
        conn.commit()
        conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

    # 2. Generate Audio
    mp3_file = "output.mp3"
    wav_file = os.path.join("static", "output.wav")
    try:
        asyncio.run(generate_audio_edge(text, mp3_file))
        subprocess.run(["ffmpeg", "-y", "-i", mp3_file, "-ar", "44100", "-ac", "2", "-acodec", "pcm_s16le", "-f", "wav", wav_file], check=True)
    except Exception as e:
        return jsonify({"status": "error", "message": "Gagal convert audio"})

    # CATATAN: Kita HAPUS bagian requests.get ke ESP32
    # Karena ESP32 yang akan bertanya ke kita.

    return jsonify({"status": "success", "message": "Pesan terkirim ke Cloud!", "time": waktu})

# ================== ENDPOINT BARU UNTUK ESP32 ==================
@app.route("/api/check_status")
def check_status():
    # Endpoint ini akan dipanggil ESP32 setiap 3 detik
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Cek pesan yang statusnya 'pending'
            cursor.execute("SELECT id FROM messages WHERE status='pending' ORDER BY id ASC LIMIT 1")
            msg = cursor.fetchone()
        conn.close()

        if msg:
            # Jika ada pesan pending, suruh ESP32 download
            # Ganti domain di bawah nanti dengan domain Railway kamu
            return jsonify({"status": "ready"}) 
        else:
            return jsonify({"status": "empty"})
    except:
        return jsonify({"status": "error"})

@app.route("/audio")
def audio():
    return send_from_directory("static", "output.wav", mimetype="audio/wav")

@app.route("/done")
def done():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE messages SET status=%s WHERE status=%s ORDER BY id ASC LIMIT 1", ("done", "pending"))
        conn.commit()
        conn.close()
    except:
        pass
    return "OK"

# Route History dll tetap sama...
@app.route("/history")
@login_required
def history():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 20")
        messages = cursor.fetchall()
    conn.close()
    return render_template("history.html", messages=messages)

# Relay Routes (Disimpan di DB atau Memory Cloud sementara)
relay_state = "off"
@app.route("/relay/on")
@login_required
def relay_on():
    global relay_state
    relay_state = "on" # ESP32 harus polling ini juga kalau mau relay jalan
    return jsonify({"status": "on"})

@app.route("/relay/off")
@login_required
def relay_off():
    global relay_state
    relay_state = "off"
    return jsonify({"status": "off"})
    
@app.route("/relay/status")
def relay_status():
    return jsonify({"status": relay_state})

if __name__ == "__main__":
    if not os.path.exists("static"): os.makedirs("static")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))