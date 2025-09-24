# Configurazione del Sistema di Logging (Client)

## Panoramica

Questo documento descrive come configurare l'invio dei log dalle applicazioni client di Auto Screen Share verso un server di logging esterno (gestito altrove). Qui configuri solo i client.

## Configurazione Python Desktop App

### File: `auto-python-screen-share/logger.py`

Modifica le seguenti variabili nella sezione `LOGGING_CONFIG`:

```python
LOGGING_CONFIG = {
    'api_url': 'https://your-domain.com',  # URL del tuo server di logging
    'api_key': 'your-api-key-here',        # Chiave API per l'autenticazione
    'version': '1.0.5'                     # Versione dell'applicazione
}
```

### Variabili da Configurare:

1. **`api_url`**: L'URL base del tuo server di logging (es. `https://logs.yourdomain.com`)
2. **`api_key`**: La chiave API per l'autenticazione con il server
3. **`version`**: La versione corrente dell'applicazione (da aggiornare ad ogni release)

## Configurazione Chrome Extension

### File: `auto-meet-screen-share/meetContent.js`

Modifica le seguenti variabili nella sezione `LOGGING_CONFIG`:

```javascript
const LOGGING_CONFIG = {
    apiUrl: 'https://your-domain.com', // URL del tuo server di logging
    apiKey: 'your-api-key-here',       // Chiave API per l'autenticazione
    version: '1.0.5'                   // Versione dell'estensione
};
```

### File: `auto-meet-screen-share/manifest.json`

Aggiorna il campo `host_permissions` per includere il dominio del tuo server:

```json
{
  "host_permissions": [
    "*://meet.google.com/*",
    "https://your-domain.com/*"
  ]
}
```

## Policy e Note

- Usa sempre HTTPS.
- Non includere dati sensibili nei payload.
- Implementa retry con backoff esponenziale in caso di errori di rete.
- Se il server è irraggiungibile, l'app deve continuare a funzionare (best-effort logging).

Per dettagli su payload ed endpoint supportati, vedi `LOGGING_API_DOCUMENTATION.md`.








