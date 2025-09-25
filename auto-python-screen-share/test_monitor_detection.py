#!/usr/bin/env python3
"""
Script di test per verificare la funzionalità di rilevamento monitor e spostamento finestre.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auto_screen_share import get_available_monitors, move_window_to_second_monitor
from logger import initialize_logger

def test_monitor_detection():
    """Testa il rilevamento dei monitor."""
    print("=== Test Rilevamento Monitor ===")
    
    # Inizializza il logger
    logger = initialize_logger()
    
    try:
        monitors = get_available_monitors()
        
        print(f"Monitor rilevati: {len(monitors)}")
        for i, monitor in enumerate(monitors):
            print(f"Monitor {i}:")
            print(f"  - ID: {monitor['id']}")
            print(f"  - Posizione: ({monitor['x']}, {monitor['y']})")
            print(f"  - Dimensioni: {monitor['width']}x{monitor['height']}")
            print(f"  - Principale: {monitor['is_primary']}")
            print()
        
        if len(monitors) >= 2:
            print("✅ Secondo monitor rilevato!")
            print("📝 Nota: Il rilevamento usa le API di Windows e funziona anche se")
            print("   Meet è l'unica finestra aperta nel primo monitor.")
            return True
        else:
            print("⚠️  Solo un monitor rilevato. Per testare lo spostamento finestre, connetti un secondo monitor.")
            print("📝 Nota: Il sistema di rilevamento è indipendente dalle finestre aperte.")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False

def test_window_move():
    """Testa lo spostamento di una finestra (se disponibile)."""
    print("\n=== Test Spostamento Finestra ===")
    
    # Cerca una finestra di test (es. Notepad, Calculator, etc.)
    import pygetwindow as gw
    
    test_windows = [
        "Notepad",
        "Calculator", 
        "Chrome",
        "Firefox",
        "Edge"
    ]
    
    test_window = None
    for window_name in test_windows:
        windows = gw.getWindowsWithTitle(window_name)
        if windows:
            test_window = windows[0]
            print(f"Finestra di test trovata: {test_window.title}")
            break
    
    if not test_window:
        print("⚠️  Nessuna finestra di test trovata. Apri Notepad o un'altra applicazione per testare.")
        return False
    
    try:
        # Mostra posizione attuale
        print(f"Posizione attuale: ({test_window.left}, {test_window.top})")
        
        # Prova a spostare la finestra con il metodo pywin32
        print("🔄 Test metodo pywin32 (API Windows native)...")
        success = move_window_to_second_monitor(test_window.title)
        
        if success:
            print("✅ Finestra spostata con successo!")
            print(f"Nuova posizione: ({test_window.left}, {test_window.top})")
            print("📝 Nota: Il metodo pywin32 dovrebbe preservare la struttura della finestra.")
        else:
            print("⚠️  Spostamento non riuscito o non necessario")
        
        return success
        
    except Exception as e:
        print(f"❌ Errore durante il test di spostamento: {e}")
        return False

def main():
    """Funzione principale di test."""
    print("🔍 Test Funzionalità Monitor e Spostamento Finestre")
    print("=" * 50)
    
    # Test rilevamento monitor
    monitor_test = test_monitor_detection()
    
    # Test spostamento finestra (solo se ci sono monitor multipli)
    if monitor_test:
        move_test = test_window_move()
    else:
        print("\n⏭️  Saltando il test di spostamento finestra (monitor singolo)")
        move_test = False
    
    # Risultati finali
    print("\n" + "=" * 50)
    print("📊 RISULTATI TEST:")
    print(f"  - Rilevamento Monitor: {'✅ PASS' if monitor_test else '❌ FAIL'}")
    print(f"  - Spostamento Finestra: {'✅ PASS' if move_test else '❌ FAIL'}")
    
    if monitor_test and move_test:
        print("\n🎉 Tutti i test sono passati! La funzionalità è pronta.")
        print("📝 La finestra Meet dovrebbe ora spostarsi correttamente usando le API native di Windows.")
        print("📝 Il metodo pywin32 dovrebbe preservare la struttura della finestra senza problemi di rendering.")
    elif monitor_test:
        print("\n⚠️  Monitor rilevati correttamente, ma spostamento finestra non testato.")
    else:
        print("\n❌ Alcuni test sono falliti. Controlla la configurazione dei monitor.")

if __name__ == "__main__":
    main()