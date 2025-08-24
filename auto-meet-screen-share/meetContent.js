// Funzione per attendere e cliccare sul pulsante "Partecipa ora"
function autoJoinMeeting() {
    console.log("[INFO] Tentativo di partecipare alla riunione...");

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

            clearInterval(interval); // Ferma il controllo continuo
            setTimeout(autoClickPresentNow, 1000); // Attendi 5 secondi e avvia la presentazione
        } else if (attempts > 20) { // Dopo 10 secondi, se non lo trova, smette di cercare
            console.log("[WARNING] Pulsante 'Partecipa ora' non trovato dopo vari tentativi.");
            clearInterval(interval);
        }
    }, 500); // Controlla ogni 500ms
}

// Funzione per attendere e cliccare sul pulsante "Present now"
function autoClickPresentNow() {
    console.log("[INFO] Tentativo di avviare la condivisione dello schermo...");

    let attempts = 0;
    let interval = setInterval(() => {
        let presentButton = document.querySelector("[aria-label='Present now'], [aria-label='Presenta ora'], [aria-label='Share screen']");
        if (presentButton) {
            presentButton.click();
            console.log("[SUCCESS] Cliccato su 'Present now'.");

            clearInterval(interval); // Ferma il controllo continuo
            setTimeout(() => {
                console.log("[INFO] Popup di condivisione dovrebbe essere aperto ora.");
            }, 10000); // Aspetta 10 secondi per permettere l'apertura del popup di condivisione
        } else {
            attempts++;
            if (attempts > 20) { // Dopo 10 secondi, se non lo trova, smette di cercare
                console.log("[WARNING] Pulsante 'Present now' non trovato dopo vari tentativi.");
                clearInterval(interval);
            }
        }
    }, 500); // Controlla ogni 500ms
}

// Avvia il processo dopo il caricamento della pagina
window.addEventListener("load", () => {
    console.log("[INFO] Google Meet caricato, attivazione auto-join...");
    
    setTimeout(autoJoinMeeting, 1000); // Aspetta 1 secondo prima di cercare il pulsante di join
});
