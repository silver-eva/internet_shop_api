FROM python:3.11-alpine

RUN mkdir /src
WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./src /src/

ENTRYPOINT [ "python", "main.py", "-a", "0.0.0.0", "-p", "8000", "--reload" ]