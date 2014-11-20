FROM python:2.7

RUN apt-get update && \
    apt-get -yqq install build-essential ruby-dev ruby git python-pip libxml2-dev libxslt-dev libffi-dev libmysqlclient-dev libpq-dev

RUN gem install --no-ri --no-rdoc fpm

ADD https://get.docker.com/builds/Linux/x86_64/docker-latest /usr/local/bin/docker

RUN chmod +x /usr/local/bin/docker

ADD . /giftwrap

WORKDIR /giftwrap

RUN python setup.py install

CMD giftwrap build -m /tmp/manifest.yml
