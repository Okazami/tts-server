# Gunakan Python versi ringan
FROM python:3.9-slim

# 1. Install System Dependencies (termasuk FFmpeg & Git)
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    apt-get clean

# 2. Setup Working Directory
WORKDIR /app

# 3. Copy file requirements dan install library python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy seluruh kodingan ke dalam container
COPY . .

# 5. Perintah untuk menjalankan aplikasi dengan Gunicorn
# Pastikan app.py kamu object-nya bernama 'app'
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "120"]