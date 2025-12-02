const { app, BrowserWindow, session } = require('electron');
const path = require('path');

function configureCSP() {
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        // Permite carregar imagens de qualquer fonte (necessário para file://) e dados embutidos.
        'Content-Security-Policy': ["default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: file:;"]
      }
    });
  });
}

function createWindow() {
  // Cria a janela do navegador.
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,    
    transparent: true, // Deixa a janela transparente
    frame: false,      // Remove a barra de título e bordas
    alwaysOnTop: true, // Mantém a janela sempre na frente
    webPreferences: {
      // Anexa o script de preload à janela
      preload: path.join(__dirname, 'preload.js'),
      // É mais seguro manter nodeIntegration como false e usar o preload para expor APIs.
      nodeIntegration: false,
      contextIsolation: true,
    }
  });
  // Impede que o usuário clique através da janela transparente
  mainWindow.setIgnoreMouseEvents(true, { forward: true });

  // Carrega o index.html do aplicativo.
  mainWindow.loadFile('index.html');

  // Abre o DevTools (ferramentas de desenvolvedor).
  // mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
  configureCSP();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});