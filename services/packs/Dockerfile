FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY database/ database/
COPY packs/ packs/
COPY migrations/ migrations/

RUN useradd --system --no-create-home appuser
USER appuser

CMD ["python", "app.py"]