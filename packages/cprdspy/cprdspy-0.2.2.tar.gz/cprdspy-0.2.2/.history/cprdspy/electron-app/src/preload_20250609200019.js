const { contextBridge, ipcRenderer } = require('electron');

// 暴露安全的API给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
    // 窗口控制
    minimizeWindow: () => ipcRenderer.send('window-control', 'minimize'),
    maximizeWindow: () => ipcRenderer.send('window-control', 'maximize'),
    closeWindow: () => ipcRenderer.send('window-control', 'close'),
    quitApp: () => ipcRenderer.send('window-control', 'quit'),

    // 监听服务器状态
    onServerStatus: (callback) => {
        ipcRenderer.on('server-status', (event, status) => callback(status));
    },

    // 打开外部链接
    openExternal: (url) => ipcRenderer.send('open-external', url)
});