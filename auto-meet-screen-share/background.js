const LOGGING_CONFIG = {
    apiUrl: 'https://www.unitretradate.it',
    apiKey: 'iuhji876ytghju7678ijhgb'
};

async function sendLogFromBackground(endpoint, data) {
    const url = `${LOGGING_CONFIG.apiUrl}/api/logs/${endpoint}`;
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${LOGGING_CONFIG.apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        return { ok: response.ok, status: response.status };
    } catch (error) {
        return { ok: false, status: 0, error: String(error) };
    }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message && message.type === 'SEND_LOG') {
        sendLogFromBackground(message.endpoint, message.data)
            .then(result => sendResponse(result));
        return true; // keep channel open for async response
    }
});


