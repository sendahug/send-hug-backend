# Dockerfile
FROM python:3.11-slim-bookworm
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential git

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/

CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8080"]
