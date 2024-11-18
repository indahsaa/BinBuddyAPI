# Gunakan base image Python dengan versi yang kompatibel
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Salin requirements.txt dan install dependency
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi ke dalam container
COPY . .

# Set environment variables untuk Flask
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main

# Ekspos port Flask (Dokumentasi saja, tidak memengaruhi runtime)
EXPOSE 8080

# Command untuk menjalankan aplikasi
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]
