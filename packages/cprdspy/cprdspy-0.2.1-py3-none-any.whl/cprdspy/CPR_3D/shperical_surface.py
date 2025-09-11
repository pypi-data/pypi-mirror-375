import plotly.graph_objects as go
import numpy as np


def spherical_surface(center, alpha, beta=0, R=1):
    # 参数设置
    theta = np.linspace(0, np.pi, 50)  # 极角 θ ∈ [0, π]（上下半球）
    phi = np.linspace(alpha, beta, 50)  # 方位角 φ ∈ [α, β]
    # 生成网格
    theta_grid, phi_grid = np.meshgrid(theta, phi)
    # 转换为直角坐标系
    x = R * np.sin(theta_grid) * np.cos(phi_grid) + center[0]
    y = R * np.sin(theta_grid) * np.sin(phi_grid) + center[1]
    z = R * np.cos(theta_grid) + center[2]
    # 绘制曲面
    fig = go.Figure(
        data=[
            go.Surface(x=x, y=y, z=z, colorscale="#0f0", opacity=0.8, showscale=False)
        ]
    )
    # 添加辅助平面
    x_bound0 = R * np.sin(theta) * np.cos(alpha) + center[0]  # 边界
    y_bound0 = R * np.sin(theta) * np.sin(alpha) + center[1]
    z_bound0 = R * np.cos(theta) + center[2]
    x_bound1 = R * np.sin(theta) * np.cos(beta) + center[0]  # 边界
    y_bound1 = R * np.sin(theta) * np.sin(beta) + center[1]
    z_bound1 = R * np.cos(theta) + center[2]
    fig.add_trace(
        go.Scatter3d(
            x=x_bound0,
            y=y_bound0,
            z=z_bound0,
            mode="lines",
            line=dict(color="red", width=5),
            name="α=alpha",
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=x_bound1,
            y=y_bound1,
            z=z_bound1,
            mode="lines",
            line=dict(color="blue", width=5),
            name="β=beta",
        )
    )
    return fig


surface = spherical_surface(
    (0, np.sqrt(2) / 2, 0),
    alpha=-np.arccos(np.sqrt(3 + 8 * np.sqrt(2)) * (4 * np.sqrt(2) - 1) / 18),
    beta=0,
    R=1,
)
# 设置布局
R = 1
surface.fig.update_layout(
    title="球面坐标系中 φ ∈ [0, π/4] 的曲面",
    scene=dict(
        xaxis=dict(range=[-R * 2, R * 2], nticks=5),  # 设置轴范围略大于半径
        yaxis=dict(range=[-R * 2, R * 2], nticks=5),
        zaxis=dict(range=[-R * 2, R * 2], nticks=5),
        aspectmode="manual",  # 手动设置比例
        aspectratio=dict(x=1, y=1, z=1),  # 1:1:1比例
    ),
    width=700,
    height=700,
)

surface.fig.show()
