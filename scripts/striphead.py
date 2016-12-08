import wave, os, sys

filename = sys.argv[1]
rawname = os.path.splitext(filename)[0] + ".raw"

with wave.open(filename, 'rb') as wf:
    data = wf.readframes(wf.getnframes())

with open(rawname, 'wb') as f:
    f.write(data)