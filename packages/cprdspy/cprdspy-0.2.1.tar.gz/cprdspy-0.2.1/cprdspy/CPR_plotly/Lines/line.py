import numpy as np
import plotly.graph_objects as go
import sys

sys.path.append("./line.py")


def swastika(N, R=1, theta=0):
    points = [
        (
            R * np.sqrt(2) ** i * np.cos(i * np.pi / 4 + theta),
            R * np.sqrt(2) ** i * np.sin(i * np.pi / 4 + theta),
        )
        for i in range(N)
    ]
    return points


def draw_swastika_plotly(N, R=1, theta=0, color="blue"):
    points = swastika(N, R, theta)
    fig = go.Figure()
    for i in range(len(points)):
        fig.add_trace(
            go.Scatter(
                x=[points[i][0]],
                y=[points[i][1]],
                mode="markers",
                marker=dict(color=color),
            )
        )
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            fig.add_trace(
                go.Scatter(
                    x=[points[i][0], points[j][0]],
                    y=[points[i][1], points[j][1]],
                    mode="lines",
                    line=dict(color=color),
                )
            )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 线
# 生成半径R圆上N等分点
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


# 生成半径R圆上N等分点
def n_points(N, R, theta=0):
    return [
        [
            R * np.cos(i * 2 * np.pi / N + np.pi / 2 + theta),
            R * np.sin(i * 2 * np.pi / N + np.pi / 2 + theta),
        ]
        for i in range(N)
    ]


# 两两连接所有点
def connect_all(points, color="g"):
    fig = go.Figure()
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            fig.add_trace(
                go.Scatter(
                    x=[points[i][0], points[j][0]],
                    y=[points[i][1], points[j][1]],
                    mode="lines",
                    line=dict(color=color),
                )
            )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 带点两两连接所有点
def connect_all_with_points(points, colorp="b", colorl="g"):
    fig = go.Figure()
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            fig.add_trace(
                go.Scatter(
                    x=[points[i][0], points[j][0]],
                    y=[points[i][1], points[j][1]],
                    mode="lines",
                    line=dict(color=colorl),
                )
            )
    for i in range(len(points)):
        fig.add_trace(
            go.Scatter(
                x=[points[i][0]],
                y=[points[i][1]],
                mode="markers",
                marker=dict(color=colorp),
            )
        )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 首尾连接
def connect(points, color="g"):
    fig = go.Figure()
    num = len(points)
    for i in range(-1, num - 1):
        fig.add_trace(
            go.Scatter(
                x=[points[i][0], points[i + 1][0]],
                y=[points[i][1], points[i + 1][1]],
                mode="lines",
                line=dict(color=color),
            )
        )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 按顺序连接
def connect_in_order(points, color="g"):
    fig = go.Figure()
    num = len(points)
    for i in range(0, num - 1):
        fig.add_trace(
            go.Scatter(
                x=[points[i][0], points[i + 1][0]],
                y=[points[i][1], points[i + 1][1]],
                mode="lines",
                line=dict(color=color),
            )
        )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 带点首尾连接
def connect_with_points(points, colorp="b", colorl="g"):
    fig = go.Figure()
    num = len(points)
    for i in range(-1, num - 1):
        fig.add_trace(
            go.Scatter(
                x=[points[i][0], points[i + 1][0]],
                y=[points[i][1], points[i + 1][1]],
                mode="lines",
                line=dict(color=colorl),
            )
        )
    for i in range(len(points)):
        fig.add_trace(
            go.Scatter(
                x=[points[i][0]],
                y=[points[i][1]],
                mode="markers",
                marker=dict(color=colorp),
            )
        )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 多重多边形
def multi_polygon(n, m, color="b", alpha=0, theta=0):
    fig = go.Figure()
    for i in range(m):
        points = n_points(
            n, (np.cos(np.pi / n)) ** (-i), alpha + i * (np.pi / n + theta)
        )
        sub_fig = connect(points, color)
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 类梅塔特隆立方体连接
def connect_like_metatron(n, m, color="b", theta=0):
    fig = go.Figure()
    points = []
    for i in range(m):
        points += n_points(n, i + 1, theta)
    sub_fig = connect_all(points, color)
    fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 卍字连接
def draw_swastika(n, R, theta=0, color="b"):
    fig = go.Figure()
    if n == 2:
        for i in range(4):
            fig.add_trace(
                go.Scatter(
                    x=[
                        R * np.sqrt(2) ** (n - 2) * np.cos(i * 2 * np.pi / 4 + theta),
                        0,
                    ],
                    y=[
                        R * np.sqrt(2) ** (n - 2) * np.sin(i * 2 * np.pi / 4 + theta),
                        0,
                    ],
                    mode="lines",
                    line=dict(color=color),
                )
            )
    elif n % 2 == 1:
        for i in range(4):
            fig.add_trace(
                go.Scatter(
                    x=[
                        R * np.sqrt(2) ** (n - 3) * np.cos(i * 2 * np.pi / 4 + theta),
                        0,
                    ],
                    y=[
                        R * np.sqrt(2) ** (n - 3) * np.sin(i * 2 * np.pi / 4 + theta),
                        0,
                    ],
                    mode="lines",
                    line=dict(color=color),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=[
                        R
                        * np.sqrt(2) ** (n - 2)
                        * np.cos(i * 2 * np.pi / 4 + np.pi / 4 + theta),
                        0,
                    ],
                    y=[
                        R
                        * np.sqrt(2) ** (n - 2)
                        * np.sin(i * 2 * np.pi / 4 + np.pi / 4 + theta),
                        0,
                    ],
                    mode="lines",
                    line=dict(color=color),
                )
            )
    else:
        for i in range(4):
            fig.add_trace(
                go.Scatter(
                    x=[
                        R * np.sqrt(2) ** (n - 2) * np.cos(i * 2 * np.pi / 4 + theta),
                        0,
                    ],
                    y=[
                        R * np.sqrt(2) ** (n - 2) * np.sin(i * 2 * np.pi / 4 + theta),
                        0,
                    ],
                    mode="lines",
                    line=dict(color=color),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=[
                        R
                        * np.sqrt(2) ** (n - 3)
                        * np.cos(i * 2 * np.pi / 4 + np.pi / 4 + theta),
                        0,
                    ],
                    y=[
                        R
                        * np.sqrt(2) ** (n - 3)
                        * np.sin(i * 2 * np.pi / 4 + np.pi / 4 + theta),
                        0,
                    ],
                    mode="lines",
                    line=dict(color=color),
                )
            )
    for i in range(4):
        points = swastika(n, R, i * 2 * np.pi / 4 + theta)
        fig.add_trace(
            go.Scatter(
                x=[p[0] for p in points],
                y=[p[1] for p in points],
                mode="lines",
                line=dict(color=color),
            )
        )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 多重卍字连接
def draw_swastikas(n, R, m, color="b", theta=0):
    fig = go.Figure()
    for i in range(m):
        sub_fig = draw_swastika(n, R, i * np.pi / m + theta, color)
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig
