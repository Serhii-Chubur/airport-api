FROM python:3.12-alpine3.17
LABEL authors="Dell"

ENV PYTHONUNBUFFERED=1


WORKDIR /airport-api
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p /files/media
RUN adduser -D my_user
RUN chown -R my_user /files/media
RUN chmod -R 755 /files/media

USER my_user
