const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs-extra');
const { spawn } = require('child_process');
const log = require('electron-log');
const Store = require('electron-store');
const { autoUpdater } = require('electron-updater');

// 配置日志
log.transports.file.level = 'info';
log.transports.console.level = 'debug';
autoUpdater.logger = log;

// 开发模式下启用热重载
if (process.env.NODE_ENV === 'development') {
    try {
        require('electron-reloader')(module);
    } catch (_) { }
}

// 存储设置
const store = new Store({
    defaults: {
        serverPort: 8050,
        dataDir: path.join(app.getPath('documents'), 'CPRDspy', 'data'),
        startWithSystem: false,
        windowBounds: { width: 1200, height: 800 }
    }
});

// 全局变量
let mainWindow;
let pythonProcess = null;
let serverRunning = false;
let serverPort = store.get('serverPort');
let dataDir = store.get('dataDir');

// 确保数据目录存在
fs.ensureDirSync(dataDir);

// 创建主窗口
function createWindow() {
    const windowBounds = store.get('windowBounds');

    mainWindow = new BrowserWindow({
        width: windowBounds.width,
        height: windowBounds.height,
        minWidth: 800,
        minHeight: 600,
        frame: false, // 无边框窗口
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
            sandbox: false
        },
        icon: path.join(__dirname, 'assets', 'icon.png')
    });

    // 加载主页面
    mainWindow.loadFile(path.join(__dirname, 'index.html'));

    // 保存窗口大小和位置
    mainWindow.on('resize', () => {
        const { width, height } = mainWindow.getBounds();
        store.set('windowBounds', { width, height });
    });

    // 开发模式下打开开发者工具
    if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }

    // 启动Python服务器
    startPythonServer();
}

// 启动Python服务器
function startPythonServer() {
    // 获取Python可执行文件路径
    const pythonExecutable = getPythonExecutable();
    const scriptPath = path.join(process.resourcesPath, 'python', 'app.py');
    const devScriptPath = path.join(__dirname, '..', '..', 'CPR_Dashborad', 'app.py');

    // 根据环境选择脚本路径
    const finalScriptPath = process.env.NODE_ENV === 'development' ? devScriptPath : scriptPath;

    log.info(`启动Python服务器: ${pythonExecutable} ${finalScriptPath}`);
    log.info(`服务器端口: ${serverPort}`);
    log.info(`数据目录: ${dataDir}`);

    // 检查脚本是否存在
    if (!fs.existsSync(finalScriptPath)) {
        log.error(`Python脚本不存在: ${finalScriptPath}`);
        mainWindow.webContents.send('server-status', 'error');
        return;
    }

    // 启动Python进程
    pythonProcess = spawn(pythonExecutable, [finalScriptPath, '--port', serverPort, '--data-dir', dataDir]);

    // 监听标准输出
    pythonProcess.stdout.on('data', (data) => {
        const output = data.toString().trim();
        log.info(`Python stdout: ${output}`);

        // 检查服务器是否已启动
        if (output.includes('Dash is running on')) {
            serverRunning = true;
            mainWindow.webContents.send('server-status', 'running');
        }
    });

    // 监听标准错误
    pythonProcess.stderr.on('data', (data) => {
        const output = data.toString().trim();
        log.error(`Python stderr: ${output}`);
    });

    // 监听进程退出
    pythonProcess.on('close', (code) => {
        log.info(`Python进程退出，代码: ${code}`);
        serverRunning = false;
        mainWindow.webContents.send('server-status', 'stopped');
    });

    // 监听进程错误
    pythonProcess.on('error', (err) => {
        log.error(`Python进程错误: ${err.message}`);
        serverRunning = false;
        mainWindow.webContents.send('server-status', 'error');
    });
}

// 获取Python可执行文件路径
function getPythonExecutable() {
    if (process.env.NODE_ENV === 'development') {
        // 开发环境使用系统Python
        return process.platform === 'win32' ? 'python' : 'python3';
    } else {
        // 生产环境使用打包的Python
        const pythonDir = path.join(process.resourcesPath, 'python');
        return process.platform === 'win32'
            ? path.join(pythonDir, 'python.exe')
            : path.join(pythonDir, 'bin', 'python3');
    }
}

// 应用程序准备就绪时创建窗口
app.whenReady().then(() => {
    createWindow();

    // 检查更新
    if (process.env.NODE_ENV !== 'development') {
        autoUpdater.checkForUpdatesAndNotify();
    }

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

// 所有窗口关闭时退出应用
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// 应用退出前清理
app.on('before-quit', () => {
    // 关闭Python进程
    if (pythonProcess) {
        log.info('正在关闭Python进程...');
        if (process.platform === 'win32') {
            spawn('taskkill', ['/pid', pythonProcess.pid, '/f', '/t']);
        } else {
            pythonProcess.kill('SIGTERM');
        }
    }
});

// IPC通信处理
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
    }
});

// 获取应用版本
ipcMain.handle('get-app-version', () => {
    return app.getVersion();
});

// 获取内存使用情况
ipcMain.handle('get-memory-usage', () => {
    const memoryInfo = process.getProcessMemoryInfo();
    return memoryInfo.then(info => {
        // 转换为MB
        return info.private / 1024 / 1024;
    });
});

// 获取文件列表
ipcMain.handle('get-file-list', async () => {
    try {
        const files = await fs.readdir(dataDir);
        const fileList = await Promise.all(files.map(async (file) => {
            const filePath = path.join(dataDir, file);
            const stats = await fs.stat(filePath);

            return {
                name: file,
                path: filePath,
                size: stats.size,
                date: stats.mtime.getTime()
            };
        }));

        // 过滤出文件（不包括目录）
        return fileList.filter(file => !file.isDirectory);
    } catch (error) {
        log.error(`获取文件列表错误: ${error.message}`);
        throw error;
    }
});

