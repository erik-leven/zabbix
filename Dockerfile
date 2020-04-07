FROM ubuntu:18.04
MAINTAINER Erik levén "erik.leven@sesam.io"
COPY ./service /service

RUN apt-get update 
RUN apt-get install -y \
	python-pip
RUN apt-get install -y \
	python2.7 \
	libssl1.0.0 \
	wget

#install zabbix-sender
RUN wget https://repo.zabbix.com/zabbix/3.0/debian/pool/main/z/zabbix/zabbix-sender_3.0.9-1%2Bwheezy_amd64.deb
RUN dpkg -i zabbix-sender_3.0.9-1+wheezy_amd64.deb
RUN apt-get install zabbix-sender

RUN pip install -r /service/requirements.txt

EXPOSE 5000/tcp

CMD ["python", "-u", "./service/zabbix.py"]
