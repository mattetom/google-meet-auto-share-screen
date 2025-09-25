// Configurazione del logger
const LOGGING_CONFIG = {
    apiUrl: 'https://www.unitretradate.it', // Da configurare
    apiKey: 'iuhji876ytghju7678ijhgb',       // Da configurare
    version: '1.0.5'                   // Da aggiornare ad ogni release
};

// Funzione per inviare log al server tramite background (bypassa CORS della pagina)
async function sendLog(endpoint, data) {
    return new Promise((resolve) => {
        chrome.runtime.sendMessage({
            type: 'SEND_LOG',
            endpoint,
            data
        }, (response) => {
            if (chrome.runtime.lastError) {
                console.warn(`[LOGGER] Error sending log to ${endpoint}:`, chrome.runtime.lastError.message);
                resolve(false);
                return;
            }
            if (response && response.ok) {
                console.log(`[LOGGER] Log sent successfully to ${endpoint}`);
                resolve(true);
            } else {
                const status = response ? response.status : 'no-response';
                console.warn(`[LOGGER] Failed to send log to ${endpoint}: ${status}`);
                resolve(false);
            }
        });
    });
}

// Funzione per ottenere i dati base per tutti i log
function getBaseLogData() {
    return {
        timestamp: new Date().toISOString(),
        application_type: 'chrome_extension',
        version: LOGGING_CONFIG.version,
        system_info: {
            user_agent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language
        }
    };
}

// Funzione per attendere e cliccare sul pulsante "Partecipa ora"
function autoJoinMeeting() {
    console.log("[INFO] Tentativo di partecipare alla riunione...");
    
    const startTime = Date.now();
    let attempts = 0;
    let interval = setInterval(() => {
        let joinButton = document.querySelector("[aria-label='Partecipa ora'], [aria-label='Join now']");
        
        if (!joinButton) {
            // Fallback: cerca un pulsante con testo "Partecipa" o "Join"
            joinButton = Array.from(document.querySelectorAll("button"))
                .find(btn => btn.innerText.includes("Partecipa") || btn.innerText.includes("Join"));

            attempts++;
        }

        if (joinButton) {
            joinButton.click();
            console.log("[SUCCESS] Cliccato su 'Partecipa ora'.");
            
            // Log dell'azione di join
            const duration = Date.now() - startTime;
            sendLog('screen-share', {
                ...getBaseLogData(),
                action_type: 'join_meeting',
                action_result: 'success',
                meet_window_title: document.title,
                action_details: {
                    attempts_made: attempts,
                    duration_ms: duration,
                    error_message: null
                }
            });

            clearInterval(interval); // Ferma il controllo continuo
            setTimeout(autoClickPresentNow, 1000); // Attendi 1 secondo e avvia la presentazione
        } else if (attempts > 20) { // Dopo 10 secondi, se non lo trova, smette di cercare
            console.log("[WARNING] Pulsante 'Partecipa ora' non trovato dopo vari tentativi.");
            
            // Log dell'errore
            const duration = Date.now() - startTime;
            sendLog('screen-share', {
                ...getBaseLogData(),
                action_type: 'join_meeting',
                action_result: 'failed',
                meet_window_title: document.title,
                action_details: {
                    attempts_made: attempts,
                    duration_ms: duration,
                    error_message: 'Join button not found after multiple attempts'
                }
            });
            
            clearInterval(interval);
        }
    }, 500); // Controlla ogni 500ms
}

// Funzione per attendere e cliccare sul pulsante "Present now"
function autoClickPresentNow() {
    console.log("[INFO] Tentativo di avviare la condivisione dello schermo...");

    const startTime = Date.now();
    let attempts = 0;
    let interval = setInterval(() => {
        let presentButton = document.querySelector("[aria-label='Present now'], [aria-label='Presenta ora'], [aria-label='Share screen']");
        if (presentButton) {
            presentButton.click();
            console.log("[SUCCESS] Cliccato su 'Present now'.");
            
            // Log dell'azione di present
            const duration = Date.now() - startTime;
            sendLog('screen-share', {
                ...getBaseLogData(),
                action_type: 'present_now',
                action_result: 'success',
                meet_window_title: document.title,
                action_details: {
                    attempts_made: attempts,
                    duration_ms: duration,
                    error_message: null
                }
            });

            clearInterval(interval); // Ferma il controllo continuo
            setTimeout(() => {
                console.log("[INFO] Popup di condivisione dovrebbe essere aperto ora.");
            }, 10000); // Aspetta 10 secondi per permettere l'apertura del popup di condivisione
        } else {
            attempts++;
            if (attempts > 20) { // Dopo 10 secondi, se non lo trova, smette di cercare
                console.log("[WARNING] Pulsante 'Present now' non trovato dopo vari tentativi.");
                
                // Log dell'errore
                const duration = Date.now() - startTime;
                sendLog('screen-share', {
                    ...getBaseLogData(),
                    action_type: 'present_now',
                    action_result: 'failed',
                    meet_window_title: document.title,
                    action_details: {
                        attempts_made: attempts,
                        duration_ms: duration,
                        error_message: 'Present button not found after multiple attempts'
                    }
                });
                
                clearInterval(interval);
            }
        }
    }, 500); // Controlla ogni 500ms
}

// Avvia il processo dopo il caricamento della pagina
window.addEventListener("load", () => {
    console.log("[INFO] Google Meet caricato, attivazione auto-join...");
    
    // Log dell'avvio dell'estensione
    sendLog('startup', {
        ...getBaseLogData(),
        update_info: {
            update_check_performed: false,
            update_available: false,
            current_version: LOGGING_CONFIG.version,
            latest_version: LOGGING_CONFIG.version
        }
    });
    
    setTimeout(autoJoinMeeting, 1000); // Aspetta 1 secondo prima di cercare il pulsante di join
});

// Log di heartbeat ogni 5 minuti
setInterval(() => {
    sendLog('heartbeat', {
        ...getBaseLogData(),
        uptime_seconds: Math.floor((Date.now() - performance.timing.navigationStart) / 1000),
        status: 'monitoring',
        meet_windows_detected: 1, // Assumiamo che se l'estensione è attiva, c'è una finestra Meet
        last_action_timestamp: new Date().toISOString()
    });
}, 300000); // 5 minuti
