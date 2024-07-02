import pandas as pd
from pydub import AudioSegment
import numpy as np

def sound2signal(sound):
    """
    Convert an AudioSegment object to a NumPy array representing the audio signal.

    Parameters:
    sound (AudioSegment): The input audio segment.

    Returns:
    numpy.array: The audio signal as a NumPy array.
    """
    signal = np.array(sound.get_array_of_samples())
    return signal
def ruidoIndicador_normalized(signal):
    """
    Calculate the Mean Absolute Error (MAE) of low frequencies and return the denormalized filtered signal.
    
    Parameters:
    signal (numpy.array): The input audio signal.
    
    Returns:
    tuple: A tuple containing the MAE (float) and the denormalized filtered signal (numpy.array).
    """
    signal_norm = signal/np.max(np.abs(signal))
    filtered_signal = np.where((signal_norm < 0.004) & (signal_norm > -0.004), signal_norm, 0)
    filtered_signal_desnorm = signal_norm * np.max(np.abs(signal))
    MAE = np.mean(np.abs(signal_norm - filtered_signal))
    return MAE, filtered_signal_desnorm
def calculate_entropy(signal):
    """
    Calculate the Shannon entropy of a given numpy array representing an audio signal.
    
    Parameters:
    signal (numpy array): The input audio signal.
    
    Returns:
    float: The Shannon entropy of the audio signal.
    """
    # Calculate the histogram
    hist, _ = np.histogram(signal, bins=256, range=(0, 256), density=True)
    
    # Filter out zero values to avoid log(0)
    hist = hist[hist > 0]
    
    # Calculate the entropy
    entropy = -np.sum(hist * np.log2(hist))
    
    return entropy
def extraerCanales(sound):  
    """
    Extract and return the audio channels as NumPy arrays.
    
    Parameters:
    sound (AudioSegment): The input audio segment.
    
    Returns:
    tuple: A tuple containing a list of NumPy arrays representing each audio channel and the number of channels (int).
    """  
    # Divide el audio en canales
    canales = sound.split_to_mono()
    # Convierte cada canal en un array de NumPy
    datos_canales = [np.array(c.get_array_of_samples()) for c in canales]
    n_channels = sound.channels
    return datos_canales, n_channels

def analizar_canales(sound):
    """
    Analyze the audio channels and determine if the audio is mono, stereo, or only audible on one side.
    
    Parameters:
    sound (AudioSegment): The input audio segment.
    
    Returns:
    str: A string indicating the type of channel ("Mono", "Estéreo sólo derecho", "Estéreo sólo izquierdo", "Estéreo").
    """
    datos_canales, n_channels = extraerCanales(sound)
    if n_channels == 1:
        return ("Mono")
    else:
        canal_izquierdo = datos_canales[0]
        canal_derecho = datos_canales[1]
        canal_derecho_sinIntro = canal_derecho[int(len(canal_derecho)/10):int(len(canal_derecho)/1.5)]
        canal_izquierdo_sinIntro = canal_izquierdo[int(len(canal_izquierdo)/10):int(len(canal_izquierdo)/1.5)]
        if np.all(canal_izquierdo_sinIntro == 0):
            return("Estéreo sólo derecho")
            
        elif np.all(canal_derecho_sinIntro == 0):
            return("Estéreo sólo izquierdo")
        else:
            return("Estéreo")

######Para detectar momentos de parada del orador de 10 segundos

def make_chunks(sound, chunk_length):
    """
    Divide an AudioSegment into chunks of a specified length.
    
    Parameters:
    sound (AudioSegment): The input audio segment.
    chunk_length (int): The length of each chunk in milliseconds.
    
    Returns:
    list: A list of AudioSegment objects representing the chunks.
    """
    chunks = [sound[i:i + chunk_length] for i in range(0, len(sound), chunk_length)]
    #chunks_to_array =[np.array(i.get_array_of_samples()) for i in chunks]
    return chunks

def detectar_silenciosIntermedios(sound):
    """
    Detect periods of silence in the audio where the speaker is not talking for at least 10 seconds.
    
    Parameters:
    sound (AudioSegment): The input audio segment.
    
    Returns:
    list: A list of positions (indices) where silence is detected.
    """
    chunk_length = 20000  #Buscamos de 10 en 10 segundos si hay volúmenes bajos
    chunks = make_chunks(sound,chunk_length = chunk_length)
    rms_s = [i.rms for i in chunks]
    rms_s = rms_s[:-6] #Eliminar últimos 6 equivalentes a los últimos 2 mins
    rms_s = rms_s[6:] # Eliminar primeros 6 equivalentes a los primeros 2 mins
    silencios = [i for i in rms_s if i < np.mean(rms_s) - 3*np.std(rms_s)]
    posiciones = [indice for indice, valor in enumerate(rms_s) if valor in silencios]
    min_dondeHaySilencios = [(i*chunk_length)/60000 for i in posiciones]
    return posiciones

