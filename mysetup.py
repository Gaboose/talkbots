import os, pathlib

# Can't commit a fifo to git, so we create it here
def ensure_fifo():
    if not os.path.exists('wav_sink'):
        os.mkdir('wav_sink')
    if not os.path.exists('wav_sink/audio_pipe'):
        os.mkfifo('wav_sink/audio_pipe')

if __name__ == '__main__':
    ensure_fifo()
