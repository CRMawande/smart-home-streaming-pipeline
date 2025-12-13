FROM python:3.11-slim

WORKDIR /app

COPY producer.py .
COPY measurements ./measurements

RUN pip install pandas kafka-python

CMD ["python", "producer.py"]
