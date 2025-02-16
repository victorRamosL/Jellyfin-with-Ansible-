#!/bin/sh

set -x

jellyfin_server="http://localhost:8096"
username="admin"
password="root"
storage_path="/media"
log_file="/tmp/jellyfin-init.log"

{
  echo "Waiting for Jellyfin to start listening on port 8096..."
  for i in $(seq 1 60); do
    if curl -s --max-time 5 --fail "${jellyfin_server}/health" > /dev/null; then
      echo "Jellyfin is now listening on port 8096"
      break
    fi
    echo "Waiting... attempt $i/60"
    sleep 5
  done

  sleep 30

  curl "${jellyfin_server}/Startup/Configuration" \
    -H 'Content-Type: application/json' \
    --data-raw '{"UICulture":"es-ES","MetadataCountryCode":"ES","PreferredMetadataLanguage":"es"}' \
    -vv
  curl "${jellyfin_server}/Startup/User" \
    -vv
  curl "${jellyfin_server}/Startup/User" \
    -H 'Content-Type: application/json' \
    --data-raw '{"Name":"'${username}'","Password":"'${password}'"}' \
    -vv
  curl "${jellyfin_server}/Library/VirtualFolders?collectionType=homevideos&refreshLibrary=true&name=Mis%20Videos" \
    -H 'Content-Type: application/json' \
    --data-raw '{"LibraryOptions":{"EnablePhotos":true,"EnableRealtimeMonitor":true,"EnableInternetProviders":true,"PreferredMetadataLanguage":"es","MetadataCountryCode":"ES","TypeOptions":[{"Type":"Video","ImageFetchers":["Screen Grabber"],"ImageFetcherOrder":["Screen Grabber"]}],"PathInfos":[{"Path":"'${storage_path}'"}]}}' \
    -vv
  curl "${jellyfin_server}/Startup/RemoteAccess" \
    -H 'Content-Type: application/json' \
    --data-raw '{"EnableRemoteAccess":true,"EnableAutomaticPortMapping":false}' \
    -vv
  curl "${jellyfin_server}/Startup/Complete" \
    -X 'POST' \
    -vv
} 2>&1 | tee "${log_file}" 