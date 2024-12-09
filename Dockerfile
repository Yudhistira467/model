# Gunakan image Python yang ringan
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Salin requirements.txt dan instal dependensi
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Salin semua file ke container
COPY . .

# Menentukan port yang akan digunakan oleh container
EXPOSE 8080

# Perintah untuk menjalankan aplikasi
CMD ["gunicorn", "-b", ":8080", "app:app"]