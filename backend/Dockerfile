FROM python:3.14-slim

# evita archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# directorio de trabajo dentro del contenedor
WORKDIR /app

# dependencias del sistema necesarias para postgres
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copiar requirements
COPY requirements.txt .

# instalar librerías python
RUN pip install --no-cache-dir -r requirements.txt

# copiar el proyecto
COPY . .