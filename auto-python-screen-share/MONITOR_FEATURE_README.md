# Funzionalità Spostamento Finestra nel Secondo Monitor

## Panoramica

Questa versione dell'applicazione Auto Screen Share include una nuova funzionalità che sposta automaticamente la finestra di Google Meet nel secondo monitor (se disponibile) prima di avviare la condivisione dello schermo.

## Funzionalità Aggiunte

### 1. Rilevamento Monitor Multipli
- **Funzione**: `get_available_monitors()`
- **Descrizione**: Rileva automaticamente tutti i monitor collegati al sistema usando le API di Windows
- **Supporto**: Windows con configurazioni multi-monitor
- **Indipendenza**: Funziona indipendentemente dalle finestre aperte (non dipende dalla posizione delle finestre)
- **Fallback**: Se le API Windows non sono disponibili, utilizza tkinter come fallback

### 2. Spostamento Automatico Finestre
- **Funzione**: `move_window_to_second_monitor(window_title)`
- **Descrizione**: Sposta la finestra specificata nel secondo monitor usando le API native di Windows
- **Tecnologia**: Usa pywin32 con SetWindowPos e InvalidateRect per preservare la struttura
- **Posizionamento**: Posiziona la finestra nel secondo monitor (50px dal bordo)
- **Validazione**: Verifica che la finestra non vada fuori dai limiti del monitor
- **Risoluzione Problemi**: Include refresh automatico per risolvere il problema della finestra bianca

### 3. Integrazione nel Flusso Principale
- **Timing**: Lo spostamento avviene dopo l'attivazione della finestra Meet e prima della condivisione
- **Logging**: Tutte le operazioni sono registrate nel sistema di logging
- **Gestione Errori**: Se lo spostamento fallisce, l'applicazione continua con la condivisione normale

## Come Funziona

1. **Rilevamento**: L'applicazione rileva automaticamente i monitor disponibili
2. **Attivazione**: Quando trova una finestra Meet, la attiva come prima
3. **Spostamento**: Se è disponibile un secondo monitor, sposta la finestra Meet usando le API native di Windows
4. **Condivisione**: Procede con la condivisione dello schermo come al solito

## Configurazione Richiesta

### Monitor Multipli
- **Minimo**: 2 monitor collegati al PC
- **Configurazione**: I monitor devono essere configurati in Windows
- **Posizione**: Il secondo monitor è tipicamente posizionato a destra del primo

### Dipendenze
- `pywin32`: Per le API native di Windows (nuovo)
- `tkinter`: Per il rilevamento dei monitor (incluso in Python)
- `pygetwindow`: Per la gestione delle finestre (già presente)
- `pywinctl`: Per l'attivazione delle finestre (già presente)

## Test della Funzionalità

È disponibile uno script di test per verificare la funzionalità:

```bash
python test_monitor_detection.py
```

Lo script testa:
- Rilevamento dei monitor disponibili
- Spostamento di una finestra di test nel secondo monitor

## Logging

Tutte le operazioni di spostamento finestra sono registrate con:
- Tipo di azione
- Risultato dell'operazione
- Numero di monitor rilevati
- Posizione finale della finestra
- Tempo di esecuzione
- Eventuali errori

## Gestione degli Errori

L'applicazione gestisce gracefully i seguenti scenari:
- **Monitor singolo**: Continua normalmente senza spostamento
- **Finestra non trovata**: Logga l'errore e continua
- **Errore di spostamento**: Prova il metodo alternativo, poi continua con la condivisione
- **Errore di rilevamento monitor**: Utilizza il monitor principale come fallback
- **Finestra bianca**: Applica refresh automatico per ripristinare il rendering

## Risoluzione Problemi

### Problema: Finestra Bianca Dopo Spostamento
**Sintomi**: La finestra Meet appare completamente bianca senza barre del browser
**Causa**: Il browser perde il rendering quando viene spostato programmaticamente
**Soluzione**: L'applicazione applica automaticamente:
1. Click nella finestra per attivarla
2. Refresh con F5 o Ctrl+R
3. Attivazione della finestra per forzare il rendering

### Problema: Spostamento Fallisce
**Sintomi**: La finestra non si sposta nel secondo monitor
**Soluzione**: L'applicazione usa le API native di Windows (pywin32) per lo spostamento. Se fallisce, continua con la condivisione normale.

### Problema: Finestra Perde Struttura
**Sintomi**: La finestra diventa completamente bianca senza bottoni
**Causa**: Spostamento che corrompe il rendering
**Soluzione**: Il metodo pywin32 usa SetWindowPos e InvalidateRect per preservare la struttura della finestra e forzare il refresh del rendering

## Compatibilità

- **Sistema Operativo**: Windows 10/11
- **Python**: 3.7+
- **Configurazioni**: Monitor estesi, duplicati, o configurazioni personalizzate

## Note Tecniche

- Il rilevamento dei monitor utilizza le **API di Windows** (`EnumDisplayMonitors`, `GetMonitorInfoW`) per un rilevamento accurato
- **Fallback robusto**: Se le API Windows non sono disponibili, utilizza `tkinter` come alternativa
- Lo spostamento delle finestre utilizza `pygetwindow.moveTo()`
- La posizione è calcolata per centrare la finestra nel secondo monitor
- I limiti del monitor sono rispettati per evitare finestre fuori schermo
- **Indipendente dalle finestre**: Il rilevamento funziona anche se Meet è l'unica finestra aperta nel primo monitor

## Versioning

- **Versione**: 1.0.14
- **Data**: Aggiunta funzionalità spostamento finestra nel secondo monitor
- **Compatibilità**: Retrocompatibile con versioni precedenti
