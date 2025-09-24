import requests
import json
import time
import platform
import os
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

class AutoScreenShareLogger:
    """Logger per inviare log al server remoto."""
    
    def __init__(self, api_url: str, api_key: str, version: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.version = version
        self.computer_name = platform.node()
        self.os_version = f"{platform.system()} {platform.release()}"
        self.python_version = platform.python_version()
        self.start_time = time.time()
        
        # Configurazione per retry
        self.max_retries = 3
        self.retry_delay = 1  # secondi
        
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Esegue una richiesta HTTP con retry automatico."""
        url = f"{self.api_url}/api/logs/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, json=data, headers=headers, timeout=10)
                if response.status_code == 200:
                    return True
                else:
                    print(f"[LOGGER WARNING] Server returned status {response.status_code}: {response.text}")
            except requests.RequestException as e:
                print(f"[LOGGER WARNING] Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
        
        print(f"[LOGGER ERROR] Failed to send log after {self.max_retries} attempts")
        return False
    
    def _get_base_data(self) -> Dict[str, Any]:
        """Restituisce i dati base per tutti i log."""
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'application_type': 'python_desktop',
            'version': self.version,
            'system_info': {
                'computer_name': self.computer_name,
                'os_version': self.os_version,
                'python_version': self.python_version
            }
        }
    
    def log_startup(self, update_info: Optional[Dict[str, Any]] = None):
        """Log dell'avvio dell'applicazione."""
        data = self._get_base_data()
        data['update_info'] = update_info or {
            'update_check_performed': False,
            'update_available': False,
            'current_version': self.version,
            'latest_version': self.version
        }
        
        print(f"[LOGGER] Sending startup log...")
        self._make_request('startup', data)
    
    def log_window_detection(self, meet_window_found: bool, window_title: str = None, 
                           window_count: int = 0, search_duration_ms: int = 0,
                           action_taken: str = "no_action_needed", error_details: str = None):
        """Log del rilevamento delle finestre Meet."""
        data = self._get_base_data()
        data['detection_result'] = {
            'meet_window_found': meet_window_found,
            'window_title': window_title,
            'window_count': window_count,
            'search_duration_ms': search_duration_ms
        }
        data['action_taken'] = action_taken
        data['error_details'] = error_details
        
        print(f"[LOGGER] Sending window detection log...")
        self._make_request('window-detection', data)
    
    def log_screen_share_action(self, action_type: str, action_result: str, 
                              meet_window_title: str = None, attempts_made: int = 1,
                              duration_ms: int = 0, error_message: str = None):
        """Log delle azioni di condivisione schermo."""
        data = self._get_base_data()
        data['action_type'] = action_type
        data['action_result'] = action_result
        data['meet_window_title'] = meet_window_title
        data['action_details'] = {
            'attempts_made': attempts_made,
            'duration_ms': duration_ms,
            'error_message': error_message
        }
        
        print(f"[LOGGER] Sending screen share action log...")
        self._make_request('screen-share', data)
    
    def log_update_check(self, check_performed: bool, update_available: bool = False,
                        current_version: str = None, latest_version: str = None,
                        download_url: str = None, update_action: str = None,
                        download_size_bytes: int = 0, download_duration_ms: int = 0,
                        error_message: str = None):
        """Log del controllo e download degli aggiornamenti."""
        data = self._get_base_data()
        data['update_check_result'] = {
            'check_performed': check_performed,
            'update_available': update_available,
            'current_version': current_version or self.version,
            'latest_version': latest_version or self.version,
            'download_url': download_url
        }
        data['update_action'] = update_action
        data['update_details'] = {
            'download_size_bytes': download_size_bytes,
            'download_duration_ms': download_duration_ms,
            'error_message': error_message
        }
        
        print(f"[LOGGER] Sending update check log...")
        self._make_request('update-check', data)
    
    def log_error(self, error_type: str, error_message: str, 
                 function_name: str = None, meet_window_title: str = None,
                 stack_trace: str = None):
        """Log degli errori dell'applicazione."""
        data = self._get_base_data()
        data['error_type'] = error_type
        data['error_message'] = error_message
        data['error_context'] = {
            'function_name': function_name,
            'meet_window_title': meet_window_title,
            'system_info': {
                'computer_name': self.computer_name,
                'os_version': self.os_version
            }
        }
        data['stack_trace'] = stack_trace
        
        print(f"[LOGGER] Sending error log...")
        self._make_request('error', data)
    
    def log_heartbeat(self, status: str = "monitoring", meet_windows_detected: int = 0,
                     last_action_timestamp: str = None):
        """Log di heartbeat per confermare che l'applicazione è attiva."""
        data = self._get_base_data()
        data['uptime_seconds'] = int(time.time() - self.start_time)
        data['status'] = status
        data['meet_windows_detected'] = meet_windows_detected
        data['last_action_timestamp'] = last_action_timestamp
        
        print(f"[LOGGER] Sending heartbeat log...")
        self._make_request('heartbeat', data)

# Configurazione globale del logger
LOGGING_CONFIG = {
    'api_url': 'https://uat.unitretradate.it',  # Da configurare
    'api_key': 'iuhji876ytghju7678ijhgb',        # Da configurare
    'version': '1.0.13'                     # Da aggiornare ad ogni release
}

# Istanza globale del logger
logger = None

def initialize_logger():
    """Inizializza il logger globale."""
    global logger
    if logger is None:
        logger = AutoScreenShareLogger(
            api_url=LOGGING_CONFIG['api_url'],
            api_key=LOGGING_CONFIG['api_key'],
            version=LOGGING_CONFIG['version']
        )
    return logger

def get_logger() -> AutoScreenShareLogger:
    """Restituisce l'istanza del logger globale."""
    if logger is None:
        return initialize_logger()
    return logger







