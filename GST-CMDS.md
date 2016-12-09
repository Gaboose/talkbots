
# Let's get it on #

Caps
```bash
"audio/x-raw, format=U8, layout=interleaved, channels=1, rate=44100"
```

Wav -> Speakers
```bash
gst-launch-1.0 filesrc location=samples/audio.wav ! wavparse ! alsasink
```

Raw -> Speakers
```bash
gst-launch-1.0 filesrc location=samples/audio.raw ! "audio/x-raw, format=(string)U8, layout=(string)interleaved, channels=(int)1, rate=(int)44100" ! alsasink
```

Wav -> RTP
```bash
gst-launch-1.0 filesrc location=samples/audio.wav ! wavparse ! audioconvert ! rtpL16pay pt=10 ! application/x-rtp, channels=2 ! udpsink host=localhost port=5555
```

Raw -> RTP (bad, transmits everything in an instant)
```bash
gst-launch-1.0 filesrc location=samples/audio.raw ! "audio/x-raw, format=(string)U8, layout=(string)interleaved, channels=(int)1, rate=(int)44100" ! audioconvert ! rtpL16pay pt=10 ! application/x-rtp, channels=2 ! udpsink host=localhost port=5555
```

Raw -> RTP (timestamped)
```bash
gst-launch-1.0 filesrc location=samples/audio.raw ! audioparse raw-format=u8 rate=44100 channels=1 ! audioconvert ! rtpL16pay pt=10 ! application/x-rtp, channels=2 ! udpsink host=localhost port=5555
```

# espeak #

Caps
```bash
"audio/x-raw, format=S16LE, layout=interleaved, channels=1, rate=22050"
```

Feed pipe
```bash
(while cat samples/brown.raw; do :; done) > myfifo
```

Raw pipe -> Speakers
```bash
gst-launch-1.0 filesrc location=wav_sink/audio_pipe ! "audio/x-raw, format=(string)S16LE, layout=(string)interleaved, channels=(int)1, rate=(int)22050" ! alsasink
```

Raw pipe -> RTP (timestamped)
```bash
gst-launch-1.0 -v filesrc location=wav_sink/audio_pipe ! audioparse raw-format=s16le rate=22050 channels=1 ! audioresample ! audioconvert ! rtpL16pay pt=10 ! udpsink host=localhost port=5555
```

Raw pipe -> RTP (rtpL16pay caps provide SDP)
```bash
gst-launch-1.0 -v filesrc location=wav_sink/audio_pipe ! audioparse raw-format=s16le rate=22050 channels=1 ! audioresample ! audioconvert ! rtpL16pay pt=10 ! application/x-rtp, pt=10, encoding-name=L16, payload=10, clock-rate=44100, channels=2 ! udpsink host=localhost port=5555
```

Raw pipe -> RTP (timestamps stretched to real clock)
```bash
gst-launch-1.0 filesrc location=wav_sink/audio_pipe do-timestamp=true ! audioparse raw-format=s16le rate=22050 channels=1 ! audioresample ! audioconvert ! rtpL16pay pt=10 ! application/x-rtp, pt=10, encoding-name=L16, payload=10, clock-rate=44100, channels=2 ! udpsink host=localhost port=5555
```

Raw pipe -> RTP (buffer offsets stretched to timestamps)
```bash
gst-launch-1.0 filesrc location=wav_sink/audio_pipe do-timestamp=true ! audioparse raw-format=s16le rate=22050 channels=1 ! audiorate ! audioresample ! audioconvert ! rtpL16pay pt=10 ! application/x-rtp, pt=10, encoding-name=L16, payload=10, clock-rate=44100, channels=2 ! udpsink host=localhost port=5555
```