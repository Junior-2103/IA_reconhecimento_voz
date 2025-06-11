import whisper
from pytubefix import YouTube
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

if not os.path.exists('Videos'):
    os.mkdir('Videos')

llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash',temperature=0.8)

yt = YouTube("https://www.youtube.com/watch?v=UdaHy0pxTl4")
stream = yt.streams.get_audio_only()
stream.download('Videos')

modelo = whisper.load_model("base")

arq = os.listdir('Videos')

r = modelo.transcribe(f"Videos/{arq[0]}")

os.remove(f'Videos/{arq[0]}')

messages = [
    ('system',
    '''
    Você é uma IA que pega o roteiro de um video destaca os pontos principais do video, faz uma explicação do video,
    falando sobre o tema, assunto, exemplos, etc.
    E a resposta deve ser em MarkDown para a melhor visualização.
    '''),
    ('human',f'{r["text"]}'),
]

resposta = llm.invoke(messages)

with open('a.md','w',encoding='utf-8') as arquivo:
    arquivo.write(resposta.content)