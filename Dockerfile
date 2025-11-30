FROM python:3.10-slim

# Install ffmpeg & dependencies
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8000

EXPOSE 8000

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000", "--workers", "1"]
