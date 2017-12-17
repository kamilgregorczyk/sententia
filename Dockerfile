FROM python:3
ENV PYTHONUNBUFFERED 1
ENV DEBUG True
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
RUN apt-get update
RUN apt-get install --assume-yes postgresql-client
