"""
创建简单的logo图片
"""

from PIL import Image, ImageDraw, ImageFont
import os

# 创建一个200x50的图像，白色背景
img = Image.new("RGBA", (200, 50), color=(255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# 绘制一个圆形
draw.ellipse((10, 10, 40, 40), fill=(76, 175, 80))

# 绘制一个波形
x_points = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180]
y_points = [25, 15, 35, 15, 35, 15, 35, 15, 35, 15, 35, 15, 35, 25]
draw.line(list(zip(x_points, y_points)), fill=(33, 150, 243), width=3)

# 保存图像
img.save("logo.png")
print("Logo创建成功！")
