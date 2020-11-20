FROM python:3.9-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt

COPY bmw_cd_exporter.py /usr/src/app
COPY attributes.json /usr/src/app

EXPOSE 9488
ENV BMWCD_PORT=9488 BMWCD_INTERVAL=5 BMWCD_REGION=rest_of_world DEBUG=0

ENTRYPOINT [ "python", "-u", "./bmw_cd_exporter.py" ]