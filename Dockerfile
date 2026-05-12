FROM python:3.11-slim-bullseye

# 1. Instala as dependências do Sistema Operacional (Agora vai achar o pdfkit!)
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# 2. Define a pasta de trabalho lá dentro do container
WORKDIR /app

# 3. Copia o arquivo de dependências primeiro (ajuda na velocidade do Docker)
COPY requirements.txt .

# 4. Instala as bibliotecas Python que você listou
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia todo o resto do seu projeto para a /app
COPY . .

# 6. Informa qual porta o Streamlit vai usar
EXPOSE 8501

# 7. O comando que o servidor vai executar para ligar sua aplicação
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]