import requests
import os
import subprocess
import time
from logger import get_logger

UPDATE_URL = "https://www.unitretradate.it/api/updates/"
LOCAL_VERSION_FILE = os.path.join(os.getenv("LOCALAPPDATA"), "AutoScreenShare", "version.txt")
# Use underscores to match the installed executable name from the Inno Setup installer
EXECUTABLE_PATH = os.path.join(os.getenv("LOCALAPPDATA"), "AutoScreenShare", "auto_screen_share.exe")

def get_latest_version():
    """Scarica la versione più recente dal server."""
    try:
        response = requests.get(UPDATE_URL + "latest_version.txt")
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException:
        return None

def get_local_version():
    """Legge la versione attuale dallo script installato."""
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "r") as file:
            return file.read().strip()
    return "0.0.0"

def ensure_directory_exists(directory_path):
    """Crea la directory se non esiste."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        print(f"[INFO] Creata directory: {directory_path}")

def update_script():
    """Verifica la versione e aggiorna se necessario."""
    logger = get_logger()
    start_time = time.time()
    
    latest_version = get_latest_version()
    if not latest_version:
        print("[ERROR] Impossibile ottenere la versione più recente")
        logger.log_update_check(
            check_performed=True,
            update_available=False,
            current_version=get_local_version(),
            latest_version=None,
            error_message="Failed to get latest version from server"
        )
        return False

    local_version = get_local_version()
    
    # Log del controllo aggiornamenti
    logger.log_update_check(
        check_performed=True,
        update_available=(latest_version != local_version),
        current_version=local_version,
        latest_version=latest_version
    )

    if latest_version != local_version:
        print(f"[INFO] Nuova versione disponibile: {latest_version}. Aggiornamento in corso...")
        download_url = f"{UPDATE_URL}auto-screen-share/{latest_version}"
        
        logger.log_update_check(
            check_performed=True,
            update_available=True,
            current_version=local_version,
            latest_version=latest_version,
            download_url=download_url,
            update_action="download_started"
        )
        
        download_start_time = time.time()
        response = requests.get(download_url, stream=True)

        if response.status_code == 200:
            # Assicurati che la directory esista
            app_data_dir = os.path.join(os.getenv("LOCALAPPDATA"), "AutoScreenShare")
            ensure_directory_exists(app_data_dir)
            
            new_executable = os.path.join(app_data_dir, f"auto-screen-share_{latest_version}.exe")
            
            print(f"[INFO] Scaricando aggiornamento in: {new_executable}")
            downloaded_size = 0
            with open(new_executable, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
                    downloaded_size += len(chunk)

            download_duration = int((time.time() - download_start_time) * 1000)
            
            # Assicurati che la directory per il file di versione esista
            ensure_directory_exists(os.path.dirname(LOCAL_VERSION_FILE))
            
            # Aggiorna il file della versione locale
            with open(LOCAL_VERSION_FILE, "w") as file:
                file.write(latest_version)

            logger.log_update_check(
                check_performed=True,
                update_available=True,
                current_version=local_version,
                latest_version=latest_version,
                download_url=download_url,
                update_action="download_completed",
                download_size_bytes=downloaded_size,
                download_duration_ms=download_duration
            )

            print("[SUCCESS] Aggiornamento completato. Riavvio lo script...")

            # Sostituisci il file eseguibile attuale con il nuovo
            os.replace(new_executable, EXECUTABLE_PATH)

            logger.log_update_check(
                check_performed=True,
                update_available=True,
                current_version=local_version,
                latest_version=latest_version,
                update_action="restart_initiated"
            )

            # Riavvia il nuovo script e chiude il vecchio
            subprocess.Popen([EXECUTABLE_PATH])
            os._exit(0)
        else:
            error_msg = f"Failed to download new version. Status code: {response.status_code}"
            print(f"[ERROR] Impossibile scaricare la nuova versione. Status code: {response.status_code}")
            logger.log_update_check(
                check_performed=True,
                update_available=True,
                current_version=local_version,
                latest_version=latest_version,
                download_url=download_url,
                update_action="download_failed",
                error_message=error_msg
            )
            return False

    return True

# if __name__ == "__main__":
#     print("[INFO] Controllo aggiornamenti...")
#     update_script()
#     print("[INFO] Controllo completato.")