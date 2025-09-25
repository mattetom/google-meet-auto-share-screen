import time
import pygetwindow as gw
import pywinctl
import pyautogui
import re
import traceback
from datetime import datetime
import update_checker
from logger import get_logger, initialize_logger
import tkinter as tk
import ctypes
from ctypes import wintypes
import win32gui
import win32con
import win32api
import win32process

def get_available_monitors():
    """Rileva tutti i monitor disponibili usando le API di Windows."""
    try:
        # Definisce le strutture necessarie per le API di Windows
        class RECT(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long),
                       ("top", ctypes.c_long),
                       ("right", ctypes.c_long),
                       ("bottom", ctypes.c_long)]
        
        class MONITORINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_ulong),
                       ("rcMonitor", RECT),
                       ("rcWork", RECT),
                       ("dwFlags", ctypes.c_ulong)]
        
        # Carica le API di Windows
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        
        monitors = []
        
        def enum_monitor_callback(hmonitor, hdc, lprect, lparam):
            """Callback per EnumDisplayMonitors."""
            monitor_info = MONITORINFO()
            monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
            
            if user32.GetMonitorInfoW(hmonitor, ctypes.byref(monitor_info)):
                monitor_data = {
                    'id': len(monitors),
                    'x': monitor_info.rcMonitor.left,
                    'y': monitor_info.rcMonitor.top,
                    'width': monitor_info.rcMonitor.right - monitor_info.rcMonitor.left,
                    'height': monitor_info.rcMonitor.bottom - monitor_info.rcMonitor.top,
                    'is_primary': bool(monitor_info.dwFlags & 1)  # MONITORINFOF_PRIMARY
                }
                monitors.append(monitor_data)
            return True
        
        # Definisce il tipo di callback
        MonitorEnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, 
                                           wintypes.HMONITOR, 
                                           wintypes.HDC, 
                                           ctypes.POINTER(RECT), 
                                           wintypes.LPARAM)
        
        # Enumera tutti i monitor
        callback = MonitorEnumProc(enum_monitor_callback)
        user32.EnumDisplayMonitors(None, None, callback, 0)
        
        # Se non riusciamo a rilevare monitor con le API di Windows, fallback a tkinter
        if not monitors:
            logger = get_logger()
            logger.log_error(
                error_type="monitor_detection_fallback",
                error_message="API Windows non disponibili, uso fallback tkinter",
                function_name="get_available_monitors"
            )
            
            # Fallback usando tkinter
            root = tk.Tk()
            root.withdraw()
            
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            
            monitors.append({
                'id': 0,
                'x': 0,
                'y': 0,
                'width': screen_width,
                'height': screen_height,
                'is_primary': True
            })
            
            root.destroy()
        
        # Log del risultato
        logger = get_logger()
        logger.log_window_move_action(
            action_type="monitor_detection",
            action_result="success",
            monitors_detected=len(monitors),
            duration_ms=0
        )
        
        return monitors
        
    except Exception as e:
        logger = get_logger()
        logger.log_error(
            error_type="monitor_detection_failed",
            error_message=str(e),
            function_name="get_available_monitors",
            stack_trace=traceback.format_exc()
        )
        
        # Fallback finale: restituisce solo il monitor principale con valori di default
        return [{
            'id': 0,
            'x': 0,
            'y': 0,
            'width': 1920,  # Valore di default
            'height': 1080,  # Valore di default
            'is_primary': True
        }]




def get_available_monitors():
    """Rileva tutti i monitor disponibili usando pywin32."""
    try:
        monitors = []
        
        # Monitor principale
        primary_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        primary_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        
        monitors.append({
            'id': 0,
            'x': 0,
            'y': 0,
            'width': primary_width,
            'height': primary_height,
            'is_primary': True
        })
        
        # Prova a rilevare monitor aggiuntivi
        virtual_width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        virtual_height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        virtual_x = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        virtual_y = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        
        # Se il virtual screen è più grande del monitor principale, probabilmente c'è un secondo monitor
        if virtual_width > primary_width or virtual_height > primary_height:
            second_monitor = {
                'id': 1,
                'x': primary_width,  # Il secondo monitor è tipicamente a destra
                'y': 0,
                'width': virtual_width - primary_width,
                'height': virtual_height,
                'is_primary': False
            }
            monitors.append(second_monitor)
        
        # Log del risultato
        logger = get_logger()
        logger.log_window_move_action(
            action_type="monitor_detection",
            action_result="success",
            monitors_detected=len(monitors),
            duration_ms=0
        )
        
        return monitors
        
    except Exception as e:
        logger = get_logger()
        logger.log_error(
            error_type="monitor_detection_failed",
            error_message=str(e),
            function_name="get_available_monitors",
            stack_trace=traceback.format_exc()
        )
        
        # Fallback: restituisce solo il monitor principale con valori di default
        return [{
            'id': 0,
            'x': 0,
            'y': 0,
            'width': 1920,  # Valore di default
            'height': 1080,  # Valore di default
            'is_primary': True
        }]

