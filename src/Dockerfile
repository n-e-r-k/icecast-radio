MAINTAINER nerk@nerksys.net
FROM alpine:latest

RUN apk add python3 ffmpeg

RUN mkdir /radio
COPY ./radio.py /radio/

RUN mkdir /data
VOLUME /data

ENV ICECAST_HOST=0.0.0.0
ENV ICECAST_PORT=8000
ENV USER=source
ENV PASSWORD=password123
ENV DIRECTORY=/data

WORKDIR /data
ENTRYPOINT python3 /radio/radio.py $ICECAST_HOST $ICECAST_PORT $USER $PASSWORD $DIRECTORY
