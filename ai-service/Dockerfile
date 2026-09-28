FROM python:3.12-slim

# Evita a criacao de arquivos .pyc e forca logs a irem direto pro terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalacao de dependencias do sistema necessarias para o confluent-kafka
RUN apt-get update && apt-get install -y \
    build-essential \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download do modelo em portugues do spaCy para o Microsoft Presidio
RUN python -m spacy download pt_core_news_sm

# Copia o codigo da aplicacao
COPY ./app ./app

# Por padrao executa o worker consumidor de evidencias do Kafka
CMD ["python", "-m", "app.messaging.consumer"]
