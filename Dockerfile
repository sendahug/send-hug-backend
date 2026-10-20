# Dockerfile
FROM python:3.14-slim-bookworm
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential git
# Min version to fix GHSA-6q48-6c7w-9gw2
RUN python -m pip install "pip @ https://files.pythonhosted.org/packages/3f/06/3e4420302363fbb71be3c7f35ce042f54bfca330e3e66b3a2e3c4cca579f/pip-26.2.2-py3-none-any.whl#sha256=fd7f4dfa8190e014013b9f08f3e973f4e4c26ffd179a204895533a7254813a70"
RUN python -m pip install --upgrade pip

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/

CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8080"]
