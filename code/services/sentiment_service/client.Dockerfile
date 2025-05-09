FROM python:3.11-slim

WORKDIR /app
COPY client/workload_generator.py /app/
RUN pip install requests

CMD ["python", "workload_generator.py"]
