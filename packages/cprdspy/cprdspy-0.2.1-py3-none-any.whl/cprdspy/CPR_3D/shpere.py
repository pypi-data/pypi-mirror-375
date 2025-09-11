import plotly.graph_objects as go
import numpy as np

# 参数设置
R = 1.0  # 球体半径
transparency = 0.5  # 透明度(0-1)

# 生成球面网格点
theta = np.linspace(0, 2 * np.pi, 50)  # 方位角
phi = np.linspace(0, np.pi, 25)  # 极角
theta_grid, phi_grid = np.meshgrid(theta, phi)

# 转换为直角坐标
x = R * np.sin(phi_grid) * np.cos(theta_grid)
y = R * np.sin(phi_grid) * np.sin(theta_grid)
z = R * np.cos(phi_grid)

# 创建球体表面
sphere = go.Surface(
    x=x,
    y=y,
    z=z,
    colorscale=[[0, "blue"], [1, "blue"]],
    opacity=transparency,
    showscale=False,
)
# 转换为直角坐标
x1 = R * np.sin(phi_grid) * np.cos(theta_grid)
y1 = R * np.sin(phi_grid) * np.sin(theta_grid)
z1 = R * np.cos(phi_grid) - R

# 创建球体表面
sphere1 = go.Surface(
    x=x1,
    y=y1,
    z=z1,
    colorscale=[[0, "lime"], [1, "lime"]],
    opacity=transparency,
    showscale=False,
)

# 标记球心
center = go.Scatter3d(
    x=[0], y=[0], z=[0], mode="markers", marker=dict(size=5, color="red"), name="球心"
)
center1 = go.Scatter3d(
    x=[0],
    y=[0],
    z=[-1],
    mode="markers",
    marker=dict(size=5, color="green"),
    name="球心1",
)

# 创建图形
fig = go.Figure(data=[sphere, center, sphere1, center1])

# 关键设置：强制等比例显示
fig.update_layout(
    scene=dict(
        xaxis=dict(range=[-R * 2, R * 2], nticks=5),  # 设置轴范围略大于半径
        yaxis=dict(range=[-R * 2, R * 2], nticks=5),
        zaxis=dict(range=[-R * 2, R * 2], nticks=5),
        aspectmode="manual",  # 手动设置比例
        aspectratio=dict(x=1, y=1, z=1),  # 1:1:1比例
    ),
    width=700,
    height=600,
    title="透明正球体(完美比例)",
)

fig.show()
