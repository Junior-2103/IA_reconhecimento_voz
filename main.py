import whisper

modelo = whisper.load_model("base")

resposta = modelo.transcribe(f"Audio.ogg")

print(resposta["text"])