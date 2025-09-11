import plotly.graph_objects as go
import numpy as np
import sys

sys.path.append("./circle.py")


"""this is a circle source
这是圈的注释
"""
# 基础工具(Basic_Tools)

"""
圈(Circles)
"""


def circle(center, radius, color="blue"):
    angle = np.linspace(0, 2 * np.pi, 10000)
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


def circle_p(center, point, color="b"):
    # 计算圆的半径
    radius = np.sqrt((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2)
    # 生成圆上的点
    theta = np.linspace(0, 2 * np.pi, 10000)
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    # 绘制图形
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 同心圆
# 等差
# 双向


def ConcentricCircles(center, n, d, radius, color="b"):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=[center[0]], y=[center[1]], mode="lines", line=dict(color=color))
    )
    for i in range(n):
        fig.add_traces(circle(center, radius - i * d, color).data)
        fig.add_traces(circle(center, radius + i * d, color).data)
    fig.add_traces(circle(center, radius, color).data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 向外


def ConcentricCircles_o(center, n, d, radius, color="blue"):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=[center[0]], y=[center[1]], mode="lines", line=dict(color=color))
    )
    for i in range(n):
        angle = np.linspace(0, 2 * np.pi, 100000)
        x = center[0] + (radius + d * i) * np.cos(angle)
        y = center[1] + (radius + d * i) * np.sin(angle)
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 向内


def ConcentricCircles_i(center, n, d, radius, color="blue"):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=[center[0]], y=[center[1]], mode="lines", line=dict(color=color))
    )
    for i in range(n):
        angle = np.linspace(0, 2 * np.pi, 100000)
        x_i = center[0] + (radius - d * i) * np.cos(angle)
        y_i = center[1] + (radius - d * i) * np.sin(angle)
        fig.add_trace(go.Scatter(x=x_i, y=y_i, mode="lines", line=dict(color=color)))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 等比数列
# 双向


def ConcentricCircles_Pro(center, n, q, radius, color="b"):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=[center[0]], y=[center[1]], mode="lines", line=dict(color=color))
    )
    for i in range(n):
        fig.add_traces(circle(center, radius / (q**i), color).data)
        fig.add_traces(circle(center, radius * (q**i), color).data)
    fig.add_traces(circle(center, radius, color).data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 向外


def ConcentricCircles_Pro_o(center, n, q, radius, color="blue"):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=[center[0]], y=[center[1]], mode="lines", line=dict(color=color))
    )
    for i in range(n):
        angle = np.linspace(0, 2 * np.pi, 100000)
        x = center[0] + radius * (q**i) * np.cos(angle)
        y = center[1] + radius * (q**i) * np.sin(angle)
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


def ConcentricCircles_Pro_i(center, n, q, radius, color="blue"):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=[center[0]], y=[center[1]], mode="lines", line=dict(color=color))
    )
    for i in range(n):
        angle = np.linspace(0, 2 * np.pi, 100000)
        x = center[0] + radius / (q**i) * np.cos(angle)
        y = center[1] + radius / (q**i) * np.sin(angle)
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 向内


def ConcentricCircles_Pro_i(center, n, q, radius, color="b"):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=[center[0]], y=[center[1]], mode="lines", line=dict(color=color))
    )
    for i in range(n):
        fig.add_traces(circle(center, radius / (q**i), color).data)
    fig.add_traces(circle(center, radius, color).data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig
