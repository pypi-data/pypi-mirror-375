import plotly.graph_objects as go
import numpy as np

# 参数设置
R = 1.0  # 球体半径
n = 3
transparency = 0.5  # 透明度(0-1)


def n_points(N, R, theta_p=0):
    return [
        [
            R * np.cos(i * 2 * np.pi / N + np.pi / 2 + theta_p),
            R * np.sin(i * 2 * np.pi / N + np.pi / 2 + theta_p),
        ]
        for i in range(N)
    ]


a = n_points(n, 1)

# 生成球面网格点
theta = np.linspace(0, 2 * np.pi, 50)  # 方位角
phi = np.linspace(0, np.pi, 25)  # 极角
theta_grid, phi_grid = np.meshgrid(theta, phi)

# 初始化列表
spheres = []  # 存储所有球体
centers = []  # 存储所有球心

for i in range(n):
    # 转换为直角坐标
    x = R * np.sin(phi_grid) * np.cos(theta_grid) + a[i][0]
    y = R * np.sin(phi_grid) * np.sin(theta_grid) + a[i][1]
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
    spheres.append(sphere)

    # 标记球心
    center = go.Scatter3d(
        x=[a[i][0]],  # 需要传入列表
        y=[a[i][1]],  # 需要传入列表
        z=[0],
        mode="markers",
        marker=dict(size=5, color="red"),
        name=f"球心 {i+1}",  # 为每个球心添加编号
    )
    centers.append(center)

# 创建图形,合并所有数据
fig = go.Figure(data=spheres + centers)

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
