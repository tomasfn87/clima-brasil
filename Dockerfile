FROM python:3.12-slim

RUN apt update && apt install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "clima_brasil.py"]