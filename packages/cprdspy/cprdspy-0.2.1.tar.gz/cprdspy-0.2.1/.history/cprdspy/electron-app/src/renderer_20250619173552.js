// 获取DOM元素
const minimizeBtn = document.getElementById('minimize-btn');
const maximizeBtn = document.getElementById('maximize-btn');
const closeBtn = document.getElementById('close-btn');
const navItems = document.querySelectorAll('.nav-item');
const views = document.querySelectorAll('.view');
const dashFrame = document.getElementById('dash-frame');
const loadingElement = document.getElementById('loading');
const serverStatusElement = document.getElementById('server-status');
const memoryUsageElement = document.getElementById('memory-usage');
const importFileBtn = document.getElementById('import-file-btn');
const fileListBody = document.getElementById('file-list-body');
const themeSelect = document.getElementById('theme-select');
const saveSettingsBtn = document.getElementById('save-settings');
const resetSettingsBtn = document.getElementById('reset-settings');
const appVersionElement = document.getElementById('app-version');
const githubLinkBtn = document.getElementById('github-link');
const docsLinkBtn = document.getElementById('docs-link');
const checkUpdatesBtn = document.getElementById('check-updates');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 设置应用版本
    window.electronAPI.getAppVersion().then(version => {
        appVersionElement.textContent = version;
    });

    // 初始化主题
    initTheme();

    // 监听服务器状态
    window.electronAPI.onServerStatus((status) => {
        updateServerStatus(status);
    });

    // 每秒更新内存使用情况
    setInterval(updateMemoryUsage, 1000);

    // 初始化文件列表
    refreshFileList();
});

// 窗口控制
minimizeBtn.addEventListener('click', () => {
    window.electronAPI.windowControl('minimize');
});

maximizeBtn.addEventListener('click', () => {
    window.electronAPI.windowControl('maximize');
});

closeBtn.addEventListener('click', () => {
    window.electronAPI.windowControl('close');
});

// 导航菜单切换
navItems.forEach(item => {
    item.addEventListener('click', () => {
        const viewId = item.getAttribute('data-view');

        // 更新活动菜单项
        navItems.forEach(navItem => {
            navItem.classList.remove('active');
        });
        item.classList.add('active');

        // 显示对应视图
        views.forEach(view => {
            view.classList.remove('active');
        });
        document.getElementById(`${viewId}-view`).classList.add('active');
    });
});

// 更新服务器状态
function updateServerStatus(status) {
    const statusText = {
        'running': '服务器状态: 运行中',
        'error': '服务器状态: 错误',
        'stopped': '服务器状态: 已停止',
        'starting': '服务器状态: 正在启动...'
    };

    serverStatusElement.className = 'status-item';
    serverStatusElement.classList.add(status);
    serverStatusElement.querySelector('span').textContent = statusText[status] || '服务器状态: 未知';

    if (status === 'running') {
        // 服务器启动成功，加载Dash应用
        dashFrame.src = 'http://localhost:8050';
        hideLoading();
    } else if (status === 'error') {
        hideLoading();
        showNotification('服务器错误', '无法启动Python服务器，请检查日志', 'error');
    }
}

// 更新内存使用情况
function updateMemoryUsage() {
    window.electronAPI.getMemoryUsage().then(memory => {
        memoryUsageElement.querySelector('span').textContent = `内存: ${memory.toFixed(1)} MB`;
    });
}

// 隐藏加载状态
function hideLoading() {
    loadingElement.style.display = 'none';
}

// 显示加载状态
function showLoading(message = '正在加载...') {
    loadingElement.querySelector('p').textContent = message;
    loadingElement.style.display = 'flex';
}

// 刷新文件列表
function refreshFileList() {
    showLoading('正在加载文件列表...');

    window.electronAPI.getFileList().then(files => {
        fileListBody.innerHTML = '';

        if (files.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="4" class="empty-list">没有可用的文件</td>';
            fileListBody.appendChild(row);
        } else {
            files.forEach(file => {
                const row = document.createElement('tr');

                row.innerHTML = `
                    <td>${file.name}</td>
                    <td>${formatFileSize(file.size)}</td>
                    <td>${formatDate(file.date)}</td>
                    <td>
                        <button class="btn" data-action="view" data-file="${file.path}">
                            <i class="mdi mdi-eye"></i>
                        </button>
                        <button class="btn" data-action="delete" data-file="${file.path}">
                            <i class="mdi mdi-delete"></i>
                        </button>
                    </td>
                `;

                fileListBody.appendChild(row);
            });

            // 添加文件操作事件监听
            document.querySelectorAll('[data-action="view"]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const filePath = btn.getAttribute('data-file');
                    viewFile(filePath);
                });
            });

            document.querySelectorAll('[data-action="delete"]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const filePath = btn.getAttribute('data-file');
                    deleteFile(filePath);
                });
            });
        }

        hideLoading();
    }).catch(error => {
        hideLoading();
        showNotification('错误', '无法加载文件列表', 'error');
        console.error('加载文件列表错误:', error);
    });
}

