FROM python:3.13-slim

COPY . /apps/wifi_portal/

WORKDIR /apps/wifi_portal/

RUN apt-get update && apt-get upgrade

RUN python3 -m pip install --no-cache-dir --upgrade pip

RUN python3 -m pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD [ "/bin/sh", "-c", "python3 main.py >> /var/log/captive_portal.log 2>&1" ]
