FROM python:3.11-alpine

RUN mkdir -p /app/src
WORKDIR /app

ARG DB_USER
ARG DB_PASS
ARG DB_HOST
ARG DB_PORT
ARG DB_NAME
ARG DB_SCHEMA

ENV DB_USER=${DB_USER}
ENV DB_PASS=${DB_PASS}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_NAME=${DB_NAME}
ENV DB_SCHEMA=${DB_SCHEMA}

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY main.py /app/main.py

COPY ./src src/

ENTRYPOINT [ "python", "main.py", "-a", "0.0.0.0", "-p", "8000", "--reload" ]