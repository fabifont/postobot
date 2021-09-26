FROM python:alpine

WORKDIR /bot
COPY postobot/   /bot/
RUN  apk --no-cache add  firefox py3-numpy postgresql-dev gcc g++ python3-dev musl-dev

RUN sh -c "wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz \ 
            && tar -x geckodriver -zf geckodriver-v0.30.0-linux64.tar.gz -O > /usr/bin/geckodriver \
            && chmod +x /usr/bin/geckodriver \
            && rm geckodriver-v0.30.0-linux64.tar.gz"
RUN pip3 install -r requirements.txt


