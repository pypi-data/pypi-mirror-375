const fs = require('fs-extra');
const path = require('path');
const { execSync } = require('child_process');
const log = require('electron-log');

// 配置路径
const rootDir = path.resolve(__dirname, '..');
const pythonSourceDir = path.join(rootDir, 'CPR_Dashborad');
const pythonDestDir = path.join(__dirname, 'python');
const requirementsFile = path.join(pythonSourceDir, 'requirements.txt');

// 确保日志目录存在
fs.ensureDirSync(path.join(__dirname, 'logs'));
log.transports.file.resolvePath = () => path.join(__dirname, 'logs', 'prepare-python.log');

/**
 * 准备Python环境
 */
async function preparePythonEnv() {
    try {
        log.info('开始准备Python环境...');

        // 检查源目录是否存在
        if (!fs.existsSync(pythonSourceDir)) {
            throw new Error(`Python源目录不存在: ${pythonSourceDir}`);
        }

        // 检查requirements.txt是否存在
        if (!fs.existsSync(requirementsFile)) {
            throw new Error(`requirements.txt不存在: ${requirementsFile}`);
        }

        // 清理目标目录
        log.info(`清理目标目录: ${pythonDestDir}`);
        await fs.remove(pythonDestDir);
        await fs.ensureDir(pythonDestDir);

        // 复制Python源代码
        log.info(`复制Python源代码到: ${pythonDestDir}`);
        await fs.copy(pythonSourceDir, pythonDestDir, {
            filter: (src) => {
                // 排除__pycache__目录和.pyc文件
                return !src.includes('__pycache__') && !src.endsWith('.pyc');
            }
        });

        // 创建虚拟环境
        log.info('创建Python虚拟环境...');
        const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

        // 在Windows上创建虚拟环境
        if (process.platform === 'win32') {
            execSync(`${pythonCmd} -m venv ${pythonDestDir}\\venv`, { stdio: 'inherit' });
            execSync(`${pythonDestDir}\\venv\\Scripts\\pip install -r ${requirementsFile}`, { stdio: 'inherit' });

            // 创建启动脚本
            const launcherScript = `@echo off
set PYTHONPATH=%~dp0
"%~dp0\\venv\\Scripts\\python.exe" "%~dp0\\app.py" %*
`;
            fs.writeFileSync(path.join(pythonDestDir, 'python.bat'), launcherScript);

            // 复制python.exe到根目录，方便主进程调用
            fs.copyFileSync(
                path.join(pythonDestDir, 'venv', 'Scripts', 'python.exe'),
                path.join(pythonDestDir, 'python.exe')
            );
        }
        // 在macOS/Linux上创建虚拟环境
        else {
            execSync(`${pythonCmd} -m venv ${pythonDestDir}/venv`, { stdio: 'inherit' });
            execSync(`${pythonDestDir}/venv/bin/pip install -r ${requirementsFile}`, { stdio: 'inherit' });

            // 创建启动脚本
            const launcherScript = `#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "\${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$SCRIPT_DIR
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/app.py" "$@"
`;
            fs.writeFileSync(path.join(pythonDestDir, 'python.sh'), launcherScript);
            execSync(`chmod +x ${path.join(pythonDestDir, 'python.sh')}`, { stdio: 'inherit' });

            // 创建符号链接
            fs.symlinkSync(
                path.join('venv', 'bin', 'python'),
                path.join(pythonDestDir, 'python')
            );
        }

        log.info('Python环境准备完成!');
    } catch (error) {
        log.error(`准备Python环境失败: ${error.message}`);
        process.exit(1);
    }
}

// 执行主函数
preparePythonEnv().catch(err => {
    log.error(err);
    process.exit(1);
});