// 导入文件
ipcMain.handle('import-file', async () => {
    try {
        const result = await dialog.showOpenDialog(mainWindow, {
            title: '选择数据文件',
            filters: [
                { name: 'CSV文件', extensions: ['csv'] },
                { name: '所有文件', extensions: ['*'] }
            ],
            properties: ['openFile', 'multiSelections']
        });

        if (result.canceled || result.filePaths.length === 0) {
            return { success: false, error: '未选择文件' };
        }

        // 复制文件到数据目录
        for (const filePath of result.filePaths) {
            const fileName = path.basename(filePath);
            const destPath = path.join(dataDir, fileName);
            await fs.copy(filePath, destPath);
        }

        return { success: true };
    } catch (error) {
        log.error(`导入文件错误: ${error.message}`);
        return { success: false, error: error.message };
    }
});

// 加载文件
ipcMain.handle('load-file', async (event, filePath) => {
    try {
        // 检查文件是否存在
        if (!await fs.pathExists(filePath)) {
            return { success: false, error: '文件不存在' };
        }

        // 通知Python服务器加载文件
        // 这里我们通过URL参数传递文件路径，实际处理在Dash应用中完成
        return { success: true };
    } catch (error) {
        log.error(`加载文件错误: ${error.message}`);
        return { success: false, error: error.message };
    }
});

// 删除文件
ipcMain.handle('delete-file', async (event, filePath) => {
    try {
        // 检查文件是否存在
        if (!await fs.pathExists(filePath)) {
            return { success: false, error: '文件不存在' };
        }

        // 检查文件是否在数据目录中
        if (!filePath.startsWith(dataDir)) {
            return { success: false, error: '无法删除数据目录外的文件' };
        }

        // 删除文件
        await fs.remove(filePath);
        return { success: true };
    } catch (error) {
        log.error(`删除文件错误: ${error.message}`);
        return { success: false, error: error.message };
    }
});

// 保存设置
ipcMain.handle('save-settings', async (event, settings) => {
    try {
        // 验证设置
        if (settings.serverPort < 1024 || settings.serverPort > 65535) {
            return { success: false, error: '端口号必须在1024-65535之间' };
        }

        // 保存设置
        store.set('serverPort', settings.serverPort);
        store.set('dataDir', settings.dataDir);
        store.set('startWithSystem', settings.startWithSystem);

        // 更新全局变量
        serverPort = settings.serverPort;
        dataDir = settings.dataDir;

        // 确保数据目录存在
        await fs.ensureDir(dataDir);

        // 设置开机启动
        app.setLoginItemSettings({
            openAtLogin: settings.startWithSystem
        });

        // 需要重启服务器
        if (serverRunning) {
            // 关闭当前服务器
            if (pythonProcess) {
                if (process.platform === 'win32') {
                    spawn('taskkill', ['/pid', pythonProcess.pid, '/f', '/t']);
                } else {
                    pythonProcess.kill('SIGTERM');
                }
                pythonProcess = null;
            }

            // 重新启动服务器
            setTimeout(() => {
                startPythonServer();
            }, 1000);
        }

        return { success: true };
    } catch (error) {
        log.error(`保存设置错误: ${error.message}`);
        return { success: false, error: error.message };
    }
});

// 重置设置
ipcMain.handle('reset-settings', async () => {
    try {
        // 重置为默认设置
        const defaultSettings = {
            serverPort: 8050,
            dataDir: path.join(app.getPath('documents'), 'CPRDspy', 'data'),
            startWithSystem: false
        };

        // 保存默认设置
        store.set('serverPort', defaultSettings.serverPort);
        store.set('dataDir', defaultSettings.dataDir);
        store.set('startWithSystem', defaultSettings.startWithSystem);

        // 更新全局变量
        serverPort = defaultSettings.serverPort;
        dataDir = defaultSettings.dataDir;

        // 确保数据目录存在
        await fs.ensureDir(dataDir);

        // 设置开机启动
        app.setLoginItemSettings({
            openAtLogin: defaultSettings.startWithSystem
        });

        // 需要重启服务器
        if (serverRunning) {
            // 关闭当前服务器
            if (pythonProcess) {
                if (process.platform === 'win32') {
                    spawn('taskkill', ['/pid', pythonProcess.pid, '/f', '/t']);
                } else {
                    pythonProcess.kill('SIGTERM');
                }
                pythonProcess = null;
            }

            // 重新启动服务器
            setTimeout(() => {
                startPythonServer();
            }, 1000);
        }

        return {
            success: true,
            settings: defaultSettings
        };
    } catch (error) {
        log.error(`重置设置错误: ${error.message}`);
        return { success: false, error: error.message };
    }
});

// 打开外部链接
ipcMain.on('open-external', (event, url) => {
    shell.openExternal(url);
});

// 检查更新
ipcMain.handle('check-for-updates', async () => {
    if (process.env.NODE_ENV === 'development') {
        // 开发环境模拟更新检查
        return { hasUpdate: false };
    } else {
        try {
            const result = await autoUpdater.checkForUpdates();
            if (result && result.updateInfo) {
                return {
                    hasUpdate: result.updateInfo.version !== app.getVersion(),
                    version: result.updateInfo.version
                };
            }
            return { hasUpdate: false };
        } catch (error) {
            log.error(`检查更新错误: ${error.message}`);
            throw error;
        }
    }
});

// 自动更新事件
autoUpdater.on('update-downloaded', () => {
    mainWindow.webContents.send('update-downloaded');
});