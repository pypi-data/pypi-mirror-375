const fs = require('fs-extra');
const path = require('path');
const { execSync } = require('child_process');
const { pipeline } = require('stream/promises');

// 配置
const pythonVersion = '3.9.13'; // 使用与开发环境相同的Python版本

// 日志函数
function log(message) {
    console.log(`[prepare-python] ${message}`);
}

// 主函数
async function main() {
    try {
        log('开始准备Python环境...');

        // 创建Python目录
        const pythonDir = path.join(__dirname, 'python');
        log(`创建Python目录: ${pythonDir}`);
        await fs.ensureDir(pythonDir);

        // 复制Python应用文件
        const sourceDashboardDir = path.join(__dirname, '..', 'CPR_Dashborad');
        const sourceWavesDir = path.join(__dirname, '..', 'CPR_plotly', 'Waves');

        log(`复制Dash应用文件从 ${sourceDashboardDir} 到 ${pythonDir}`);
        await fs.copy(sourceDashboardDir, pythonDir, {
            filter: (src) => {
                // 排除__pycache__目录和.pyc文件
                return !src.includes('__pycache__') && !src.endsWith('.pyc');
            }
        });

        // 创建Waves目录
        const wavesDir = path.join(pythonDir, 'Waves');
        await fs.ensureDir(wavesDir);

        log(`复制波形配置文件从 ${sourceWavesDir} 到 ${wavesDir}`);
        await fs.copy(sourceWavesDir, wavesDir, {
            filter: (src) => {
                // 排除__pycache__目录和.pyc文件
                return !src.includes('__pycache__') && !src.endsWith('.pyc');
            }
        });

        // 创建requirements.txt文件
        const requirementsPath = path.join(pythonDir, 'requirements.txt');
        log(`创建requirements.txt: ${requirementsPath}`);
        await fs.writeFile(requirementsPath, `
dash==2.9.3
plotly==5.14.1
numpy==1.24.3
pandas==2.0.1
        `.trim());

        log('Python环境准备完成');
    } catch (error) {
        console.error(`[prepare-python] 错误: ${error.message}`);
        process.exit(1);
    }
}

// 执行主函数
main();