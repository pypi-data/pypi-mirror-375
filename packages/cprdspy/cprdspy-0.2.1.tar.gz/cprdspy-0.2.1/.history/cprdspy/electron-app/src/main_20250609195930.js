const { app, BrowserWindow, ipcMain, Tray, Menu, shell, dialog } = require('electron');
const path = require('path');
const url = require('url');
const { spawn } = require('child_process');
const isDev = require('electron-is-dev');
const findProcess = require('find-process');
const fs = require('fs');
const log = require('electron-log');
const Store = require('electron-store');

// 配置日志
log.transports.file.level = 'info';
log.info('应用启动');

// 存储设置
const store = new Store();

// 全局变量
let mainWindow;
let tray;
let pythonProcess = null;
let serverUrl = 'http://localhost:8050';
let isQuitting = false;

// 获取Python可执行文件路径
function getPythonPath() {
    if (isDev) {
        return 'python'; // 开发模式使用系统Python
    } else {
        // 生产模式使用打包的Python
        return path.join(process.resourcesPath, 'python', 'python.exe');
    }
}

// 获取Python脚本路径
function getScriptPath() {
    if (isDev) {
        return path.join(__dirname, '..', '..', 'CPR_Dashborad', 'app_waves.py');
    } else {
        return path.join(process.resourcesPath, 'python', 'app_waves.py');
    }
}

// 启动Python服务器
function startPythonServer() {
    return new Promise((resolve, reject) => {
        const pythonPath = getPythonPath();
        const scriptPath = getScriptPath();

        log.info(`启动Python服务器: ${pythonPath} ${scriptPath}`);

        // 检查文件是否存在
        if (!isDev && !fs.existsSync(scriptPath)) {
            log.error(`Python脚本不存在: ${scriptPath}`);
            dialog.showErrorBox('启动错误', `找不到Python脚本: ${scriptPath}`);
            reject(new Error(`找不到Python脚本: ${scriptPath}`));
            return;
        }

        // 启动Python进程
        pythonProcess = spawn(pythonPath, [scriptPath]);

        // 处理Python输出
        pythonProcess.stdout.on('data', (data) => {
            const output = data.toString();
            log.info(`Python输出: ${output}`);

            // 检查服务器是否已启动
            if (output.includes('Dash is running on')) {
                const match = output.match(/http:\/\/[0-9.:]+/);
                if (match) {
                    serverUrl = match[0];
                    log.info(`服务器URL: ${serverUrl}`);
                }
                resolve();
            }
        });

        pythonProcess.stderr.on('data', (data) => {
            log.error(`Python错误: ${data}`);
        });

        pythonProcess.on('error', (error) => {
            log.error(`启动Python进程失败: ${error.message}`);
            dialog.showErrorBox('启动错误', `启动Python进程失败: ${error.message}`);
            reject(error);
        });

        // 设置超时
        setTimeout(() => {
            if (pythonProcess) {
                resolve(); // 即使没有看到明确的启动消息，也假设服务器已启动
            }
        }, 5000);
    });
}

// 创建主窗口
function createWindow() {
    // 从存储中获取窗口大小和位置
    const windowConfig = store.get('windowConfig', {
        width: 1200,
        height: 800,
        x: undefined,
        y: undefined,
        maximized: false
    });

    mainWindow = new BrowserWindow({
        width: windowConfig.width,
        height: windowConfig.height,
        x: windowConfig.x,
        y: windowConfig.y,
        minWidth: 800,
        minHeight: 600,
        frame: false, // 无框架窗口，用于自定义标题栏
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'assets', 'icon.png')
    });

    // 如果之前是最大化状态，则最大化窗口
    if (windowConfig.maximized) {
        mainWindow.maximize();
    }

    // 加载应用
    mainWindow.loadURL(url.format({
        pathname: path.join(__dirname, 'index.html'),
        protocol: 'file:',
        slashes: true
    }));

    // 打开开发者工具（仅在开发模式）
    if (isDev) {
        mainWindow.webContents.openDevTools();
    }

    // 窗口关闭事件
    mainWindow.on('close', (event) => {
        if (!isQuitting) {
            event.preventDefault();
            mainWindow.hide();
            return false;
        }

        // 保存窗口配置
        const isMaximized = mainWindow.isMaximized();
        const bounds = mainWindow.getBounds();

        store.set('windowConfig', {
            width: bounds.width,
            height: bounds.height,
            x: bounds.x,
            y: bounds.y,
            maximized: isMaximized
        });
    });

    // 窗口关闭后清除引用
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // 创建系统托盘
    createTray();
}

