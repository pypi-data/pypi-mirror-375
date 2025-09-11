import numpy as np
import plotly.graph_objects as go
import sys

sys.path.append("./dot.py")

"""点(Dots)"""


# 生成半径R圆上均匀N等分点
def n_points(N, R, theta=0):
    return [
        [
            R * np.cos(i * 2 * np.pi / N + np.pi / 2 + theta),
            R * np.sin(i * 2 * np.pi / N + np.pi / 2 + theta),
        ]
        for i in range(N)
    ]


# 画出点
def draw_points(points, colorp="b", size=10):
    fig = go.Figure()
    for point in points:
        fig.add_trace(
            go.Scatter(
                x=[point[0]],
                y=[point[1]],
                mode="markers",
                marker=dict(color=colorp, size=size),
            )
        )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 双向生成点阵
def n_points_array(n, m, theta=0):
    points = []
    for i in range(m):
        points += n_points(n, (np.cos(np.pi / n)) ** i, i * (np.pi / n + theta))
        points += n_points(n, (np.cos(np.pi / n)) ** (-i), i * (np.pi / n - theta))
    return points


# 向内生成点阵
def n_points_array_inner(n, m, theta=0):
    points = []
    for i in range(m):
        points += n_points(n, (np.cos(np.pi / n)) ** i, i * (np.pi / n + theta))
    return points


# 向外生成点阵
def n_points_array_outer(n, m, theta=0):
    points = []
    for i in range(m):
        points += n_points(n, (np.cos(np.pi / n)) ** (-i), i * (np.pi / n + theta))
    return points


# 向外旋转生成点阵
def n_points_array_outer_rotate(n, m, alpha=0, theta=0):
    points = []
    for i in range(m):
        points += n_points(
            n, (np.cos(np.pi / n)) ** (-i), alpha + i * (np.pi / n + theta)
        )
    return points


# 向内旋转生成点阵
def n_points_array_inner_rotate(n, m, alpha=0, theta=0):
    points = []
    for i in range(m):
        points += n_points(n, (np.cos(np.pi / n)) ** i, alpha + i * (np.pi / n + theta))
    return points


# 画N边形点阵
def draw_n_points_array(n, m, theta=0, color="b", size=10):
    fig = go.Figure()
    for i in range(m):
        points = n_points(n, (np.cos(np.pi / n)) ** i, i * (np.pi / n + theta))
        sub_fig = draw_points(points, color, size)
        fig.add_traces(sub_fig.data)
        points = n_points(n, (np.cos(np.pi / n)) ** (-i), i * (np.pi / n - theta))
        sub_fig = draw_points(points, color, size)
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 向外画点阵
def draw_n_points_array_outer(n, m, theta=0, color="b", size=10):
    fig = go.Figure()
    for i in range(m):
        points = n_points(n, (np.cos(np.pi / n)) ** (-i), i * (np.pi / n + theta))
        sub_fig = draw_points(points, color, size)
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 向内画点阵
def draw_n_points_array_inner(n, m, theta=0, color="b", size=10):
    fig = go.Figure()
    for i in range(m):
        points = n_points(n, (np.cos(np.pi / n)) ** i, i * (np.pi / n - theta))
        sub_fig = draw_points(points, color, size)
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig
