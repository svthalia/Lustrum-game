# syntax=docker/dockerfile:1
FROM node:16
RUN apt-get update || : && apt-get install python3 python3-pip gcc musl-dev python3-dev libffi-dev libssl-dev cargo -y
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt
#RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -;
#ENV NPM_BIN_PATH="/usr/local/bin/npm"
COPY . /code/
