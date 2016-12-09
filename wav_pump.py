import sys
import time
import os, wave
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio, functools

audio_pipe = None
socket = None
aioloop = None
clip_queue = asyncio.Queue()

async def pipe_feed():
    SAMPLERATE = 22050

    audio_pipe.write(bytes(SAMPLERATE*16))

    global audio_pipe
    last = int(time.time()*SAMPLERATE)
    samples_behind = 0
    while True:
        try:
            data = await asyncio.wait_for(clip_queue.get(), 1.0)
            audio_pipe.write(data)
            samples_behind -= len(data)
        except asyncio.TimeoutError:
            now = int(time.time()*SAMPLERATE)
            samples_behind += now - last
            last = now

            if samples_behind > 0:
                audio_pipe.write(bytes(samples_behind * 2))
                samples_behind = 0

    # Send raw frames to gstreamer for rtp transmission
    # global audio_pipe
    # while True:
    #     try:
    #         audio_pipe.write(raw)
    #         break
    #     except BrokenPipeError:
    #         print("pipe broken. reopening...")
    #         audio_pipe = open(str(workdir.joinpath('audio_pipe')), 'wb')
    # audio_pipe.flush()

async def consume_wav(filename):
    print(filename)

    # Read raw frames of the wav file
    with wave.open(filename, 'rb') as wf:
        raw = wf.readframes(wf.getnframes())
        duration = wf.getnframes()/wf.getframerate()
        print("duration: {0:.2f}s".format(duration))
    
    # Remove wav file
    os.remove(filename)
    
    # Request another wav
    request_more(duration)

    await clip_queue.put(raw)

# Send a request for another wav after a given amount of time
# (consumer-side back-pressure)
def request_more(seconds):
    def blocking():
        time.sleep(max(0, seconds-0.4))
        socket.send_string('gimme moar')

    # socket.send_string will block the thread,
    # so for this function to be asynchronous it must be run in a threadpool executor 
    aioloop.run_in_executor(None, functools.partial(blocking))

class EventHandler(FileSystemEventHandler):
    
    # This is called whenever a new file is created in the watched directory
    def on_created(self, event):

        # Only continue if the new file is a wav file
        filename = event.src_path
        _, ext = os.path.splitext(filename)
        if ext != '.wav':
            return
        
        aioloop.call_soon_threadsafe(
            asyncio.Task,
            consume_wav(filename)
        )
        
        # Send raw frames to gstreamer for rtp transmission
        # global audio_pipe
        # while True:
        #     try:
        #         audio_pipe.write(raw)
        #         break
        #     except BrokenPipeError:
        #         print("pipe broken. reopening...")
        #         audio_pipe = open(str(workdir.joinpath('audio_pipe')), 'wb')
        # audio_pipe.flush()

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
        aioloop.run_until_complete(pipe_feed())
    except KeyboardInterrupt:
        pass

    try:
        observer.stop()
    except KeyboardInterrupt:
        pass

    observer.join()