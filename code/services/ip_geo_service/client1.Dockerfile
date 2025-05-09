FROM python:3.11-slim

WORKDIR /client
COPY client/workload_generator.py /client/
RUN pip install requests

CMD ["python", "workload_generator.py"]
