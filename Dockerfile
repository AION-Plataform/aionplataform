FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dependências de sistema para compilar pacotes Python (quando necessário)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências da API
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o projeto para permitir validações de import e uso no container
COPY . .

# Verificação de instalação: garante que o runtime sobe por import
RUN python -c "import runtime.main; print('Runtime import check: OK')"

EXPOSE 8000

# Comando padrão para iniciar a API após instalação
CMD ["uvicorn", "runtime.main:app", "--host", "0.0.0.0", "--port", "8000"]
