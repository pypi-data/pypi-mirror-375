const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;
let pythonProcess;
const PYTHON_SERVER_PORT = 8050;  // Dash默认端口

function createWindow() {
    // 创建浏览器窗口
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        frame: false,  // 无边框窗口
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'assets', 'icon.png')
    });

    // 加载应用
    if (isDev) {
        mainWindow.loadFile(path.join(__dirname, 'index.html'));
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, 'index.html'));
    }

    // 启动Python服务器
    startPythonServer();

    // 窗口控制
    ipcMain.on('window-control', (event, command) => {
        switch (command) {
            case 'minimize':
                mainWindow.minimize();
                break;
            case 'maximize':
                if (mainWindow.isMaximized()) {
                    mainWindow.unmaximize();
                } else {
                    mainWindow.maximize();
                }
                break;
            case 'close':
                mainWindow.close();
                break;
            case 'quit':
                app.quit();
                break;
        }
    });

    // 处理外部链接
    ipcMain.on('open-external', (event, url) => {
        shell.openExternal(url);
    });
}

function startPythonServer() {
    const pythonPath = isDev
        ? 'python'  // 开发环境使用系统Python
        : path.join(process.resourcesPath, 'python', 'python.exe');  // 生产环境使用打包的Python

    const scriptPath = path.join(
        isDev ? process.cwd() : process.resourcesPath,
        'python',
        'app.py'
    );

    pythonProcess = spawn(pythonPath, [scriptPath], {
        stdio: ['ignore', 'pipe', 'pipe']
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`[Python] ${data}`);
        if (data.toString().includes('Dash is running on')) {
            mainWindow.webContents.send('server-status', 'running');
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`[Python Error] ${data}`);
        mainWindow.webContents.send('server-status', 'error');
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python进程退出，退出码 ${code}`);
        mainWindow.webContents.send('server-status', 'stopped');
    });
}

// 应用程序生命周期
app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    if (pythonProcess) {
        pythonProcess.kill();
    }
});

// 开发环境下的热重载
if (isDev) {
    try {
        require('electron-reloader')(module, {
            debug: true,
            watchRenderer: true
        });
    } catch (_) { console.log('Error'); }
}