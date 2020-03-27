FROM python:3.8-stretch

RUN apt-get update

COPY . /var/www
WORKDIR /var/www

RUN pip3 install -r requirements.txt
