FROM ubuntu:22.04

RUN apt update && apt install -y python3-pip python-is-python3

COPY . .

RUN pip install .

RUN pip install -r requirements.txt

RUN python model/download.py