##Detectar distorsiones en volumen

def moving_average(data, window_size):
    """
    Calculate the moving average of a given data array.
    
    Parameters:
    data (list): The input data array.
    window_size (int): The size of the moving window.
    
    Returns:
    list: The moving average of the input data.
    """
    return [np.mean(data[i:i + window_size]) for i in range(len(data) - window_size + 1)]

def detectar_distorsiones(sound):
    """
    Detect volume distortions in the audio, identifying both excessively high and low volume segments.
    
    Parameters:
    sound (AudioSegment): The input audio segment.
    
    Returns:
    list: A list of minutes where volume distortions are detected.
    """
    chunk_length = 5000  #Buscamos de 5 en 5 segundos si hay volúmenes bajos
    chunks = make_chunks(sound,chunk_length = chunk_length)
    rms_s = [i.rms for i in chunks]
    rms_s = rms_s[:-12] #Eliminar últimos 12 equivalentes a los últimos 60 segs
    rms_s = rms_s[12:] # Eliminar primeros 12 equivalentes a los primeros 60 segs
    # Aplicar la media móvil
    window_size = int(chunk_length/1000)
    moving_avg = moving_average(rms_s, window_size)
    moving_avg_full = [None] * (window_size - 1) + moving_avg
    #Buscar Residuos
    residuos = [rms_s[i] - moving_avg_full[i] for i in range(len(rms_s)) if moving_avg_full[i] is not None]
    mean_residuos = np.mean(residuos)
    std_residuos = np.std(residuos)
    #Buscar outliers
    outliers = [(i, rms_s[i]) for i in range(len(rms_s)) if moving_avg_full[i] is not None and abs(rms_s[i] - moving_avg_full[i]) > 3 * std_residuos]
    mins_distorsiones = [(i*chunk_length)/60000 for i,j in outliers]
    return mins_distorsiones


def crearDataFrameConMetricas():
    """
    Create a DataFrame containing various audio metrics for a set of audio files.
    
    The function iterates over a list of audio file URLs, processes each file to extract metrics such as RMS, MAE of low frequencies, entropy, type of channel, periods of silence, and volume distortions, and stores these metrics in a DataFrame.
    
    Returns:
    pandas.DataFrame: A DataFrame containing the calculated metrics for each audio file.
    """
    videos_codigo = pd.read_csv('../codigo_videos.csv')
    rms_s = []
    mae_lowFreq_list = []
    signal_entropy_list = []
    lowFrequencies_entropy_list = []
    tipo_canal_list = []
    silenciosIntermedios_list = []
    distorsiones_list = []
    cantidad_distorsiones_list = []
    i = 0
    for index,row in videos_codigo.iterrows():
        print(f'Instancia {i}. {i/len(videos_codigo) * 100}% completado')
        url_codigo = row['url']
        if pd.isna(url_codigo):
            mae_lowFreq_list.append(None)
            signal_entropy_list.append(None)
            lowFrequencies_entropy_list.append(None)
            tipo_canal_list.append(None)
            silenciosIntermedios_list.append(None)
            distorsiones_list.append(None)
            cantidad_distorsiones_list.append(None)
            rms_s.append(None)
        else:
            audio_path = f"../audios_de_trabajo/{url_codigo}.mp3"
            sound = AudioSegment.from_mp3(audio_path)
            signal = sound2signal(sound)
            signal_entropy = calculate_entropy(signal)
            mae_lowFreq, filtered_signal_desnorm = ruidoIndicador_normalized(signal)
            lowFrequencies_entropy =  calculate_entropy(filtered_signal_desnorm)
            tipo_canal = analizar_canales(sound)
            silenciosIntermedios = detectar_silenciosIntermedios(sound)
            distorsiones = detectar_distorsiones(sound)
            tipo_canal_list.append(tipo_canal)
            silenciosIntermedios_list.append(silenciosIntermedios)
            distorsiones_list.append(distorsiones)
            cantidad_distorsiones_list.append(len(distorsiones))
            rms_s.append(sound.rms)
            mae_lowFreq_list.append(mae_lowFreq)
            signal_entropy_list.append(signal_entropy)
            lowFrequencies_entropy_list.append(lowFrequencies_entropy)
        i += 1
    videos_codigo['volumen(rms)'] = rms_s
    videos_codigo['proporcion_frecuenciasBajas'] = mae_lowFreq_list
    videos_codigo['tipo_canal'] = tipo_canal_list
    videos_codigo['silencios_intermedios'] = silenciosIntermedios_list
    videos_codigo['cantidad_distorsiones'] = cantidad_distorsiones_list
    videos_codigo['distorsiones'] = distorsiones_list
    videos_codigo['entropia_frecuenciasBajas'] = lowFrequencies_entropy_list
    videos_codigo['entropia_total'] = signal_entropy_list

    videos_codigo.to_csv('../audioClases_IndicadoresCalidad.csv')

crearDataFrameConMetricas()