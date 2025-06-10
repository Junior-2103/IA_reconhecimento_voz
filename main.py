import whisper
from pytubefix import YouTube
import os

if not os.path.exists('Videos'):
    os.mkdir('Videos')

yt = YouTube("https://www.youtube.com/watch?v=GCQl9RFns_0")
stream = yt.streams.get_audio_only()
stream.download('Videos')

modelo = whisper.load_model("base")

arq = os.listdir('Videos')

resposta = modelo.transcribe(f"Videos/{arq[0]}")

os.remove(f'Videos/{arq[0]}')

print(resposta["text"])