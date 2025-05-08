FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
COPY IP2LOCATION-LITE-DB1.BIN ./

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
