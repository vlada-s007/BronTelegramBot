FROM python:3.13
WORKDIR /
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
RUN # pybabel extract --input-dirs=. -o locales/messages.pot
# pybabel update -i locales/messages.pot -d locales -D messages uz
RUN chmod 755 .
COPY .. .
