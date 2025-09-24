# Sistema di Logging - Auto Screen Share

## Panoramica

Il sistema di logging per Auto Screen Share consente di monitorare e tracciare le operazioni importanti dell'applicazione (desktop Python ed estensione Chrome) inviando eventi a un server di logging esterno. Questo repository contiene solo i client: non include il codice del server.

## Caratteristiche

- **Logging completo**: Traccia avvio, rilevamento finestre, azioni di screen sharing, aggiornamenti ed errori
- **Heartbeat**: Monitoraggio continuo dello stato delle applicazioni
- **Retry automatico**: Gestione robusta degli errori di rete
- **Sicurezza**: Autenticazione tramite API key e rate limiting
- **Scalabilità**: Database PostgreSQL con indici ottimizzati

## Struttura del Progetto

```
├── LOGGING_API_DOCUMENTATION.md    # Specifica API che il server esterno espone
├── LOGGING_CONFIGURATION.md        # Guida alla configurazione lato client
└── LOGGING_README.md               # Questo file
```

## Quick Start

Prerequisiti:
- Un endpoint HTTPS del server di logging esterno (base URL) e una API key fornite dal team server.

### 1. Configurazione dell'Applicazione Python

Modifica `auto-python-screen-share/logger.py`:

```python
LOGGING_CONFIG = {
    'api_url': 'https://your-domain.com',
    'api_key': 'your-api-key-here',
    'version': '1.0.5'
}
```

### 2. Configurazione dell'Estensione Chrome

Modifica `auto-meet-screen-share/meetContent.js`:

```javascript
const LOGGING_CONFIG = {
    apiUrl: 'https://your-domain.com',
    apiKey: 'your-api-key-here',
    version: '1.0.5'
};
```

E aggiorna `auto-meet-screen-share/manifest.json`:

```json
{
  "host_permissions": [
    "*://meet.google.com/*",
    "https://your-domain.com/*"
  ]
}
```

## Tipi di Log inviati

### 1. Startup Log
- **Quando**: All'avvio dell'applicazione
- **Dati**: Versione, info sistema, stato aggiornamenti
- **Frequenza**: Una volta per avvio

### 2. Window Detection Log
- **Quando**: Durante la ricerca di finestre Meet
- **Dati**: Risultato ricerca, numero finestre, durata
- **Frequenza**: Continuamente durante il monitoraggio

### 3. Screen Share Action Log
- **Quando**: Durante le azioni di screen sharing
- **Dati**: Tipo azione, risultato, durata, errori
- **Frequenza**: Per ogni azione di condivisione

### 4. Update Check Log
- **Quando**: Durante il controllo e download aggiornamenti
- **Dati**: Versione corrente/latest, stato download, errori
- **Frequenza**: Ad ogni controllo aggiornamenti

### 5. Error Log
- **Quando**: In caso di errori o eccezioni
- **Dati**: Tipo errore, messaggio, stack trace, contesto
- **Frequenza**: Quando si verificano errori

### 6. Heartbeat Log
- **Quando**: Periodicamente per confermare che l'app è attiva
- **Dati**: Uptime, stato, finestre rilevate, ultima azione
- **Frequenza**: Ogni 5 minuti

## Monitoraggio e Alerting

Il monitoraggio, le dashboard e le query vengono gestiti dal server di logging esterno. Per dettagli su payload ed endpoint, vedere `LOGGING_API_DOCUMENTATION.md` e la documentazione del server.

## Sicurezza

### Best Practices lato client

1. **HTTPS Only**: usa sempre endpoint HTTPS del server
2. **API Key Management**: conserva l'API key in modo sicuro (no commit, no log)
3. **Rate Limiting consapevole**: rispetta i limiti comunicati dal server
4. **Input Validation locale**: sanitizza i campi prima dell'invio
5. **Log Sanitization**: non inviare dati sensibili

### Dati da Non Loggare

- Password o token di autenticazione
- Informazioni personali degli utenti
- Contenuto delle chiamate o chat
- Dati di navigazione sensibili

## Troubleshooting lato client

### Problemi Comuni

#### "Failed to send log"
- Verifica connessione di rete e DNS
- Controlla URL/base path forniti dal server
- Verifica che l'endpoint sia raggiungibile (HTTPS) e non bloccato da firewall

#### "Authentication failed"
- Verifica API key e formato header Authorization
- Controlla che l'API key sia aggiornata e attiva

#### "Rate limited"
- Riduci frequenza dei log ed implementa backoff esponenziale
- Coordina con il team server per eventuali limiti diversi

#### "Server error"
- Ritenta con backoff; se persiste, contatta il team server

### Debug

Per abilitare il debug nelle applicazioni:

**Python:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Chrome Extension:**
```javascript
console.log('[DEBUG] Sending log:', data);
```

## Deployment lato client

Checklist:
- [ ] Base URL del server configurato nelle app client
- [ ] API key impostata in `logger.py` e `meetContent.js`
- [ ] Versioni aggiornate
- [ ] `host_permissions` aggiornati nel `manifest.json`

Rollback:
1. Disabilita temporaneamente l'invio dei log (feature flag/config)
2. Ripristina una versione precedente senza logging se necessario
3. Contatta il team server per incidenti lato server

## Manutenzione lato client

- Ruota periodicamente le API key secondo le policy del server
- Aggiorna la versione applicativa riportata nei log ad ogni release
- Monitora i fallback: i client devono continuare a funzionare anche se il logging fallisce

## Supporto

Per problemi lato client:
1. Verifica la configurazione locale
2. Consulta `LOGGING_API_DOCUMENTATION.md` per i payload
3. Contatta il team che gestisce il server di logging per incidenti lato server

## Changelog

### v1.0.0
- Implementazione iniziale del sistema di logging lato client (Python + Chrome)








