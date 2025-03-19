import requests
import os
import subprocess

UPDATE_URL = "https://tuoserver.com/updates/"
LOCAL_VERSION_FILE = os.path.join(os.getenv("LOCALAPPDATA"), "AutoScreenShare", "version.txt")
EXECUTABLE_PATH = os.path.join(os.getenv("LOCALAPPDATA"), "AutoScreenShare", "auto-screen-share.exe")

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

def update_script():
    """Verifica la versione e aggiorna se necessario."""
    latest_version = get_latest_version()
    if not latest_version:
        print("[ERROR] Impossibile ottenere la versione più recente")
        return False

    local_version = get_local_version()

    if latest_version != local_version:
        print(f"[INFO] Nuova versione disponibile: {latest_version}. Aggiornamento in corso...")
        download_url = f"{UPDATE_URL}auto-screen-share_{latest_version}.exe"
        response = requests.get(download_url, stream=True)

        if response.status_code == 200:
            new_executable = os.path.join(os.getenv("LOCALAPPDATA"), "AutoScreenShare", f"auto-screen-share_{latest_version}.exe")
            with open(new_executable, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

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
            print("[ERROR] Impossibile scaricare la nuova versione")
            return False

    return True

# if __name__ == "__main__":
#     print("[INFO] Controllo aggiornamenti...")
#     update_script()
#     print("[INFO] Controllo completato.")