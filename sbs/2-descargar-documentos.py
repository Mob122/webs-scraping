import pandas as pd
import requests
import os

dic_extensiones = {
    'application/pdf': '.pdf',
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/vnd.ms-excel': '.xls',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
    'text/plain': '.txt'
}

def descargar_documentos(df, nombre_carpeta):
  os.makedirs(f'output/documentos/{nombre_carpeta}', exist_ok= True)

  for index, row in df.iterrows():
    enlace = row['enlace']

    try:
        response = requests.get(enlace)        

        response.raise_for_status()  # Lanza un error si la respuesta no es 200.
        nombre_archivo = f"{row['numero_norma']}_{row['version']}" + dic_extensiones.get(response.headers.get('Content-Type'), '')
        ruta_archivo = f'output/documentos/{nombre_carpeta}/{nombre_archivo}'
            
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar {nombre_archivo}: {e}")

    with open(ruta_archivo, 'wb') as f:

        f.write(response.content)

        print(f"Descargado: {nombre_archivo}")        

if __name__ == "__main__":
    df = pd.read_csv('output/enlaces_sbs_sujetos_obligados_supervisados.csv')    

    descargar_documentos(df, 'sbs-sujetos-obligados-supervisados')  # Cambia el nombre de la carpeta según sea necesario.

    print(f"Descarga de documentos finalizada. Total de documentos descargados: {len(df)} y se han guardado {len(os.listdir('output/documentos/sbs-sujetos-obligados-supervisados'))} archivos.")
