FROM python:3-slim-buster

RUN apt-get update && apt-get install -y libgammu-dev build-essential && apt-get clean
RUN pip install -U pip && pip install -U requests python-gammu

ADD gammu-smsdrc /etc/gammu-smsdrc

WORKDIR /app
ADD main.py /app/main.py

ENV WEBHOOK_URL=
ENV PIN=

CMD [ "python", "/app/main.py" ]
