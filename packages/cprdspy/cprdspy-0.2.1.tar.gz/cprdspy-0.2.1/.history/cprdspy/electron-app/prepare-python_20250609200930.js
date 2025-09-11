const fs = require('fs-extra');
const path = require('path');
const { execSync } = require('child_process');
const { pipeline } = require('stream/promises');

// 配置
const pythonVersion = '3.9.13'; // 使用与开发环境相同的Python版本
const pythonDir = path.join(__dirname, 'python');
const appDir = path.join(__dirname, '..', 'CPR_Dashborad');
const requirements = [
    'dash',
    'numpy',
    'plotly'
    // 添加其他必要的依赖
];

async function preparePythonEnv() {
    try {
        console.log('开始准备Python环境...');

        // 清理旧的Python目录
        if (fs.existsSync(pythonDir)) {
            console.log('清理旧的Python目录...');
            await fs.remove(pythonDir);
        }

        // 创建新的Python目录
        await fs.mkdir(pythonDir, { recursive: true });

        // 下载并解压Python嵌入式发行版
        console.log('下载Python嵌入式发行版...');
        const pythonEmbedUrl = `https://www.python.org/ftp/python/${pythonVersion}/python-${pythonVersion}-embed-amd64.zip`;

        // 使用PowerShell下载
        const downloadCommand = `
      $ProgressPreference = 'SilentlyContinue';
      Invoke-WebRequest -Uri "${pythonEmbedUrl}" -OutFile "${path.join(pythonDir, 'python-embed.zip')}";
    `;

        execSync(`powershell -Command "${downloadCommand}"`, { stdio: 'inherit' });

        // 解压Python
        console.log('解压Python...');
        execSync(`powershell -Command "Expand-Archive -Path '${path.join(pythonDir, 'python-embed.zip')}' -DestinationPath '${pythonDir}' -Force"`, { stdio: 'inherit' });

        // 下载get-pip.py
        console.log('下载pip安装程序...');
        const getPipCommand = `
      $ProgressPreference = 'SilentlyContinue';
      Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "${path.join(pythonDir, 'get-pip.py')}";
    `;

        execSync(`powershell -Command "${getPipCommand}"`, { stdio: 'inherit' });

        // 修改python*._pth文件以启用site-packages
        const pthFiles = fs.readdirSync(pythonDir).filter(file => file.endsWith('._pth'));
        for (const pthFile of pthFiles) {
            const pthPath = path.join(pythonDir, pthFile);
            let content = fs.readFileSync(pthPath, 'utf8');
            if (content.includes('#import site')) {
                content = content.replace('#import site', 'import site');
                fs.writeFileSync(pthPath, content);
            }
        }

        // 安装pip
        console.log('安装pip...');
        execSync(`"${path.join(pythonDir, 'python.exe')}" "${path.join(pythonDir, 'get-pip.py')}" --no-warn-script-location`, { stdio: 'inherit' });

        // 安装依赖
        console.log('安装Python依赖...');
        const pipCommand = `"${path.join(pythonDir, 'python.exe')}" -m pip install ${requirements.join(' ')} --no-warn-script-location`;
        execSync(pipCommand, { stdio: 'inherit' });

        // 复制应用文件
        console.log('复制应用文件...');
        await fs.copy(appDir, path.join(pythonDir, 'CPR_Dashborad'), {
            filter: (src) => {
                // 排除不需要的文件
                return !src.includes('__pycache__') && !src.endsWith('.pyc');
            }
        });

        // 创建启动脚本
        const launcherScript = `
import os
import sys

# 添加应用目录到Python路径
app_dir = os.path.join(os.path.dirname(__file__), 'CPR_Dashborad')
sys.path.insert(0, app_dir)

# 导入并运行应用
from app_waves import app

if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_hot_reload=False)
    `;

        await fs.writeFile(path.join(pythonDir, 'app_waves.py'), launcherScript);

        console.log('Python环境准备完成！');

    } catch (error) {
        console.error('准备Python环境时出错:', error);
        process.exit(1);
    }
}

// 运行准备脚本
preparePythonEnv().catch(console.error);