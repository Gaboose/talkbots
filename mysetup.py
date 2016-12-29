import os, pathlib
import chatterbot

# Can't commit a fifo or empty folders to git, so we create them here
def ensure_sink_tree():
    if not os.path.exists('wav_sink'):
        os.mkdir('wav_sink')
    if not os.path.exists('wav_sink/audio_pipe'):
        os.mkfifo('wav_sink/audio_pipe')
    if not os.path.exists('wav_sink/L'):
        os.mkdir('wav_sink/L')
    if not os.path.exists('wav_sink/R'):
        os.mkdir('wav_sink/R')


def process_corpus():
    for name in ['bot1', 'bot2']:
        chatbot = chatterbot.ChatBot(
            'Ron',
            trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
            database=name+'.db'
        )
        chatbot.train("corpus."+name)

if __name__ == '__main__':
    ensure_sink_tree()
    process_corpus()
