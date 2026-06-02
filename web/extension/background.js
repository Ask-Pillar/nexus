// Nexus Web Ingest — background service worker

const NEXUS_URL = 'http://localhost:8765/ingest';

chrome.runtime.onMessage.addListener((msg, sender) => {
  if (msg.action === 'ingest') {
    fetch(NEXUS_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: msg.text, source: msg.source }),
    })
      .then(r => r.json())
      .then(data => console.log('Nexus ingested:', data))
      .catch(() => {});
  }
});
