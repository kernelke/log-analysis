const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')

const { dialog } = require('electron')

ipcMain.handle('open-file-dialog', async () => {
  const { filePaths } = await dialog.showOpenDialog({
    properties: ['openFile']
  })
  return filePaths[0]
})

let mainWindow

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: false // 允许跨域请求
    }
  })

  // 加载本地开发服务器或打包后的文件
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(
      path.resolve(__dirname, '../dist/index.html').replace(/\\/g, '/')
    )
  }
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})