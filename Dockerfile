FROM python:3.13
WORKDIR /
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
RUN psql -h 127.0.0.1 -U bron_user -d bron_db -p 5433
RUN Alpha2005@
RUN chmod 755 .
COPY .. .
