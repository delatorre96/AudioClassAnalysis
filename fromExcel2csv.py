import pandas as pd
import numpy as np

def lista_tiene_nans(lista):
    #lista_str = [str(i) for i in lista]
    return all(elem in ['nan', None, 'None',np.nan] for elem in lista)

def crearDataFrame (excel_file):
    xls = pd.ExcelFile(excel_file)

    sheet_names = xls.sheet_names

    codigo_asignatura_s = []
    url_s = []
    sesion_s = []
    intancia = 0
    codigo_videos_dict = {} 
    for sheet_name in sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        if 'Ejercicio' in df.columns:
            if lista_tiene_nans(sesion_practica):
                sesion = list(df['Sesión'])
                url = list(df['Código'])
                codigo_asignatura = [sheet_name for _ in range(len(sesion))]
                for i in range(len(codigo_asignatura)):
                    codigo_videos_dict[intancia] = {'codigo_asignatura': codigo_asignatura[i],'url': url[i],'sesion':sesion[i]} 
                    intancia += 1
            else:
                sesion_teorica = list(df['Sesión'])
                codigo_teorica = list(df['Código'])
                sesion_practica = list(df['Ejercicio'])
                codigo_practica = list(df['Código.1'])
                sesion = sesion_teorica + sesion_practica
                url = codigo_teorica + codigo_practica
                codigo_asignatura = [sheet_name for _ in range(len(url))]
                for i in range(len(codigo_asignatura)):
                    codigo_videos_dict[intancia] = {'codigo_asignatura': codigo_asignatura[i],'url': url[i],'sesion':sesion[i]} 
                    intancia += 1
        else:
            sesion = list(df['Sesión'])
            url = list(df['Código'])
            codigo_asignatura = [sheet_name for _ in range(len(sesion))]
            for i in range(len(codigo_asignatura)):
                    codigo_videos_dict[intancia] = {'codigo_asignatura': codigo_asignatura[i],'url': url[i],'sesion':sesion[i]} 
                    intancia += 1
    return codigo_videos_dict

def exportarCSV(excel_file):
    codigo_videos_dict = crearDataFrame (excel_file)
    codigo_videos = pd.DataFrame(codigo_videos_dict).T
    codigo_videos_sin_nans = codigo_videos.dropna(subset=['url'])
    codigo_videos_sin_nans.to_csv('../codigo_videos.csv', index= False)

