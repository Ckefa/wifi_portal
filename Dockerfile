FROM python:3.13-slim

WORKDIR /app

COPY ./requirements.txt /app

RUN apt-get update && apt-get upgrade -y

RUN python3 -m pip install --no-cache-dir --upgrade pip

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY ./app /app

EXPOSE 8001

CMD [ "sh", "-c", "gunicorn -b 0.0.0.0:80 wsgi:app" ]
