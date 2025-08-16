from pytubefix import YouTube
from groq import Groq
import os
from dotenv import load_dotenv
import re

def create_folders(path_audio:str,path_summary_videos:str):
    os.makedirs(path_audio,exist_ok=True)
    os.makedirs(path_summary_videos,exist_ok=True)

def download_youtube_audio(url:str,path_audio:str,filename:str='audio') -> str:
    """
    Baixa os áudios dos videos do Youtube com a URL informada.
    Args:
        url (str): Link do video do Youtube
        path_audio (str): Local para baixar os arquivos de áudio
        filename (str): Nome do arquivo de áudio
    Returns:
        str: Nome do arquivo de áudio
    Raises:
        Exception: Quaiquer erros
        ValueError: Se nenhum áduio for encontrado
    """
    print('Baixando audio...')
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        if not stream:
            raise ValueError('Nenhum áudio do stream foi encontrado')
        stream.download(path_audio,filename=f'{filename}.mp3')
        return filename
    except Exception as err:
        raise Exception(f'Erro ao baixar video: {err}')

def transcribe_audio(path_audio:str, groq_client:Groq, model_transcription:str = "whisper-large-v3-turbo", language:str = 'pt') -> str:
    """
    Pega o áudio mp3 de `path_audio` e transcreve ele.
    
    Args:
        path_audio (str): Local do arquivo de áudio
        groq_client (Groq): Cliente do Groq
        model_transcription (str): Nome do modelo de transcrição de áudio
        language (str): Transcreve para (pt) 'Português'
    Returns:
        str: Transcrição do áudio

    """
    print('Transcrevendo audio...')
    print(path_audio)
    with open(path_audio,'rb') as file:
        transcription = groq_client.audio.transcriptions.create(
            file=(path_audio, file.read()),
            model=model_transcription,
            language=language,
            response_format="verbose_json",
        )
    os.remove(path_audio)
    return transcription.text

def create_summary(transcription:str,groq_client:Groq,summary_filename:str,model_llm:str = 'qwen/qwen3-32b',language_markdown:str = 'Portugues-BR',out_dir:str = 'summary_videos'):
    """
    Cria um summario com a transcrição do áudio.
    Args:
        transcription (str): 
        groq_client (Groq): 
        summary_filename (str): 
        model_llm (str): 
        language_markdown (str): 
        out_dir (str): 
    Returns:
        Arquivo na pasta `out_dir`

    """
    summary_prompt = f"""
        Você é uma IA que pega o roteiro de um video destaca os pontos principais do video, faz uma explicação do video,
        falando sobre o tema, assunto, exemplos, etc.
        E a resposta deve ser em **{language_markdown}**.
        texto:
        {transcription}
    """

    print('Criando a melhor resposta...')
    llm = groq_client.chat.completions.create(
        model=model_llm,
        messages=[
            {
            "role": "user",
            "content": f"{summary_prompt}\n"
            }
        ],
        temperature=0.6,
        max_completion_tokens=4096,
        top_p=0.95,
        reasoning_effort="default",
        stream=False,
        stop=None
    )

    summary_response = llm.choices[0].message.content
    with open(f'{out_dir}/{summary_filename}.md','w',encoding='utf-8') as markdown:
        text_markdown = re.sub(r'<think>.*?</think>','',summary_response, flags=re.DOTALL)
        markdown.write(f'''{text_markdown}''')
    print('Tudo Pronto!')

def main(url:str, markdown_filename:str, path_audio:str = 'videos_audios', path_summary_videos:str = 'summary_videos') -> None:
    create_folders(path_audio,path_summary_videos)

    loaded_env = load_dotenv()
    if not loaded_env:
        raise ValueError('Chave Api não encontrada. Defina GROQ_API_KEY no ambiente.')
    
    client = Groq()

    audio_file_name = download_youtube_audio(url,path_audio)
    audio_file = f'{path_audio}/{audio_file_name}.mp3'

    transcription_data = transcribe_audio(audio_file,client)
    create_summary(transcription_data,client,summary_filename=markdown_filename)

if __name__ == '__main__':
    url = input('URL do video: ')
    summary_filename = input('Nome do Arquivo: ')
    main(url,summary_filename)