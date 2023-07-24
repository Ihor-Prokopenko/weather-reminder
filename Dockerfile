FROM python:3.10-bookworm

COPY requirements.txt /wrapi/
COPY . /wrapi/
WORKDIR /wrapi

RUN pip install -r requirements.txt

RUN adduser --disabled-password wrapi-user

USER wrapi-user