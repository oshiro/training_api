FROM python:3.10

EXPOSE 8080

ADD src/requirements.txt .

RUN pip install -U pip && pip install -r requirements.txt

ADD src /api

WORKDIR /api

CMD gunicorn --bind 0.0.0.0:8080 wsgi:app
