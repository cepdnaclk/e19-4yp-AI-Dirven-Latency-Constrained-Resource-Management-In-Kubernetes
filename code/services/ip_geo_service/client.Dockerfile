FROM python:3.11-slim

WORKDIR /client
COPY client/client.py /client/
RUN pip install requests

CMD ["python", "client.py"]
