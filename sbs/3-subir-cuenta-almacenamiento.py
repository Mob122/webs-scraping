from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

import os

from dotenv import load_dotenv

load_dotenv()

CADENA_CONEXION = os.getenv('CADENA_CONEXION')
NOMBRE_CONTENEDOR = os.getenv('NOMBRE_CONTENEDOR')

def subir_blob(ruta_archivo_local, nombre_contenedor, nombre_blob):
    # Obtener el BlobClient para interactuar con el blob especifico.
    cliente_blob = cliente_servicio.get_blob_client(container= nombre_contenedor, blob= nombre_blob)

    # Comprobar si el blob ya existe.
    try:
        cliente_blob.get_blob_properties()
        print(f'El blob {nombre_blob} ya existe en el contenedor {nombre_contenedor}.')
        return
    except ResourceNotFoundError:
        print(f'El blob {nombre_blob} no existe en el contenedor {nombre_contenedor}.')
        
    # Subir el archivo al blob.
    with open(ruta_archivo_local, 'rb') as archivo:
        # Configuración del contenido.
        configuracion_contenido = ContentSettings(content_type= 'text/plain', content_encoding= 'utf-8', content_disposition= 'inline')

        # Parametros overwrite y content_settings.
        cliente_blob.upload_blob(archivo, content_settings= configuracion_contenido, overwrite= True)

        print(f'Blob {nombre_blob} subido al contenedor {nombre_contenedor}.')

if __name__ == '__main__':
    # Crear un cliente para el servicio de almacenamiento de Azure.
    cliente_servicio = BlobServiceClient.from_connection_string(CADENA_CONEXION)

    try:
        cliente_contenedor = cliente_servicio.create_container(NOMBRE_CONTENEDOR) # No se puede utilizar guiones.
        print('Contenedor creado.')
    except ResourceExistsError:
        print('El contenedor ya existe.')
        
    # Cambiar la ruta según sea necesario.
    path = 'output/metadata'

    for i, archivo in enumerate(os.listdir(path), start= 1):            
        # Cambiar la ruta según sea necesario.
        subir_blob(f'{path}/{archivo}', nombre_contenedor= NOMBRE_CONTENEDOR, nombre_blob= archivo)