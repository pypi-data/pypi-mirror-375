const { contextBridge, ipcRenderer } = require('electron');

// 暴露给渲染进程的API
contextBridge.exposeInMainWorld('electronAPI', {
    // 窗口控制
    windowControl: (command) => ipcRenderer.send('window-control', command),

    // 获取应用版本
    getAppVersion: () => ipcRenderer.invoke('get-app-version'),

    // 服务器状态监听
    onServerStatus: (callback) => {
        ipcRenderer.on('server-status', (event, status) => callback(status));
    },

    // 获取内存使用情况
    getMemoryUsage: () => ipcRenderer.invoke('get-memory-usage'),

    // 文件操作
    getFileList: () => ipcRenderer.invoke('get-file-list'),
    importFile: () => ipcRenderer.invoke('import-file'),
    loadFile: (filePath) => ipcRenderer.invoke('load-file', filePath),
    deleteFile: (filePath) => ipcRenderer.invoke('delete-file', filePath),

    // 设置操作
    saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
    resetSettings: () => ipcRenderer.invoke('reset-settings'),

    // 外部链接
    openExternal: (url) => ipcRenderer.send('open-external', url),

    // 更新检查
    checkForUpdates: () => ipcRenderer.invoke('check-for-updates')
});