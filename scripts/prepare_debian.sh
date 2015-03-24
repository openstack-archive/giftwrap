#!/bin/bash

apt-get -yqq update
apt-get dist-upgrade -y
apt-get install -yqq build-essential ruby1.9.1-dev git python-pip python-dev python-virtualenv libxml2-dev libxslt-dev libffi-dev libmysqlclient-dev libpq-dev libsqlite3-dev
