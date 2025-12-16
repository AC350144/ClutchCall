const { app, BrowserWindow, ipcMain, Tray, Menu, Notification, shell} = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const http = require('http');

let backendProcess = null;
let window;
let tray;
let isQuitting = false;

function createWindow() {
    window = new BrowserWindow({
        width: 550,
        height: 850,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true
        }
    });

    window.loadFile(path.join(__dirname, 'history.html'));
    window.setTitle('ClipVault - Secure Clipboard Manager');

    window.on('close', (event) => {
        if (!isQuitting) {
            event.preventDefault();
            window.hide();
        }
    });
}

function startBackend() {
    if (backendProcess) return;

    const isPackaged = app.isPackaged;
    const logPath = path.join(app.getPath('userData'), 'backend.log');

    const log = (msg) => {
        const line = `[${new Date().toISOString()}] ${msg}\n`;
        try { fs.appendFileSync(logPath, line); } catch {}
        console.log(msg);
    };

    if (isPackaged) {
        const backendExe = path.join(process.resourcesPath, 'backend.exe');
        backendProcess = spawn(backendExe, [], {
            windowsHide: true,
            env: { ...process.env, CLIPVAULT_DISABLE_CLIPBOARD: '0' }
        });
    } else {
        const pythonExe = path.join(__dirname, '..', '.venv', 'Scripts', 'python.exe');
        const mainPy = path.join(__dirname, '..', 'backend', 'main.py');

        log(`Starting backend: ${pythonExe} ${mainPy}`);

        backendProcess = spawn(pythonExe, [mainPy], {
            windowsHide: true,
            cwd: path.join(__dirname, '..', 'backend'),
            env: { ...process.env, CLIPVAULT_DISABLE_CLIPBOARD: '1' }
        });
    }

    backendProcess.stdout?.on('data', d => log(`[backend stdout] ${d}`));
    backendProcess.stderr?.on('data', d => log(`[backend stderr] ${d}`));

    backendProcess.on('exit', (code, signal) => {
        log(`Backend exited code=${code} signal=${signal}`);
        backendProcess = null;
    });
}

function stopBackend() {
    if (!backendProcess) return;

    try {
        exec(`taskkill /PID ${backendProcess.pid} /T /F`);
    } catch (e) {
        console.error('Failed to stop backend', e);
    }

    backendProcess = null;
}

function isBackendUp(timeoutMs = 1000) {
    return new Promise(resolve => {
        const req = http.request({
            host: '127.0.0.1',
            port: 8000,
            path: '/health',
            timeout: timeoutMs
        }, res => resolve(res.statusCode === 200));

        req.on('timeout', () => { req.destroy(); resolve(false); });
        req.on('error', () => resolve(false));
        req.end();
    });
}

let watcherInterval = null;
let lastClipboardContent = null;

function startClipboardWatcher() {
    if (watcherInterval) return;

    watcherInterval = setInterval(() => {
        const req = http.request({
            host: '127.0.0.1',
            port: 8000,
            path: '/clipboard/current',
            timeout: 1000
        }, res => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);

                    if (json.content && json.content !== lastClipboardContent) {
                        const oldContent = lastClipboardContent;
                        lastClipboardContent = json.content;

                        if (Notification.isSupported()) {
                            new Notification({
                                title: 'Clipboard Updated',
                                body: 'New clipboard entry captured',
                                silent: true
                            }).show();
                        }
                    }
                } catch (e) {
                    console.error('Clipboard watcher parse error', e);
                }
            });
        });

        req.on('error', (err) => {
            console.error('Clipboard watcher request error', err);
        });
        req.end();
    }, 1000);
}

ipcMain.on('exit-app', () => {
    isQuitting = true;
    stopBackend();
    app.quit();
});


ipcMain.on('open-external', (event, url) => {
    shell.openExternal(url).catch(err => {
        console.error('Failed to open URL externally:', err);
    });
});

app.whenReady().then(async () => {
    createWindow();

    tray = new Tray(path.join(__dirname, 'Logo.JPG'));
    tray.setContextMenu(Menu.buildFromTemplate([
        { label: 'Show App', click: () => window.show() },
        { label: 'Quit', click: () => {
            isQuitting = true;
            stopBackend();
            app.quit();
        }}
    ]));

    if (!(await isBackendUp(800))) {
        startBackend();
        for (let i = 0; i < 10; i++) {
            await new Promise(r => setTimeout(r, 400));
            if (await isBackendUp(600)) break;
        }
    }

    startClipboardWatcher();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    isQuitting = true;
    stopBackend();
    app.quit();
});