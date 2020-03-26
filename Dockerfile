FROM python:3.5-stretch

RUN apt-get update

COPY . /var/www
WORKDIR /var/www

RUN pip3 install -r requirements.txt