// 导入文件
importFileBtn.addEventListener('click', () => {
    window.electronAPI.importFile().then(result => {
        if (result.success) {
            showNotification('成功', '文件导入成功', 'success');
            refreshFileList();
        } else {
            showNotification('错误', result.error || '文件导入失败', 'error');
        }
    });
});

// 查看文件
function viewFile(filePath) {
    // 切换到仪表盘视图
    navItems.forEach(navItem => {
        navItem.classList.remove('active');
        if (navItem.getAttribute('data-view') === 'dashboard') {
            navItem.classList.add('active');
        }
    });

    views.forEach(view => {
        view.classList.remove('active');
    });
    document.getElementById('dashboard-view').classList.add('active');

    // 加载文件到仪表盘
    showLoading('正在加载文件数据...');
    window.electronAPI.loadFile(filePath).then(result => {
        if (result.success) {
            // 刷新仪表盘
            dashFrame.src = 'http://localhost:8050?file=' + encodeURIComponent(filePath);
        } else {
            showNotification('错误', result.error || '无法加载文件', 'error');
        }
        hideLoading();
    });
}

// 删除文件
function deleteFile(filePath) {
    if (confirm('确定要删除此文件吗？此操作无法撤销。')) {
        window.electronAPI.deleteFile(filePath).then(result => {
            if (result.success) {
                showNotification('成功', '文件已删除', 'success');
                refreshFileList();
            } else {
                showNotification('错误', result.error || '无法删除文件', 'error');
            }
        });
    }
}

// 主题设置
function initTheme() {
    // 从本地存储获取主题设置
    const savedTheme = localStorage.getItem('theme') || 'system';
    themeSelect.value = savedTheme;
    applyTheme(savedTheme);

    // 监听主题选择变化
    themeSelect.addEventListener('change', () => {
        const theme = themeSelect.value;
        localStorage.setItem('theme', theme);
        applyTheme(theme);
    });
}

function applyTheme(theme) {
    if (theme === 'system') {
        // 检测系统主题
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
        }

        // 监听系统主题变化
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (themeSelect.value === 'system') {
                document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
            }
        });
    } else {
        document.documentElement.setAttribute('data-theme', theme);
    }
}

// 设置保存
saveSettingsBtn.addEventListener('click', () => {
    const settings = {
        serverPort: parseInt(document.getElementById('server-port').value),
        dataDir: document.getElementById('data-dir').value,
        startWithSystem: document.getElementById('start-with-system').checked
    };

    window.electronAPI.saveSettings(settings).then(result => {
        if (result.success) {
            showNotification('成功', '设置已保存', 'success');
        } else {
            showNotification('错误', result.error || '无法保存设置', 'error');
        }
    });
});

// 设置重置
resetSettingsBtn.addEventListener('click', () => {
    if (confirm('确定要重置所有设置吗？')) {
        window.electronAPI.resetSettings().then(result => {
            if (result.success) {
                // 更新UI
                document.getElementById('server-port').value = result.settings.serverPort;
                document.getElementById('data-dir').value = result.settings.dataDir;
                document.getElementById('start-with-system').checked = result.settings.startWithSystem;

                showNotification('成功', '设置已重置', 'success');
            } else {
                showNotification('错误', result.error || '无法重置设置', 'error');
            }
        });
    }
});

// 外部链接
githubLinkBtn.addEventListener('click', () => {
    window.electronAPI.openExternal('https://github.com/yourusername/cprdspy');
});

docsLinkBtn.addEventListener('click', () => {
    window.electronAPI.openExternal('https://yourusername.github.io/cprdspy-docs');
});

// 检查更新
checkUpdatesBtn.addEventListener('click', () => {
    showLoading('正在检查更新...');

    window.electronAPI.checkForUpdates().then(result => {
        hideLoading();

        if (result.hasUpdate) {
            showNotification('更新可用', `发现新版本: ${result.version}`, 'info');
        } else {
            showNotification('已是最新版本', '您的应用已是最新版本', 'success');
        }
    }).catch(() => {
        hideLoading();
        showNotification('检查更新失败', '无法检查更新，请稍后再试', 'error');
    });
});

// 通知系统
function showNotification(title, message, type = 'info') {
    const container = document.getElementById('notification-container');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    const iconMap = {
        'info': 'mdi-information',
        'success': 'mdi-check-circle',
        'warning': 'mdi-alert',
        'error': 'mdi-alert-circle'
    };

    notification.innerHTML = `
        <i class="mdi ${iconMap[type]} notification-icon"></i>
        <div class="notification-content">
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close">
            <i class="mdi mdi-close"></i>
        </button>
    `;

    container.appendChild(notification);

    // 关闭按钮
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });

    // 自动关闭
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';

        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// 辅助函数
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';

    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}