FROM python:3.7-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . ./

RUN pip install --upgrade pip \
    && pip3 install -r requirements.txt --no-cache-dir

CMD gunicorn api.wsgi:application --bind 0:8000
