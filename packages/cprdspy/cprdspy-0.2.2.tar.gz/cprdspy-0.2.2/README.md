# CPR可视化工具包

一个用于CPR(圈点圆)可视化的Python工具包，基于Plotly构建。

## 功能特点

- 实时CPR波形可视化
- 种类繁多的花形可视化
- 交互式数据展示
- 自定义图表样式
- 导出图片功能

## 安装

```bash
pip install cprdspy
```

## 快速开始

```python
from cprdspy import wave_circle_geometric


# 创建可视化器实例
fig=wave_circle_geometric(1.2, 2, 12)

# 显示波形
fig.show()
```
```python
from cprdspy import config, set_theme,flowers_flower_by_petal_multi

# 设置主题
set_theme("dark")

# 自定义配置
config.line_width = 3
config.opacity = 0.8
# config.show_grid = True
# config.show_legend = False
# config.show_axis = False    
config.axis_mirror = False
# 绘图时应用配置
fig = flowers_flower_by_petal_multi(
    [0, 0], 1, 1, 4, np.sqrt(2), 3, 12, color="red", width=2, opacity=0.5
)
config.apply_to_figure(fig)
fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))
```

## 文档

详细的文档请访问：[文档链接](https://github.com/lbylzk8/cprdspy#readme)

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Pull Request 或创建 Issue！

## 联系方式

如有问题，请通过以下方式联系我们：
- 提交 Issue
- 发送邮件至：lbylzk8@outlook.com