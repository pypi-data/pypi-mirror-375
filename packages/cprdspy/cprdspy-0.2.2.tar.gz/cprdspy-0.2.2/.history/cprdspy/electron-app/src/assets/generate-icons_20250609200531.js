const fs = require('fs');
const path = require('path');
const { createCanvas } = require('canvas');
const { app } = require('electron');

// 确保目录存在
const assetsDir = __dirname;
if (!fs.existsSync(assetsDir)) {
    fs.mkdirSync(assetsDir, { recursive: true });
}

// 创建图标
function createIcon(size, filename) {
    const canvas = createCanvas(size, size);
    const ctx = canvas.getContext('2d');

    // 背景
    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(0, 0, size, size);

    // 波形图案
    ctx.beginPath();
    ctx.moveTo(size * 0.1, size * 0.5);

    // 创建波形
    for (let i = 0; i < size; i += size / 20) {
        const x = size * 0.1 + i;
        const height = Math.sin(i / (size / 5)) * (size * 0.2);
        const y = size * 0.5 + height;

        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }

    ctx.strokeStyle = '#3498db';
    ctx.lineWidth = size / 20;
    ctx.stroke();

    // 保存为PNG
    const buffer = canvas.toBuffer('image/png');
    fs.writeFileSync(path.join(assetsDir, filename), buffer);

    console.log(`创建图标: ${filename}`);
}

// 创建不同尺寸的图标
createIcon(16, 'icon-16.png');
createIcon(32, 'icon-32.png');
createIcon(64, 'icon-64.png');
createIcon(128, 'icon-128.png');
createIcon(256, 'icon.png'); // 主图标
createIcon(32, 'tray-icon.png'); // 托盘图标

console.log('所有图标已生成');