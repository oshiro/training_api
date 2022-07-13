FROM python:3.10

ADD src /api

WORKDIR /api

RUN pip install -U pip && pip install -r requirements.txt

EXPOSE 8080

CMD gunicorn --bind 0.0.0.0:8080 wsgi:app