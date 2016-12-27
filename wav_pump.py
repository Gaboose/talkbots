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

audio_pipe = None
socket = None
aioloop = None

# Consumer-side back-pressure
# I.e. Send a request for another wav after a given amount of time
def request_more(seconds):

    def blocking():
        socket.send_string('gimme moar')
    
    # socket.send_string will block the thread,
    # so for this function to be asynchronous it must be run in a threadpool executor 
    aioloop.run_in_executor(None, blocking)

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

        # Schedule wavs if there are less than 3
        wavs = [f for f in os.listdir(str(workdir.resolve())) if f.endswith('.wav')]
        for i in range(3 - len(wavs)):
            aioloop.call_soon_threadsafe(
                functools.partial(
                    request_more,
                    duration
            ))
        
        # Send raw frames to gstreamer for rtp transmission
        global audio_pipe
        while True:
            try:
                audio_pipe.write(raw)
                break
            except BrokenPipeError:
                print("pipe broken. reopening...")
                audio_pipe = open(str(workdir.joinpath('audio_pipe')), 'wb')
        audio_pipe.flush()

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
    audio_pipe = open(str(workdir.joinpath('audio_pipe')), 'wb')
    print("pipe open")

    # Watch for new wav files in the working directory
    observer = Observer()
    observer.schedule(EventHandler(), str(workdir), recursive=False)
    observer.start()

    try:
        aioloop = asyncio.get_event_loop()
        request_more(0)
        aioloop.run_forever()
    except KeyboardInterrupt:
        pass

    try:
        observer.stop()
    except KeyboardInterrupt:
        pass

    observer.join()