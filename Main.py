from fromExcel2csv import exportarCSV
from descargar_audios_videos import iteracion_video
from metricasCalidadAudio import crearDataFrameConMetricas

def main():
    try:
        # Nombre del archivo Excel que contiene los datos de los vídeos
        excel_file = '../videos_maquetados.xlsx'
        
        # Exportar datos del Excel a archivos CSV
        exportarCSV(excel_file)
        
        # Descargar audios de los vídeos
        iteracion_video()
        
        # Calcular métricas de calidad de audio
        crearDataFrameConMetricas()
        
        print("Proceso completado exitosamente.")
        
    except Exception as e:
        print(f"Error durante la ejecución del script: {str(e)}")

if __name__ == "__main__":
    main()

