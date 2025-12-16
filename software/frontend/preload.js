const { contextBridge, shell, ipcRenderer } = require('electron');

const API_URL = 'http://127.0.0.1:8000';

async function fetchJSON(url, options = {}) {
    const res = await fetch(url, options);
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
    }
    return res.json();
}

contextBridge.exposeInMainWorld('electronAPI', {
    openExternal: (url) => ipcRenderer.send('open-external', url),
    backend: {
        async health() { return fetchJSON(`${API_URL}/health`); },
        async getClipboard() { return fetchJSON(`${API_URL}/clipboard/current`); },
        async getHistory(limit = 10) { return fetchJSON(`${API_URL}/clipboard/history?limit=${limit}`); },
        async deleteHistoryEntry(id) { return fetchJSON(`${API_URL}/clipboard/history/${id}`, { method: 'DELETE' }); },
        async clearHistory() { return fetchJSON(`${API_URL}/clipboard/history`, { method: 'DELETE' }); },
        async rotateKey() { return fetchJSON(`${API_URL}/admin/rotate-key`, { method: 'POST' }); },
        exitApp() { ipcRenderer.send('exit-app'); }
    }
});
