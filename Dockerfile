FROM python:3-slim-buster

RUN apt-get update && apt-get install -y libgammu-dev && apt-get clean
RUN pip install -U requests python-gammu

ADD gammu-smsdrc /etc/gammu-smsdrc

WORKDIR /app
ADD main.py /app/main.py

ENV WEBHOOK_URL=

ENTRYPOINT [ "python", "/app/main.py" ]
