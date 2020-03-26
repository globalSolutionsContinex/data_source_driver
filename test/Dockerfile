FROM python:3.5-stretch

RUN apt-get update
RUN apt-get install -y wget unzip

COPY . /var/www
WORKDIR /var/www

RUN pip3 install -r requirements.txt
RUN chmod +x test/run.sh
RUN ./test/run.sh