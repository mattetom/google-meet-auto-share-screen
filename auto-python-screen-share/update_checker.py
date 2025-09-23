import requests
import os
import subprocess

UPDATE_URL = "http://localhost:3000/api/updates/"
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
    latest_version = get_latest_version()
    if not latest_version:
        print("[ERROR] Impossibile ottenere la versione più recente")
        return False

    local_version = get_local_version()

    if latest_version != local_version:
        print(f"[INFO] Nuova versione disponibile: {latest_version}. Aggiornamento in corso...")
        download_url = f"{UPDATE_URL}auto-screen-share/{latest_version}"
        response = requests.get(download_url, stream=True)

        if response.status_code == 200:
            # Assicurati che la directory esista
            app_data_dir = os.path.join(os.getenv("LOCALAPPDATA"), "AutoScreenShare")
            ensure_directory_exists(app_data_dir)
            
            new_executable = os.path.join(app_data_dir, f"auto-screen-share_{latest_version}.exe")
            
            print(f"[INFO] Scaricando aggiornamento in: {new_executable}")
            with open(new_executable, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            # Assicurati che la directory per il file di versione esista
            ensure_directory_exists(os.path.dirname(LOCAL_VERSION_FILE))
            
            # Aggiorna il file della versione locale
            with open(LOCAL_VERSION_FILE, "w") as file:
                file.write(latest_version)

            print("[SUCCESS] Aggiornamento completato. Riavvio lo script...")

            # Sostituisci il file eseguibile attuale con il nuovo
            os.replace(new_executable, EXECUTABLE_PATH)

            # Riavvia il nuovo script e chiude il vecchio
            subprocess.Popen([EXECUTABLE_PATH])
            os._exit(0)
        else:
            print(f"[ERROR] Impossibile scaricare la nuova versione. Status code: {response.status_code}")
            return False

    return True

# if __name__ == "__main__":
#     print("[INFO] Controllo aggiornamenti...")
#     update_script()
#     print("[INFO] Controllo completato.")