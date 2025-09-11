import numpy as np
import plotly.graph_objects as go

# 参数设置
R = 1.0  # 球体半径
transparency = 0.5  # 透明度(0-1)


# 生成半径R圆上均匀N等分点
def n_points(N, R, theta_p=0):
    return [
        [
            R * np.cos(i * 2 * np.pi / N + np.pi / 2 + theta_p),
            R * np.sin(i * 2 * np.pi / N + np.pi / 2 + theta_p),
        ]
        for i in range(N)
    ]


a = n_points(3, 1)
print(a)
