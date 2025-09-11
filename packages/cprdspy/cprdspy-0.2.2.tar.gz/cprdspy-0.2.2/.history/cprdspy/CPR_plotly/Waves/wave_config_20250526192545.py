import plotly.graph_objects as go
import numpy as np
from ..Circles.circle import *
import sys

sys.path.append("./wave.py")
"""
波(Waves)
"""

# 圈上波

# 等差

# 向外


def wave_circle_ari_o(A, F, P, color, theta=0, R=1):
    fig = ConcentricCircles_o((0, 0), F, A, R, "g")
    for i in range(P + 1):
        sub_fig = ConcentricCircles_o(
            (
                np.cos(i * 2 * np.pi / P + np.pi / 2 + theta),
                np.sin(i * 2 * np.pi / P + np.pi / 2 + theta),
            ),
            F,
            A,
            R,
            color,
        )
        fig.add_traces(sub_fig.data)
    fig.update_layout(showlegend=False)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 向内


def wave_circle_ari_i(A, F, P, color, theta=0, R=1):
    fig = ConcentricCircles_i((0, 0), F, A, R, "g")
    for i in range(P + 1):
        sub_fig = ConcentricCircles_i(
            (
                np.cos(i * 2 * np.pi / P + np.pi / 2 + theta),
                np.sin(i * 2 * np.pi / P + np.pi / 2 + theta),
            ),
            F,
            A,
            R,
            color,
        )
        fig.add_traces(sub_fig.data)
    fig.update_layout(showlegend=False)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 双向


def wave_circle_ari(A, F, P, color, theta=0, R=1):
    fig = ConcentricCircles((0, 0), F, A, R, "g")
    for i in range(P + 1):
        sub_fig = ConcentricCircles(
            (
                np.cos(i * 2 * np.pi / P + np.pi / 2 + theta),
                np.sin(i * 2 * np.pi / P + np.pi / 2 + theta),
            ),
            F,
            A,
            R,
            color,
        )
        fig.add_traces(sub_fig.data)
    fig.update_layout(showlegend=False)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 等比

# 向外


def wave_circle_pro_o(A, F, P, color, theta=0, R=1):
    fig = ConcentricCircles_Pro_o((0, 0), F, np.sqrt(A), R, color)
    for i in range(P + 1):
        sub_fig = ConcentricCircles_Pro_o(
            (
                (np.cos(i * 2 * np.pi / P + np.pi / 2 + theta)),
                np.sin(i * 2 * np.pi / P + np.pi / 2 + theta),
            ),
            F,
            np.sqrt(A),
            R,
            color,
        )
        fig.add_traces(sub_fig.data)
    fig.update_layout(showlegend=False)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 向内


def wave_circle_pro_i(A, F, P, color, theta=0, R=1):
    fig = ConcentricCircles_Pro_i((0, 0), F, np.sqrt(A), R, color)
    for i in range(P + 1):
        sub_fig = ConcentricCircles_Pro_i(
            (
                (np.cos(i * 2 * np.pi / P + np.pi / 2 + theta)),
                np.sin(i * 2 * np.pi / P + np.pi / 2 + theta),
            ),
            F,
            np.sqrt(A),
            R,
            color,
        )
        fig.add_traces(sub_fig.data)
    fig.update_layout(showlegend=False)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 双向


def wave_circle_pro(A, F, P, color, theta=0, R=1):
    fig = ConcentricCircles_Pro((0, 0), F, np.sqrt(A), R, color)
    for i in range(P + 1):
        sub_fig = ConcentricCircles_Pro(
            (
                (np.cos(i * 2 * np.pi / P + np.pi / 2 + theta)),
                np.sin(i * 2 * np.pi / P + np.pi / 2 + theta),
            ),
            F,
            np.sqrt(A),
            R,
            color,
        )
        fig.add_traces(sub_fig.data)
    fig.update_layout(showlegend=False)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig
