FROM python:3.10-bookworm

COPY requirements.txt /weather_reminder/
COPY . /weather_reminder/
WORKDIR /weather_reminder

RUN pip install -r requirements.txt

RUN adduser --disabled-password wrapi-user

USER wrapi-user