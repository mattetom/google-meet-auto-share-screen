import time
import pygetwindow as gw
import pywinctl
import pyautogui

def find_meet_window():
    """Trova una finestra attiva di Google Meet."""
    for window in gw.getWindowsWithTitle("Meet - izq-dpey-uuo"):  # Il titolo delle call di Meet inizia con "Meet - <nome>"
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

    while True:
        meet_window = find_meet_window()
        
        if meet_window:
            print(f"[INFO] Finestra trovata: {meet_window.title}, attivazione tra 10 secondi...")
            try:
                time.sleep(5) # Aspetta 10 secondi prima di attivare la finestra
                pywinctl.getWindowsWithTitle(meet_window.title)[0].activate()
                time.sleep(1) # Aspetta per essere sicuri che la finestra sia in primo piano
                share_entire_screen()
            except Exception as e:
                print(f"[ERROR] Impossibile attivare la finestra di Meet: {e}")
            
            # Dopo l'attivazione, attendere qualche minuto prima di cercare di nuovo
            print("[INFO] Attesa di 2 minuti prima di controllare una nuova call...")
            time.sleep(120)
        else:
            # Nessuna finestra trovata, riprova tra 10 secondi
            print("[INFO] Nessuna finestra di Meet trovata, riprova tra 1 secondo...")
            time.sleep(1)

if __name__ == "__main__":
    monitor_meet()
