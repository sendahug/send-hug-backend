# Dockerfile
FROM python:3.11-slim-buster
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential git

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/

CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8080"]
