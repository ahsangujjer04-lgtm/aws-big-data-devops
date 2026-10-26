FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

COPY app/ ./app/

CMD ["python", "-m", "unittest", "discover", "-s", "app/tests", "-v"]
