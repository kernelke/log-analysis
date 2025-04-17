console.log('[Preload] 环境变量:', process.env.VITE_API_URL)
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
  openFileDialog: () => ipcRenderer.invoke('open-file-dialog')
})