def move_window_to_second_monitor(window_title: str):
    """Sposta la finestra usando pywin32 con API specifiche di Windows."""
    start_time = time.time()
    logger = get_logger()
    
    try:
        # Ottieni i monitor disponibili usando pywin32
        monitors = get_available_monitors()
        
        if len(monitors) < 2:
            logger.log_window_move_action(
                action_type="move_to_second_monitor",
                action_result="no_second_monitor",
                window_title=window_title,
                monitors_detected=len(monitors),
                duration_ms=int((time.time() - start_time) * 1000)
            )
            print("[INFO] Nessun secondo monitor rilevato, la finestra rimane nel monitor principale")
            return False
        
        # Trova la finestra usando win32gui
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_title in window_text:
                    windows.append((hwnd, window_text))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if not windows:
            logger.log_window_move_action(
                action_type="move_to_second_monitor",
                action_result="window_not_found",
                window_title=window_title,
                monitors_detected=len(monitors),
                duration_ms=int((time.time() - start_time) * 1000)
            )
            print(f"[WARNING] Finestra '{window_title}' non trovata per lo spostamento")
            return False
        
        hwnd = windows[0][0]  # Handle della finestra
        second_monitor = monitors[1]  # Il secondo monitor
        
        print(f"[INFO] Spostamento con pywin32: finestra {hwnd}")
        
        # Ottieni le dimensioni attuali della finestra
        rect = win32gui.GetWindowRect(hwnd)
        window_width = rect[2] - rect[0]
        window_height = rect[3] - rect[1]
        
        
        # Calcola la posizione nel secondo monitor
        target_x = second_monitor['x'] + 50  # 50px dal bordo sinistro
        target_y = second_monitor['y'] + 50  # 50px dal bordo superiore
        
        # Usa SetWindowPos per spostare la finestra
        # SWP_NOZORDER mantiene l'ordine Z, SWP_SHOWWINDOW mostra la finestra
        result = win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOP,
            target_x,
            target_y,
            window_width,
            window_height,
            win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW
        )
        
        # Verifica se la finestra si è effettivamente spostata controllando la posizione
        time.sleep(0.5)  # Aspetta che lo spostamento sia completato
        new_rect = win32gui.GetWindowRect(hwnd)
        new_x = new_rect[0]
        new_y = new_rect[1]
        
        # Considera lo spostamento riuscito se la finestra si è spostata nel secondo monitor
        # (con una tolleranza di 200 pixel per X e 100 pixel per Y)
        moved = (new_x >= second_monitor['x'] - 200 and 
                new_x <= second_monitor['x'] + second_monitor['width'] + 200 and
                abs(new_y - target_y) < 100)
        
        if moved:
            result = True
        else:
            result = False
        
        if result:
            # Attiva la finestra
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            
            # Forza il refresh della finestra
            win32gui.InvalidateRect(hwnd, None, True)
            win32gui.UpdateWindow(hwnd)
            time.sleep(0.5)
            
            duration_ms = int((time.time() - start_time) * 1000)
            logger.log_window_move_action(
                action_type="move_to_second_monitor",
                action_result="success",
                window_title=window_title,
                monitors_detected=len(monitors),
                new_position_x=target_x,
                new_position_y=target_y,
                duration_ms=duration_ms
            )
            
            print(f"[SUCCESS] Finestra spostata con pywin32 alla posizione ({target_x}, {target_y})")
            return True
        else:
            raise Exception("SetWindowPos fallito")
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.log_window_move_action(
            action_type="move_to_second_monitor",
            action_result="failed",
            window_title=window_title,
            monitors_detected=len(monitors) if 'monitors' in locals() else 0,
            duration_ms=duration_ms,
            error_message=str(e)
        )
        logger.log_error(
            error_type="window_move_failed",
            error_message=str(e),
            function_name="move_window_to_second_monitor",
            window_title=window_title,
            stack_trace=traceback.format_exc()
        )
        print(f"[ERROR] Errore durante lo spostamento con pywin32: {e}")
        return False

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
    # search_duration = int((time.time() - start_time) * 1000)
    # logger = get_logger()
    # logger.log_window_detection(
    #     meet_window_found=False,
    #     window_count=len(windows),
    #     search_duration_ms=search_duration,
    #     action_taken="no_action_needed"
    # )
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
        time.sleep(1)
        pyautogui.press("right")  # Preme la freccia a destra per selezionare l'intero schermo
        time.sleep(1)
        pyautogui.press("right")  # Preme la freccia a destra per selezionare l'intero schermo
        time.sleep(1)
        
        print("[INFO] Conferma della condivisione...")
        pyautogui.press("tab", presses=2)  # Naviga fino al pulsante "Condividi"
        time.sleep(1)
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
                print(f"[INFO] Finestra trovata: {current_title}, attivazione tra 20 secondi...")
                try:
                    time.sleep(20)  # Aspetta 20 secondi prima di attivare la finestra
                    pywinctl.getWindowsWithTitle(current_title)[0].activate()
                    time.sleep(10)  # Aspetta per essere sicuri che la finestra sia in primo piano
                    
                    # Sposta la finestra nel secondo monitor prima di condividere lo schermo
                    print("[INFO] Tentativo di spostamento della finestra nel secondo monitor...")
                    move_success = move_window_to_second_monitor(current_title)
                    
                    if move_success:
                        time.sleep(3)  # Aspetta un momento dopo lo spostamento
                        print("[INFO] Finestra spostata con successo, procedo con la condivisione...")
                    else:
                        print("[INFO] Spostamento non riuscito o non necessario, procedo con la condivisione...")
                    
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
