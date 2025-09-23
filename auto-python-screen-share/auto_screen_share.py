import time
import pygetwindow as gw
import pywinctl
import pyautogui
import re
import traceback
from datetime import datetime
import update_checker
from logger import get_logger, initialize_logger

def find_meet_window():
    """Trova una finestra attiva di Google Meet."""
    start_time = time.time()
    pattern = re.compile(r"Meet - (\w{3,4}-){2}\w{3,4}")
    windows = gw.getWindowsWithTitle("Meet - ")
    
    for window in windows:
        if pattern.match(window.title):
            search_duration = int((time.time() - start_time) * 1000)
            logger = get_logger()
            logger.log_window_detection(
                meet_window_found=True,
                window_title=window.title,
                window_count=len(windows),
                search_duration_ms=search_duration,
                action_taken="window_found"
            )
            return window
    
    # Nessuna finestra trovata
    search_duration = int((time.time() - start_time) * 1000)
    logger = get_logger()
    logger.log_window_detection(
        meet_window_found=False,
        window_count=len(windows),
        search_duration_ms=search_duration,
        action_taken="no_action_needed"
    )
    return None

def share_entire_screen(meet_window_title: str = None):
    """Simula la selezione dell'intero schermo e avvia la condivisione."""
    start_time = time.time()
    logger = get_logger()
    
    try:
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

        duration_ms = int((time.time() - start_time) * 1000)
        logger.log_screen_share_action(
            action_type="select_screen",
            action_result="success",
            meet_window_title=meet_window_title,
            duration_ms=duration_ms
        )
        print("[SUCCESS] Condivisione avviata!")
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.log_screen_share_action(
            action_type="select_screen",
            action_result="failed",
            meet_window_title=meet_window_title,
            duration_ms=duration_ms,
            error_message=str(e)
        )
        logger.log_error(
            error_type="screen_share_failed",
            error_message=str(e),
            function_name="share_entire_screen",
            meet_window_title=meet_window_title,
            stack_trace=traceback.format_exc()
        )
        print(f"[ERROR] Errore durante la condivisione: {e}")
        raise

def monitor_meet():
    """Controlla continuamente se Meet è aperto e attiva la condivisione."""
    print("[INFO] Avvio monitoraggio continuo di Google Meet...")
    logger = get_logger()
    
    last_processed_title = None  # Memorizza l'ultimo titolo di finestra elaborato
    last_heartbeat = time.time()
    heartbeat_interval = 300  # 5 minuti
    
    while True:
        current_time = time.time()
        
        # Invia heartbeat ogni 5 minuti
        if current_time - last_heartbeat >= heartbeat_interval:
            logger.log_heartbeat(
                status="monitoring",
                meet_windows_detected=1 if find_meet_window() else 0,
                last_action_timestamp=datetime.utcnow().isoformat() + 'Z' if last_processed_title else None
            )
            last_heartbeat = current_time
        
        meet_window = find_meet_window()
        
        if meet_window:
            current_title = meet_window.title
            
            # Controlla se questa finestra è nuova rispetto all'ultima processata
            if current_title != last_processed_title:
                print(f"[INFO] Finestra trovata: {current_title}, attivazione tra 10 secondi...")
                try:
                    time.sleep(10)  # Aspetta 10 secondi prima di attivare la finestra
                    pywinctl.getWindowsWithTitle(current_title)[0].activate()
                    time.sleep(1)  # Aspetta per essere sicuri che la finestra sia in primo piano
                    share_entire_screen(current_title)
                    last_processed_title = current_title  # Aggiorna l'ultimo titolo processato
                except Exception as e:
                    logger.log_error(
                        error_type="window_activation_failed",
                        error_message=str(e),
                        function_name="monitor_meet",
                        meet_window_title=current_title,
                        stack_trace=traceback.format_exc()
                    )
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
    # Inizializza il logger
    logger = initialize_logger()
    
    # Log dell'avvio dell'applicazione
    logger.log_startup()
    
    # Execute update script before starting monitoring
    print("[INFO] Checking for updates...")
    try:
        update_result = update_checker.update_script()
        logger.log_update_check(
            check_performed=True,
            update_available=False,  # update_checker non restituisce info dettagliate
            current_version=logger.version,
            latest_version=logger.version
        )
    except Exception as e:
        logger.log_update_check(
            check_performed=True,
            update_available=False,
            current_version=logger.version,
            latest_version=logger.version,
            error_message=str(e)
        )
        logger.log_error(
            error_type="update_check_failed",
            error_message=str(e),
            function_name="main",
            stack_trace=traceback.format_exc()
        )
    
    print("[INFO] Update check completed. Starting monitoring...")
    monitor_meet()
