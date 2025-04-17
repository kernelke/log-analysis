const
{app, BrowserWindow} = require('electron')
const
{spawn} = require('child_process')
const
path = require('path')

let
pythonProcess = null
let
mainWindow = null

function
createWindow()
{
    mainWindow = new
BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
        nodeIntegration: true,
        contextIsolation: false
    }
})

// 启动Python后端
pythonProcess = spawn(
    'python',
    [path.join(__dirname, 'backend/main.py')],
    {stdio: 'inherit'}
)

                // 加载前端页面
mainWindow.loadFile('frontend/dist/index.html')
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () = > {
if (pythonProcess)
pythonProcess.kill()
if (process.platform !== 'darwin')
app.quit()
})