// 创建系统托盘
function createTray() {
    tray = new Tray(path.join(__dirname, 'assets', 'tray-icon.png'));

    const contextMenu = Menu.buildFromTemplate([
        {
            label: '显示应用',
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                }
            }
        },
        { type: 'separator' },
        {
            label: '退出',
            click: () => {
                isQuitting = true;
                app.quit();
            }
        }
    ]);

    tray.setToolTip('CPR波形可视化');
    tray.setContextMenu(contextMenu);

    tray.on('click', () => {
        if (mainWindow) {
            if (mainWindow.isVisible()) {
                mainWindow.hide();
            } else {
                mainWindow.show();
            }
        }
    });
}

// 清理Python进程
function cleanupPythonProcess() {
    return new Promise((resolve) => {
        if (pythonProcess) {
            log.info('正在终止Python进程...');

            // 在Windows上，我们需要终止整个进程树
            if (process.platform === 'win32') {
                spawn('taskkill', ['/pid', pythonProcess.pid, '/f', '/t']);
            } else {
                pythonProcess.kill();
            }

            pythonProcess = null;
        }

        // 查找可能残留的Python进程
        findProcess('port', 8050)
            .then((list) => {
                if (list.length > 0) {
                    log.info(`发现在端口8050上运行的进程: ${JSON.stringify(list)}`);

                    list.forEach((proc) => {
                        log.info(`正在终止进程 ${proc.pid}`);
                        if (process.platform === 'win32') {
                            spawn('taskkill', ['/pid', proc.pid, '/f']);
                        } else {
                            process.kill(proc.pid);
                        }
                    });
                }
                resolve();
            })
            .catch((err) => {
                log.error(`查找进程时出错: ${err}`);
                resolve();
            });
    });
}

// 应用准备就绪
app.whenReady().then(() => {
    // 创建必要的目录
    if (!isDev) {
        const assetsDir = path.join(__dirname, 'assets');
        if (!fs.existsSync(assetsDir)) {
            fs.mkdirSync(assetsDir, { recursive: true });
        }
    }

    // 启动Python服务器
    startPythonServer()
        .then(() => {
            log.info('Python服务器已启动');
            createWindow();

            // 通知渲染进程服务器已启动
            if (mainWindow) {
                mainWindow.webContents.on('did-finish-load', () => {
                    mainWindow.webContents.send('server-status', {
                        status: 'running',
                        url: serverUrl
                    });
                });
            }
        })
        .catch((error) => {
            log.error(`启动Python服务器失败: ${error}`);
            dialog.showErrorBox('启动错误', `无法启动Python服务器: ${error.message}`);
            app.quit();
        });

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        } else if (mainWindow) {
            mainWindow.show();
        }
    });
});

// 所有窗口关闭时退出应用（macOS除外）
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// 应用退出前清理
app.on('before-quit', (event) => {
    isQuitting = true;

    // 如果正在清理，阻止退出
    if (pythonProcess) {
        event.preventDefault();

        cleanupPythonProcess()
            .then(() => {
                log.info('清理完成，正在退出应用');
                app.quit();
            })
            .catch((error) => {
                log.error(`清理时出错: ${error}`);
                app.quit();
            });
    }
});

// IPC事件处理
ipcMain.on('window-control', (event, action) => {
    if (!mainWindow) return;

    switch (action) {
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
            mainWindow.hide();
            break;
        case 'quit':
            isQuitting = true;
            app.quit();
            break;
    }
});

// 打开外部链接
ipcMain.on('open-external', (event, url) => {
    shell.openExternal(url);
});