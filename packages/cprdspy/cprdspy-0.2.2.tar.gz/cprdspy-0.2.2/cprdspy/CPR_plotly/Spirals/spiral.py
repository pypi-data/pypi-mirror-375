import plotly.graph_objects as go
import numpy as np
from ..Circles.circle import *
import sys

sys.path.append("./spiral.py")


# 罗丹线圈
def rodincoil(R, r, n, color="b", theta=0):
    fig = go.Figure()
    for i in range(0, n):
        sub_fig = circle(
            (
                R * np.cos(i * 2 * np.pi / n + theta),
                R * np.sin(i * 2 * np.pi / n + theta),
            ),
            r,
            color,
        )
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 罗丹线圈带颜色
def rodincoil_colorful(R, r, n, colors, theta=0):
    fig = go.Figure()
    for i in range(0, n):
        sub_fig = circle(
            (
                R * np.cos(i * 2 * np.pi / n + theta),
                R * np.sin(i * 2 * np.pi / n + theta),
            ),
            r,
            colors[i],
        )
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 螺旋线
def logSpiral(n, a, b, cyc, color="b", theta=0):
    t = np.linspace(-cyc * 2 * np.pi, cyc * 2 * np.pi, 10000)
    x = a * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.cos(t + theta)
    y = b * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.sin(t + theta)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 向外螺旋线
def logSpiral_out(n, a, b, cyc, color="b", theta=0):
    t = np.linspace(0, cyc * 2 * np.pi, 10000)
    x = a * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.cos(t + theta)
    y = b * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.sin(t + theta)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 向内螺旋线
def logSpiral_in(n, a, b, cyc, color="b", theta=0):
    t = np.linspace(0, -cyc * 2 * np.pi, 10000)
    x = a * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.cos(t + theta)
    y = b * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.sin(t + theta)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 多重螺旋线
def n_spiral(n, cyc, color, theta=0):
    fig = go.Figure()
    for i in range(n):
        sub_fig1 = logSpiral(n, 1, 1, cyc, color, theta + i * 2 * np.pi / n)
        sub_fig2 = logSpiral(n, -1, 1, cyc, color, theta + i * 2 * np.pi / n)
        fig.add_traces(sub_fig1.data)
        fig.add_traces(sub_fig2.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 旋转螺旋线
def n_spiral_rotate(n, cyc, color, alpha=0, theta=0):
    fig = go.Figure()
    for i in range(n):
        sub_fig1 = logSpiral(n, 1, 1, cyc, color, alpha + theta + i * 2 * np.pi / n)
        sub_fig2 = logSpiral(n, -1, 1, cyc, color, alpha - theta + i * 2 * np.pi / n)
        fig.add_traces(sub_fig1.data)
        fig.add_traces(sub_fig2.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 向外旋转螺旋线
def n_spiral_rotate_out(n, cyc, color, theta=0):
    fig = go.Figure()
    for i in range(n):
        sub_fig1 = logSpiral_out(n, 1, 1, cyc, color, theta + i * 2 * np.pi / n)
        sub_fig2 = logSpiral_out(n, -1, 1, cyc, color, -theta + i * 2 * np.pi / n)
        fig.add_traces(sub_fig1.data)
        fig.add_traces(sub_fig2.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 向内旋转螺旋线
def n_spiral_rotate_in(n, cyc, color, theta=0):
    fig = go.Figure()
    for i in range(n):
        sub_fig1 = logSpiral_in(n, 1, 1, cyc, color, theta + i * 2 * np.pi / n)
        sub_fig2 = logSpiral_in(n, -1, 1, cyc, color, -theta + i * 2 * np.pi / n)
        fig.add_traces(sub_fig1.data)
        fig.add_traces(sub_fig2.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 画花算法
def calla_petal(n, cyc, theta, color):
    fig = go.Figure()
    sub_fig1 = logSpiral(n, 1, 1, cyc * 1.25, color, theta)
    sub_fig2 = logSpiral(n, -1, 1, cyc * 1.25, color, -theta)
    fig.add_traces(sub_fig1.data)
    fig.add_traces(sub_fig2.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


def calla_by_petal(n, cyc, N, theta, colors):
    fig = go.Figure()
    for i in range(N):
        sub_fig = calla_petal(n, cyc, theta + i * 2 * np.pi / N, colors[i])
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig
