import os, pathlib
import chatterbot

# Can't commit a fifo to git, so we create it here
def ensure_fifo():
    if not os.path.exists('wav_sink'):
        os.mkdir('wav_sink')
    if not os.path.exists('wav_sink/audio_pipe'):
        os.mkfifo('wav_sink/audio_pipe')

def process_corpus():
    for name in ['bot1', 'bot2']:
        chatbot = chatterbot.ChatBot(
            'Ron',
            trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
            database=name+'.db'
        )
        chatbot.train("corpus."+name)

if __name__ == '__main__':
    ensure_fifo()
    process_corpus()
