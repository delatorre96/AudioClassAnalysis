import pandas as pd
import urllib.request
import moviepy.editor as mp
import os
import numpy as np


def downloadVideo_GetSound(url_link, nombre_destino):
    """
    Descarga un vídeo desde `url_link` y extrae el audio como archivo MP3.
    
    Parameters:
    - url_link (str): URL del vídeo a descargar.
    - nombre_destino (str): Nombre del archivo MP3 de destino.
    """
    # Directorio donde se guardarán los archivos
    directorio = '../audios_de_trabajo'
    
    # Verificar si el directorio existe, si no, crearlo
    if not os.path.exists(directorio):
        os.makedirs(directorio)
        print(f"Directorio '{directorio}' creado correctamente.")
    
    # Descargar el vídeo
    urllib.request.urlretrieve(url_link, f'{directorio}/video1.mp4')
    
    # Cargar el archivo .mp4 como un clip de vídeo
    clip = mp.VideoFileClip(f'{directorio}/video1.mp4')
    
    # Escribir el audio como archivo .mp3
    clip.audio.write_audiofile(f"{directorio}/{nombre_destino}.mp3")
    
    # Confirmar la descarga del audio
    print(f'Audio de {nombre_destino}.mp3 descargado correctamente.')

def iteracion_video ():
    videos_codigo = pd.read_csv('codigo_videos.csv')
    for index,row in videos_codigo.iterrows():
        url_codigo = row['url']
        if pd.isna(url_codigo):
            pass
        else:
            url_link = f'https://medial.mondragon.edu/flash/{url_codigo}_hd.mp4'
            print(f'Vídeo {index}')
            downloadVideo_GetSound (url_link = url_link, nombre_destino = url_codigo)



