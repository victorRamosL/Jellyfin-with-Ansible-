import requests
import json
import os

# Configuración de la API de Jellyfin
JELLYFIN_URL = "http://victoropss.es:8096"
API_KEY = ""
HEADERS = {
    "X-Emby-Token": API_KEY,
    "Content-Type": "application/json"
}

def obtener_id_video(nombre_archivo):
    """Busca un video en Jellyfin por nombre y devuelve su ID."""
    # Quitamos la extensión .txt del nombre del archivo
    nombre_video = nombre_archivo.replace(".txt", "")
    
    # Codificamos el nombre para la URL
    nombre_codificado = requests.utils.quote(nombre_video)
    
    # Primero obtenemos el ID de la biblioteca
    library_url = f"{JELLYFIN_URL}/Library/MediaFolders"
    print(f"🔍 Obteniendo bibliotecas: {library_url}")
    
    library_response = requests.get(library_url, headers=HEADERS)
    print(f"🔍 Respuesta biblioteca: {library_response.status_code}")
    print(f"🔍 Contenido respuesta: {library_response.text}")
    
    if library_response.status_code == 200:
        libraries = library_response.json()
        library_id = None
        
        # Buscamos la biblioteca VideosVirales
        for library in libraries.get("Items", []):
            if library.get("Name") == "VideosVirales":
                library_id = library.get("Id")
                break
        
        if library_id:
            # Buscamos el video en la biblioteca
            url = f"{JELLYFIN_URL}/Items?Recursive=true&SearchTerm={nombre_codificado}&ParentId={library_id}"
            print(f"🔍 Buscando video: {nombre_video}")
            print(f"🔍 URL de búsqueda: {url}")
            
            response = requests.get(url, headers=HEADERS)
            print(f"🔍 Respuesta búsqueda: {response.status_code}")
            print(f"🔍 Contenido respuesta: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("Items") and len(data["Items"]) > 0:
                    print(f"✅ Encontrado video: {nombre_video} → ID: {data['Items'][0]['Id']}")
                    return data['Items'][0]['Id']
    
    print(f"❌ No se encontró el video: {nombre_video}")
    return None

def actualizar_metadatos(video_id, texto):
    """Sube la transcripción como metadato en Jellyfin."""
    if not video_id:
        return 404
        
    url = f"{JELLYFIN_URL}/Items/{video_id}"
    
    # Creamos un payload más completo basado en la respuesta de la API
    payload = {
        "Name": None,
        "Overview": texto,
        "Taglines": [],
        "Genres": [],
        "Tags": [],
        "Studios": [],
        "People": [],
        "RemoteTrailers": [],
        "ProviderIds": {},
        "IsFolder": False,
        "Type": "Video",
        "VideoType": "VideoFile",
        "LocationType": "FileSystem",
        "MediaType": "Video",
        "LockedFields": [],
        "LockData": False
    }
    
    print(f"📤 Intentando actualizar metadatos para ID: {video_id}")
    print(f"📤 URL: {url}")
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    
    # Cambiamos a POST y añadimos más headers
    headers = HEADERS.copy()
    headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8"
    })
    
    response = requests.post(url, headers=headers, json=payload)
    print(f"🔄 Update Response: {response.status_code}")
    print(f"🔄 Response Text: {response.text}")
    
    return response.status_code

# Buscar transcripciones y enviarlas a Jellyfin
video_folder = "/opt/jellyfin/media/"

for file in os.listdir(video_folder):
    if file.endswith(".txt"):
        video_id = obtener_id_video(file)
        
        if video_id:
            with open(os.path.join(video_folder, file), "r") as f:
                texto = f.read()
            
            status = actualizar_metadatos(video_id, texto)
            print(f"✅ Actualizado: {file} → Status: {status}")
        else:
            print(f"❌ No se pudo actualizar: {file} (video no encontrado)")
