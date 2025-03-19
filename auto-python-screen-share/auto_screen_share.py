import time
import pygetwindow as gw
import pywinctl
import pyautogui
import re
import update_checker

def find_meet_window():
    """Trova una finestra attiva di Google Meet."""
    pattern = re.compile(r"Meet - (\w{3,4}-){2}\w{3,4}")
    for window in gw.getWindowsWithTitle("Meet - "):
        if pattern.match(window.title):
            return window
    return None

def share_entire_screen():
    """Simula la selezione dell'intero schermo e avvia la condivisione."""
    # print("[INFO] Attesa del popup di condivisione...")
    # time.sleep(5)  # Tempo per permettere al popup di essere visibile

    print("[INFO] Selezione dell'intero schermo...")
    pyautogui.press("tab")  # Passa alla selezione dello schermo
    time.sleep(0.5)
    pyautogui.press("right")  # Preme la freccia a destra per selezionare l'intero schermo
    time.sleep(0.5)
    pyautogui.press("right")  # Preme la freccia a destra per selezionare l'intero schermo
    time.sleep(0.5)
    
    print("[INFO] Conferma della condivisione...")
    pyautogui.press("tab", presses=2)  # Naviga fino al pulsante "Condividi"
    time.sleep(0.5)
    pyautogui.press("enter")  # Conferma

    print("[SUCCESS] Condivisione avviata!")

def monitor_meet():
    """Controlla continuamente se Meet è aperto e attiva la condivisione."""
    print("[INFO] Avvio monitoraggio continuo di Google Meet...")
    
    last_processed_title = None  # Memorizza l'ultimo titolo di finestra elaborato
    
    while True:
        meet_window = find_meet_window()
        
        if meet_window:
            current_title = meet_window.title
            
            # Controlla se questa finestra è nuova rispetto all'ultima processata
            if current_title != last_processed_title:
                print(f"[INFO] Finestra trovata: {current_title}, attivazione tra 5 secondi...")
                try:
                    time.sleep(5)  # Aspetta 5 secondi prima di attivare la finestra
                    pywinctl.getWindowsWithTitle(current_title)[0].activate()
                    time.sleep(1)  # Aspetta per essere sicuri che la finestra sia in primo piano
                    share_entire_screen()
                    last_processed_title = current_title  # Aggiorna l'ultimo titolo processato
                except Exception as e:
                    print(f"[ERROR] Impossibile attivare la finestra di Meet: {e}")
            else:
                print(f"[INFO] Finestra già processata: {current_title}, attesa di altri 2 minuti...")
            
            # Dopo l'attivazione o la verifica, attendere 2 minuti prima di controllare di nuovo
            print("[INFO] Attesa di 2 minuti prima di controllare una nuova call...")
            time.sleep(120)
        else:
            # Nessuna finestra trovata, riprova tra 1 secondo
            print("[INFO] Nessuna finestra di Meet trovata, riprova tra 1 secondo...")
            last_processed_title = None  # Resetta se non ci sono finestre
            time.sleep(1)

if __name__ == "__main__":
    # Execute update script before starting monitoring
    print("[INFO] Checking for updates...")
    update_checker.update_script()
    print("[INFO] Update check completed. Starting monitoring...")
    monitor_meet()
