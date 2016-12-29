import sys
import time
import os, wave
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio, functools

__doc__ = """
Watches wav_sink for wav files and feeds their raw frames to wav_sink/audio_pipe
for the gst pipeline to consume.
"""

socket = None
aioloop = None
pump = None

# Consumer-side back-pressure
# I.e. Send a request for another wav after a given amount of time
def request_more(seconds):

    def blocking():
        socket.send_string('gimme moar')
    
    # socket.send_string will block the thread,
    # so for this function to be asynchronous it must be run in a threadpool executor 
    aioloop.run_in_executor(None, blocking)


from itertools import chain, repeat, zip_longest, tee

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def interleave(raw, bytes_per_sample, pan='center'):
    """ Pan audio frames by interleaving zero-bytes. """
    if pan == 'left':
        a = grouper(list(raw), bytes_per_sample)
        b = repeat((0,)*bytes_per_sample)
    elif pan == 'right':
        a = repeat((0,)*bytes_per_sample)
        b = grouper(list(raw), bytes_per_sample)
    else:
        a = grouper(list(raw), bytes_per_sample)
        a, b = tee(a)
    
    c = chain.from_iterable(chain.from_iterable(zip(a, b)))
    return bytes(c)

class EventHandler(FileSystemEventHandler):
    
    # This is called whenever a new file is created in the watched directory
    def on_created(self, event):

        # Only continue if the new file is a wav file
        filename = event.src_path
        _, ext = os.path.splitext(filename)
        if ext != '.wav':
            return

        print(filename)

        # Read raw frames of the wav file
        with wave.open(filename, 'rb') as wf:
            raw = wf.readframes(wf.getnframes())
            duration = wf.getnframes()/wf.getframerate()
            print("duration: {0:.2f}s".format(duration))
        
        # Remove wav file
        os.remove(filename)

        aioloop.call_soon_threadsafe(
            functools.partial(
                request_more,
                duration
        ))

        if '/L/' in filename:
            raw = interleave(raw, 2, 'left')
        elif '/R/' in filename:
            raw = interleave(raw, 2, 'right')
        else:
            raw = interleave(raw, 2, 'center')
        
        # Send raw frames to gstreamer for rtp transmission
        aioloop.call_soon_threadsafe(
            functools.partial(
                asyncio.Task,
                pump.put(raw, duration)
        ))

class PumpOut:

    def __init__(self, path):
        self.audio_pipe = open(path, 'wb')
        self.lagging = 0.0

    # Write wav frames to audio_pipe
    async def put(self, raw, duration):
        self.audio_pipe.write(raw)
        self.audio_pipe.flush()
        self.lagging -= duration
    
    # Ensure audio_pipe is fed with frames even if 'put' calls fall behind real-time
    async def fill_silence(self):
        byterate = 44100*2
        silence = b'\x00'*(byterate//10)

        import random
        noise = bytes([random.getrandbits(8) for i in range(byterate)])

        last = time.time()
        while True:

            while self.lagging >= 0.1:
                self.audio_pipe.write(silence)
                self.audio_pipe.flush()
                self.lagging -= 0.1
            
            await asyncio.sleep(0.1)
            now = time.time()
            self.lagging += now - last
            last = now


if __name__ == "__main__":

    # Establish a connection with wav producer (chatter.py)
    import zmq
    ctx = zmq.Context()
    socket = ctx.socket(zmq.PUSH)
    socket.bind('tcp://127.0.0.1:5656')

    # Find the directory of this python script
    import pathlib
    workdir = pathlib.Path(__file__).resolve().parent.joinpath('wav_sink')

    # Open the audio_pipe in the working directory
    print("opening audio_pipe...")
    pump = PumpOut(str(workdir.joinpath('audio_pipe')))
    print("pipe open")

    # Watch for new wav files in the working directory
    observer = Observer()
    observer.schedule(EventHandler(), str(workdir), recursive=True)
    observer.start()

    try:
        aioloop = asyncio.get_event_loop()
        asyncio.Task(pump.fill_silence())
        request_more(0)
        aioloop.run_forever()
    except KeyboardInterrupt:
        pass

    try:
        observer.stop()
    except KeyboardInterrupt:
        pass

    observer.join()