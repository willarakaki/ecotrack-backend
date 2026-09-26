FROM python:3.12-slim

# Evita a criação de arquivos .pyc e força logs a irem direto pro terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalação de dependências do sistema necessárias para o confluent-kafka e pydantic
RUN apt-get update && apt-get install -y \
    build-essential \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY ./app ./app

# Por ser um worker de Kafka, rodamos diretamente o consumer
CMD ["python", "-m", "app.messaging.consumer"]
