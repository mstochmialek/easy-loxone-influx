FROM python:3-alpine

WORKDIR /usr/src/app

RUN pip install --no-cache-dir influxdb

COPY *.py .

CMD [ "python", "./Loxone2InfluxDB.py" ]
