import numpy as np
import plotly.graph_objects as go
from ..Arcs.arc import *
import sys

sys.path.append("./flowers.py")

"""
画花算法(Flower Drawing Algorithm)
"""

"""_summary_: 画空心花(Draw Hollow Flowers)
"""


# 花瓣


def n_flower_petal(center, R, r, n, theta=0, color="b"):
    alpha = 2 * np.pi / n
    a = R * np.sin(np.pi / n)
    beta = np.arccos((a) / r)
    theta_arc = np.pi / 2 - np.pi / n + np.arccos((a) / r)
    theta_petal = 2 * theta_arc
    center1 = (
        np.cos(theta + alpha / 2) * R + center[0],
        np.sin(theta + alpha / 2) * R + center[1],
    )
    center2 = (
        np.cos(theta + alpha / 2 - 2 * np.pi / n) * R + center[0],
        np.sin(theta + alpha / 2 - 2 * np.pi / n) * R + center[1],
    )
    fig = go.Figure()
    if abs(r - a) < 1e-12:
        arc1 = arc_degree_p(
            center1, r, np.pi + alpha / 2 + theta, np.pi + alpha / 2 + theta + theta_arc
        )
        arc2 = arc_degree_p(
            center2, r, np.pi / 2 + theta, np.pi / 2 + theta + theta_arc
        )
    elif r > a:
        arc1 = arc_degree_p(
            center1, r, np.pi + alpha / 2 + theta, np.pi + alpha / 2 + theta + theta_arc
        )
        arc2 = arc_degree_p(
            center2, r, np.pi / 2 - beta + theta, np.pi / 2 - beta + theta + theta_arc
        )
    else:
        print("r=", r, ",a=", a)
        print("r<a,不能形成花瓣。")
        return fig
    fig.add_trace(
        go.Scatter(x=arc1[0], y=arc1[1], mode="lines", line=dict(color=color))
    )
    fig.add_trace(
        go.Scatter(x=arc2[0], y=arc2[1], mode="lines", line=dict(color=color))
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 花弧


def n_flower_arc(center, R, r, n, theta=0, color="b"):
    alpha = 2 * np.pi / n
    a = R * np.sin(np.pi / n)
    beta = np.arccos((a) / r)
    theta_arc = np.pi / 2 - np.pi / n + np.arccos((a) / r)
    theta_petal = 2 * theta_arc
    center1 = (
        np.cos(theta + alpha / 2) * R + center[0],
        np.sin(theta + alpha / 2) * R + center[1],
    )
    center2 = (
        np.cos(theta + alpha / 2 - 2 * np.pi / n) * R + center[0],
        np.sin(theta + alpha / 2 - 2 * np.pi / n) * R + center[1],
    )
    fig = go.Figure()
    if abs(r - a) < 1e-12:
        arc1 = arc_degree_p(
            center1,
            r,
            np.pi / 2 + alpha + theta,
            np.pi / 2 + alpha + theta + theta_petal,
        )
        arc2 = arc_degree_p(
            center2, r, np.pi / 2 + theta, np.pi / 2 + theta + theta_petal
        )
    elif r > a:
        arc1 = arc_degree_p(
            center1,
            r,
            np.pi / 2 + alpha - beta + theta,
            np.pi / 2 + alpha - beta + theta + theta_petal,
        )
        arc2 = arc_degree_p(
            center2, r, np.pi / 2 - beta + theta, np.pi / 2 - beta + theta + theta_petal
        )
    else:
        print("r=", r, ",a=", a)
        print("r<a,不能形成花瓣。")
        return fig
    fig.add_trace(
        go.Scatter(x=arc1[0], y=arc1[1], mode="lines", line=dict(color=color))
    )
    fig.add_trace(
        go.Scatter(x=arc2[0], y=arc2[1], mode="lines", line=dict(color=color))
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 带场花弧


def n_flowers_flower_arc_with_field(
    center, R, r, n, theta=0, color="b", colorfield="#ff0"
):
    alpha = 2 * np.pi / n
    a = R * np.sin(np.pi / n)
    beta = np.arccos((a) / r)
    theta_arc = np.pi / 2 - np.pi / n + np.arccos((a) / r)
    theta_petal = 2 * theta_arc
    center1 = (
        np.cos(theta + alpha / 2) * R + center[0],
        np.sin(theta + alpha / 2) * R + center[1],
    )
    center2 = (
        np.cos(theta + alpha / 2 - 2 * np.pi / n) * R + center[0],
        np.sin(theta + alpha / 2 - 2 * np.pi / n) * R + center[1],
    )
    fig = go.Figure()
    if abs(r - a) < 1e-12:
        arc1 = arc_degree_p(
            center1,
            r,
            np.pi / 2 + alpha + theta,
            np.pi / 2 + alpha + theta + theta_petal,
        )
        arc2 = arc_degree_p(
            center2, r, np.pi / 2 + theta, np.pi / 2 + theta + theta_petal
        )
        arc1_inv = arc_degree_p_inverse(
            center1,
            r,
            np.pi / 2 + alpha + theta,
            np.pi / 2 + alpha + theta + theta_petal,
        )
        arc2_inv = arc_degree_p_inverse(
            center2, r, np.pi / 2 + theta, np.pi / 2 + theta + theta_petal
        )
    elif r > a:
        arc1 = arc_degree_p(
            center1,
            r,
            np.pi / 2 + alpha - beta + theta,
            np.pi / 2 + alpha - beta + theta + theta_petal,
        )
        arc2 = arc_degree_p(
            center2, r, np.pi / 2 - beta + theta, np.pi / 2 - beta + theta + theta_petal
        )
        arc1_inv = arc_degree_p_inverse(
            center1,
            r,
            np.pi / 2 + alpha - beta + theta,
            np.pi / 2 + alpha - beta + theta + theta_petal,
        )
        arc2_inv = arc_degree_p_inverse(
            center2, r, np.pi / 2 - beta + theta, np.pi / 2 - beta + theta + theta_petal
        )
    else:
        print("r=", r, ",a=", a)
        print("r<a,不能形成花瓣。")
        return fig
    fig.add_trace(
        go.Scatter(x=arc1[0], y=arc1[1], mode="lines", line=dict(color=color))
    )
    fig.add_trace(
        go.Scatter(x=arc2[0], y=arc2[1], mode="lines", line=dict(color=color))
    )
    fig.add_trace(
        go.Scatter(
            x=arc1_inv[0], y=arc1_inv[1], mode="lines", line=dict(color=colorfield)
        )
    )
    fig.add_trace(
        go.Scatter(
            x=arc2_inv[0], y=arc2_inv[1], mode="lines", line=dict(color=colorfield)
        )
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 一朵向上花瓣


def one_flower_petal(center, R, r, n, theta=0, color="b"):
    return n_flower_petal(center, R, r, n, theta + np.pi / 2, color)


# 一朵向上花弧


def one_flower_arc(center, R, r, n, theta=0, color="b"):
    return n_flower_arc(center, R, r, n, theta + np.pi / 2, color)


# 一朵向上花瓣场


def one_flower_flower_arc_with_field(
    center, R, r, n, theta=0, color="b", colorfield="#ff0"
):
    return n_flowers_flower_arc_with_field(
        center, R, r, n, theta + np.pi / 2, color, colorfield
    )


# 花瓣形成的单层花


def flowers_flower_by_petal(center, R, r, N, n, theta, color="b"):
    fig = go.Figure()
    for i in range(0, N):
        sub_fig = one_flower_petal(center, R, r, n, 2 * i * np.pi / N + theta, color)
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 花弧形成的单层花


def flowers_flower_by_arc(center, R, r, N, n, theta, color="b"):
    fig = go.Figure()
    for i in range(0, N):
        sub_fig = one_flower_arc(center, R, r, n, 2 * i * np.pi / N + theta, color)
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 单层花带场


def flowers_flower_by_flower_arc_with_field(
    center, R, r, N, n, theta, color="b", colorfield="#ff0"
):
    fig = go.Figure()
    for i in range(0, N):
        sub_fig = one_flower_flower_arc_with_field(
            center, R, r, n, 2 * i * np.pi / N + theta, color, colorfield
        )
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 花瓣形成的多层花


def flowers_flower_by_petal_multi(center, R, r, n, ratio, M, N, theta, color="b"):
    fig = go.Figure()
    for j in range(1, M + 1):
        for i in range(0, N):
            sub_fig = one_flower_petal(
                center,
                R * (ratio ** (j - 1)),
                r * (ratio ** (j - 1)),
                n,
                2 * i * np.pi / N + (j - 1) * np.pi / N + theta,
                color,
            )
            fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 带填充的花瓣形成的花


def one_petal_fill(center, r, n, theta, colorf="r", color="b"):
    return n_lily_petal_fill(center, r, n, theta + np.pi / 2, colorf, color)


def one_layer_flower_by_petal_fill(center, R, n, theta, colorf="r", color="b"):
    fig = go.Figure()
    for i in range(0, n):
        sub_fig = one_petal_fill(center, R, n, 2 * i * np.pi / n + theta, colorf, color)
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


def flower_by_petal_fill(center, r, M, N, n, theta, colorf="r", color="b"):
    fig = go.Figure()
    for j in range(1, M + 1):
        for i in range(0, N):
            sub_fig = one_petal_fill(
                center,
                (np.sqrt(2 * np.cos(np.pi / n)) ** (2 * j - 1) * r),
                n,
                2 * i * np.pi / N + (j - 1) * np.pi / N + theta,
                colorf,
                color,
            )
            fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 一朵向上花瓣带填充


def one_flower_petal_fill(center, R, r, n, theta=0, colorf="r", color="b", alpha=0.5):
    return n_flowers_petal_fill(
        center, R, r, n, theta + np.pi / 2, colorf, color, alpha
    )


# 花瓣形成的单层花带填充


def flowers_flower_by_petal_fill(
    center, R, r, N, n, theta, colorf="r", color="b", alpha=0.5
):
    fig = go.Figure()
    for i in range(0, N):
        sub_fig = one_flower_petal_fill(
            center, R, r, n, 2 * i * np.pi / N + theta, colorf, color, alpha
        )
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 带填充的花瓣
def n_lily_petal_fill(center, r, n, theta, colorf="b", color="r", alpha=0.1):
    alpha = np.pi / n
    beta = np.pi - np.pi / n
    center1 = (
        np.cos(theta + alpha) * r + center[0],
        np.sin(theta + alpha) * r + center[1],
    )
    center2 = (
        np.cos(theta + alpha - 2 * np.pi / n) * r + center[0],
        np.sin(theta + alpha - 2 * np.pi / n) * r + center[1],
    )
    arc = arc_degree_p(
        center1, r, alpha + np.pi + theta, alpha + np.pi + theta + np.pi * (n - 2) / n
    )
    arc_inverse = arc_degree_p_inverse(
        center2, r, beta + theta, beta + theta + np.pi * (n + 2) / n
    )
    x = arc[0]
    y = arc[1]
    x1 = arc_inverse[0]
    y1 = arc_inverse[1]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            fill="toself",
            fillcolor=colorf,
            line=dict(color=color, width=alpha),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x1,
            y=y1,
            fill="toself",
            fillcolor=colorf,
            line=dict(color=color, width=alpha),
        )
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


def n_flowers_petal_fill(center, R, r, n, theta=0, colorf="b", color="r", alpha=0.1):
    alpha = 2 * np.pi / n
    a = R * np.sin(np.pi / n)
    beta = np.arccos((a) / r)
    theta_arc = np.pi / 2 - np.pi / n + np.arccos((a) / r)
    theta_petal = 2 * theta_arc
    center1 = (
        np.cos(theta + alpha / 2) * R + center[0],
        np.sin(theta + alpha / 2) * R + center[1],
    )
    center2 = (
        np.cos(theta + alpha / 2 - 2 * np.pi / n) * R + center[0],
        np.sin(theta + alpha / 2 - 2 * np.pi / n) * R + center[1],
    )
    if abs(r - a) < 1e-12:
        arc = arc_degree_p(
            center1, r, np.pi + alpha / 2 + theta, np.pi + alpha / 2 + theta + theta_arc
        )
        arc_inverse = arc_degree_p(
            center2, r, np.pi / 2 + theta, np.pi / 2 + theta + theta_arc
        )
    elif r > a:
        arc = arc_degree_p(
            center1, r, np.pi + alpha / 2 + theta, np.pi + alpha / 2 + theta + theta_arc
        )
        arc_inverse = arc_degree_p(
            center2, r, np.pi / 2 - beta + theta, np.pi / 2 - beta + theta + theta_arc
        )
    elif r < a:
        print("r=", r, ",a=", a)
        print("r<a,不能形成花瓣。")
        return go.Figure()
    x1 = arc[0]
    y1 = arc[1]
    x2 = arc_inverse[0]
    y2 = arc_inverse[1]
    merged_x = np.concatenate((x1, x2))
    merged_y = np.concatenate((y1, y2))
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=merged_x,
            y=merged_y,
            fill="toself",
            fillcolor=colorf,
            line=dict(color=color, width=alpha),
        )
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 带填充的花瓣形成的花
def one_petal_fill(center, r, n, theta, colorf="r", color="b"):
    return n_lily_petal_fill(center, r, n, theta + np.pi / 2, colorf, color)


def one_layer_flower_by_petal_fill(center, R, n, theta, colorf="r", color="b"):
    fig = go.Figure()
    for i in range(0, n):
        sub_fig = one_petal_fill(center, R, n, 2 * i * np.pi / n + theta, colorf, color)
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


def flower_by_petal_fill(center, r, M, N, n, theta, colorf="r", color="b"):
    fig = go.Figure()
    for j in range(1, M + 1):
        for i in range(0, N):
            sub_fig = one_petal_fill(
                center,
                (np.sqrt(2 * np.cos(np.pi / n)) ** (2 * j - 1) * r),
                n,
                2 * i * np.pi / N + (j - 1) * np.pi / N + theta,
                colorf,
                color,
            )
            fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 一朵向上花瓣带填充
def one_flower_petal_fill(center, R, r, n, theta=0, colorf="r", color="b", alpha=0.5):
    return n_flowers_petal_fill(
        center, R, r, n, theta + np.pi / 2, colorf, color, alpha
    )


# 花瓣形成的单层花带填充
def flowers_flower_by_petal_fill(
    center, R, r, N, n, theta, colorf="r", color="b", alpha=0.5
):
    fig = go.Figure()
    for i in range(0, N):
        sub_fig = one_flower_petal_fill(
            center, R, r, n, 2 * i * np.pi / N + theta, colorf, color, alpha
        )
        fig.add_traces(sub_fig.data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 花弧
def n_flowers_arc_p(center, R, r, n, theta=0):
    alpha = 2 * np.pi / n
    a = R * np.sin(np.pi / n)
    beta = np.arccos((a) / r)
    theta_arc = np.pi / 2 - np.pi / n + np.arccos((a) / r)
    theta_petal = 2 * theta_arc
    center1 = (
        np.cos(theta + alpha / 2) * R + center[0],
        np.sin(theta + alpha / 2) * R + center[1],
    )
    center2 = (
        np.cos(theta + alpha / 2 - 2 * np.pi / n) * R + center[0],
        np.sin(theta + alpha / 2 - 2 * np.pi / n) * R + center[1],
    )
    if abs(r - a) < 1e-12:
        arc1 = arc_degree_p(
            center1,
            r,
            np.pi / 2 + alpha + theta,
            np.pi / 2 + alpha + theta + theta_petal,
        )
        arc2 = arc_degree_p(
            center2, r, np.pi / 2 + theta, np.pi / 2 + theta + theta_petal
        )
    elif r > a:
        arc1 = arc_degree_p(
            center1,
            r,
            np.pi / 2 + alpha - beta + theta,
            np.pi / 2 + alpha - beta + theta + theta_petal,
        )
        arc2 = arc_degree_p(
            center2, r, np.pi / 2 - beta + theta, np.pi / 2 - beta + theta + theta_petal
        )
    else:
        print("r=", r, ",a=", a)
        print("r<a,不能形成花瓣。")
        return [[], []]
    x1 = arc1[0]
    y1 = arc1[1]
    x2 = arc2[0]
    y2 = arc2[1]
    merged_x = np.concatenate((x1, x2))
    merged_y = np.concatenate((y1, y2))
    return [merged_x, merged_y]


# flowers_flower_by_petal_multi((0, 0), 1, 1, 6, np.sqrt(2.5), 3, 12, 0, "#0f0")
