FROM --platform=linux/amd64 python:3.9.2

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

##### Requirement install #####
RUN cd ..

COPY . /usr/src/app

RUN cp .env.example .env

RUN pip install -r /usr/src/app/requirements.txt
# COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
