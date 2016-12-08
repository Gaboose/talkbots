# TalkBots #

Stream audio of chatter bots talking to one another.

## Get Image ##
Build:
```bash
docker build . --tag gaboose/talkbots
```

Or pull:
```bash
docker pull gaboose/talkbots
```

## Run ##

```bash
$ docker run -it --rm gaboose/talkbots bash
$ python3 chatter.py & python3 wav_pump.py & gst-launch-1.0 -v filesrc location=wav_sink/audio_pipe ! audioparse raw-format=s16le rate=22050 channels=1 ! audiorate ! audioresample ! audioconvert ! rtpL16pay pt=10 ! application/x-rtp, pt=10, encoding-name=L16, payload=10, clock-rate=44100, channels=2 ! udpsink sync=1 host=${STREAM_TARGET} port=5555
```

## Alternative gst-launch commands ##

Stream a sample raw audio instead of fifo pipe

```bash
gst-launch-1.0 -v filesrc location=audio.raw ! audioparse raw-format=U8 rate=44100 channels=1 ! audiorate ! audioconvert ! rtpL16pay pt=10 ! application/x-rtp, pt=10, encoding-name=L16, payload=10, clock-rate=44100, channels=2 ! udpsink sync=1 host=${STREAM_TARGET} port=5555
```
