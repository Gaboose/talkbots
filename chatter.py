from chatterbot import ChatBot
import chatterbot.trainers
import time
from subprocess import call

__doc__ = """
Creates wav files with chatterbot and espeak and puts them into
wav_sink directory for wav_pump.py to consume them.
"""

import pathlib
workdir = pathlib.Path(__file__).resolve().parent.joinpath('wav_sink')

socket = None

class AudioProducer:

    def __init__(self):
        self.i = 0
        
    def produce(self, text, args, outdir):
        print(text)
        call(['espeak',
            '-w', str(outdir.joinpath('out'+str(self.i)+'.wav')),
            text] + args)
        self.i += 1

def main():
    chatbot1 = ChatBot('UK',
                       read_only=True,
                       storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
                       database='bot1')
    chatbot2 = ChatBot('US',
                       read_only=True,
                       storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
                       database='bot2')
    voice1 = ['-v', 'en-uk', '-p', '100', '-s', '140']
    voice2 = ['-v', 'en-us', '-p', '40', '-s', '160']

    text2speech = AudioProducer()

    socket.recv()
    line_of_dialog = 'Hello, how are you?'
    text2speech.produce(line_of_dialog, voice2, workdir.joinpath('R'))
    socket.recv()

    while True:
        line_of_dialog = chatbot1.get_response(line_of_dialog).text
        text2speech.produce(line_of_dialog, voice1, workdir.joinpath('L'))
        
        socket.recv()

        line_of_dialog = chatbot2.get_response(line_of_dialog).text
        text2speech.produce(line_of_dialog, voice2, workdir.joinpath('R'))

        socket.recv()

if __name__ == '__main__':

    # Remove any pre-existing wav files in the wav_sink folder
    import os
    for fname in os.listdir(str(workdir)):
        if os.path.splitext(fname)[1] == '.wav':
            os.remove(str(workdir.joinpath(fname)))

    # Establish a connection with wav consumer (wav_pump.py)
    import zmq
    ctx = zmq.Context()
    socket = ctx.socket(zmq.PULL)
    socket.connect('tcp://127.0.0.1:5656')

    main()