import whisper
from pytubefix import YouTube
yt = YouTube("https://www.youtube.com/watch?v=GCQl9RFns_0")
stream = yt.streams.get_audio_only()
stream.download('Videos')

modelo = whisper.load_model("base")

resposta = modelo.transcribe(f"Audio.m4a")

print(resposta["text"])