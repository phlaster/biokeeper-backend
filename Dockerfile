FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY python/src ./python/src

CMD ["python", "python/src/FastAPI/main.py"]