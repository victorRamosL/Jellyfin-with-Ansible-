from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import io
import time
import shutil
import logging
from datetime import datetime, timedelta

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='drive_sync.log'
)

# Si modificas estos scopes, elimina el archivo token.json
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = '11fyrSpAGBSdR8Gypv4985Cf1LqzxVBQ5'  # ID de la carpeta a monitorear
DESTINATION_PATH = '/opt/jellyfin/media'
TOKEN_PATH = 'token.json'
CREDENTIALS_PATH = 'credentials.json'

def get_drive_service():
    """Obtiene el servicio de Google Drive."""
    creds = None
    
    # Cargar credenciales existentes
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    # Si no hay credenciales válidas, solicitar al usuario
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar credenciales
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def get_files_in_folder(service, folder_id):
    """Obtiene la lista de archivos en la carpeta especificada."""
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="files(id, name, modifiedTime, size)"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        logging.error(f"Error al obtener archivos: {str(e)}")
        return []

def download_file(service, file_id, file_name):
    """Descarga un archivo de Drive."""
    try:
        request = service.files().get_media(fileId=file_id)
        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)
        done = False
        
        while not done:
            status, done = downloader.next_chunk()
            if status:
                logging.info(f"Descarga {int(status.progress() * 100)}%")
        
        file_handle.seek(0)
        return file_handle
    except Exception as e:
        logging.error(f"Error al descargar {file_name}: {str(e)}")
        return None

def save_file(file_handle, destination_path, file_name):
    """Guarda el archivo en el sistema local."""
    try:
        full_path = os.path.join(destination_path, file_name)
        with open(full_path, 'wb') as f:
            shutil.copyfileobj(file_handle, f)
        logging.info(f"Archivo guardado: {full_path}")
        return True
    except Exception as e:
        logging.error(f"Error al guardar {file_name}: {str(e)}")
        return False

def main():
    """Función principal."""
    logging.info("Iniciando servicio de sincronización Drive-Jellyfin")
    
    # Verificar y crear directorio de destino si no existe
    if not os.path.exists(DESTINATION_PATH):
        os.makedirs(DESTINATION_PATH)
        logging.info(f"Directorio creado: {DESTINATION_PATH}")
    
    service = get_drive_service()
    processed_files = set()
    
    while True:
        try:
            files = get_files_in_folder(service, FOLDER_ID)
            
            for file in files:
                if file['id'] not in processed_files:
                    logging.info(f"Nuevo archivo encontrado: {file['name']}")
                    
                    file_handle = download_file(service, file['id'], file['name'])
                    if file_handle:
                        if save_file(file_handle, DESTINATION_PATH, file['name']):
                            processed_files.add(file['id'])
                            logging.info(f"Archivo procesado: {file['name']}")
            
            time.sleep(300)  # Esperar 5 minutos antes de la siguiente verificación
            
        except Exception as e:
            logging.error(f"Error en el ciclo principal: {str(e)}")
            time.sleep(60)  # Esperar 1 minuto antes de reintentar

if __name__ == '__main__':
    main() 