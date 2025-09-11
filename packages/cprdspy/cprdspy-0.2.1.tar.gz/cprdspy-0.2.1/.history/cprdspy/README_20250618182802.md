# CPRDSpy

CPRDSpy是一个用于创建和可视化CPR（Circle Point Round）模式的Python库。它提供了丰富的工具来生成各种美丽的数学图案，包括圆形、波形、花朵等。

## 特点

- 多种可视化后端支持：Plotly、Matplotlib和3D渲染
- 交互式仪表盘，用于实时调整参数和探索模式
- 丰富的图形类型：圆形、波形、花朵、螺旋、星形等
- 支持自定义主题和样式
- 包含Electron应用程序，提供桌面体验

## 安装

使用pip安装CPRDSpy：

```bash
pip install cprdspy
```

## 快速开始

### 基本用法

```python
import cprdspy
import plotly.io as pio

# 设置主题
cprdspy.set_theme("dark")

# 创建一个简单的圆形波
fig = cprdspy.wave_circle_arithmetic(
    A=0.5,  # 振幅
    F=3,    # 频率
    P=11,   # 周期
    color="#1f77b4"  # 颜色
)

# 显示图形
fig.show()
```

### 使用交互式仪表盘

```python
from cprdspy.electron_app.python.app_waves import app

# 运行Dash应用
app.run_server(debug=True)
```

## 模块结构

CPRDSpy包含以下主要模块：

- `CPR_plotly`: 使用Plotly后端的图形生成函数
- `CPR_matplotlib`: 使用Matplotlib后端的图形生成函数
- `CPR_3D`: 3D图形生成函数
- `CPR_Dashborad`: 交互式仪表盘应用
- `CPR_js`: JavaScript实现，用于Web集成

## 示例

### 创建等差圆形波

```python
import cprdspy

# 创建等差圆形波
fig = cprdspy.wave_circle_arithmetic(
    A=0.5,  # 振幅
    F=3,    # 频率
    P=11,   # 周期
    color="#1f77b4",  # 颜色
    theta=0,  # 相位
    R=1.0,  # 基准半径
    width=2,  # 线宽
    opacity=1.0  # 透明度
)

# 显示图形
fig.show()
```

### 创建等比圆形波

```python
import cprdspy

# 创建等比圆形波
fig = cprdspy.wave_circle_geometric(
    A=1.2,  # 振幅比例
    F=5,    # 频率
    P=7,    # 周期
    color="#d62728",  # 颜色
    theta=0,  # 相位
    R=1.0,  # 基准半径
)

# 显示图形
fig.show()
```

## 贡献

欢迎贡献！请随时提交问题或拉取请求。

1. Fork仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个拉取请求

## 许可证

本项目采用MIT许可证 - 详情请参阅[LICENSE](LICENSE)文件。

## 联系方式

如有任何问题或建议，请通过[GitHub Issues](https://github.com/yourusername/cprdspy/issues)联系我们。