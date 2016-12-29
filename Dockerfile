FROM ubuntu

# Major dependencies
RUN apt-get -y update && \
apt-get -y install python3 espeak gstreamer1.0-tools python3-pip

# pyzmq (from requirements.txt) dependency
RUN apt-get -y install libzmq5 \
# provides rtpL16pay plugin
gstreamer1.0-plugins-good \
# provides audioparse plugin
gstreamer1.0-plugins-bad

ADD . /app
WORKDIR /app

RUN pip3 install -r requirements.txt && \
# Creates wav_sink/audio_pipe fifo and bot1.db, bot2.db files.
python3 mysetup.py

# IP address to stream audio to. May need to override on runtime. E.g.:
# docker run -it --rm -e STREAM_TARGET=192.168.0.16 gaboose/talkbots
ENV STREAM_TARGET 172.17.0.1

CMD python3 chatter.py & python3 wav_pump.py & ./gst-pipeline.sh