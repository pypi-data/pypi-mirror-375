import numpy as np
import plotly.graph_objects as go
import sys

sys.path.append("./arc.py")

"""弧(Arcs)"""

""""""
# 从point1到point2的圆弧
""""""

# 顺时针


def arc(center, point1, point2, color="blue"):
    vector1 = np.array(point1) - np.array(center)
    vector2 = np.array(point2) - np.array(center)
    r1 = np.linalg.norm(vector1)
    theta1 = np.arctan2(vector1[1], vector1[0])
    theta2 = np.arctan2(vector2[1], vector2[0])

    if theta1 < theta2:
        theta1 += 2 * np.pi

    t = np.linspace(theta1, theta2, 10000)
    x = center[0] + r1 * np.cos(t)
    y = center[1] + r1 * np.sin(t)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# 逆时针


def arc_inverse(center, point1, point2, color="blue"):
    vector1 = np.array(point1) - np.array(center)
    vector2 = np.array(point2) - np.array(center)
    r1 = np.linalg.norm(vector1)
    theta1 = np.arctan2(vector1[1], vector1[0])
    theta2 = np.arctan2(vector2[1], vector2[0])

    if theta2 < theta1:
        theta2 += 2 * np.pi

    t = np.linspace(theta1, theta2, 10000)
    x = center[0] + r1 * np.cos(t)
    y = center[1] + r1 * np.sin(t)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


"""通过角度画圆弧
"""


def arc_degree(center, radius, angle1, angle2, color="b"):
    if angle1 < angle2:
        angle = np.linspace(angle1, angle2, 100000)
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
        fig.update_yaxes(scaleanchor="x", scaleratio=1)
        return fig


def arc_degree_inverse(center, radius, angle1, angle2, color="b"):
    angle = np.linspace(angle2 - 2 * np.pi, angle1, 100000)
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


"""通过角度画圆弧
"""


def flower_arc_degree(center, radius, angle1, angle2, color="b"):
    if angle1 < angle2:
        angle = np.linspace(angle1, angle2, 100000)
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
        fig.update_yaxes(scaleanchor="x", scaleratio=1)
        return fig


def flower_arc_degree_inverse(center, radius, angle1, angle2, color="b"):
    angle = np.linspace(angle2 - 2 * np.pi, angle1, 100000)
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color)))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


"""带填充的弧(Arcs With Fills)
"""
# 顺时针


def arc_dot(center, point1, point2):
    # 计算端点到圆心的向量
    vector1 = np.array(point1) - np.array(center)
    vector2 = np.array(point2) - np.array(center)

    # 计算向量的模长
    r1 = np.linalg.norm(vector1)
    r2 = np.linalg.norm(vector2)

    # 计算向量之间的夹角
    theta1 = np.arctan2(vector1[1], vector1[0])
    theta2 = np.arctan2(vector2[1], vector2[0])

    # 确保 theta2 > theta1
    if theta1 < theta2:
        theta1 += 2 * np.pi

    # 计算圆弧上的点
    t = np.linspace(theta1, theta2, 10000)
    x = center[0] + r1 * np.cos(t)
    y = center[1] + r1 * np.sin(t)

    return [x, y]


# 逆时针


def arc_inverse_dot(center, point1, point2):
    # 计算端点到圆心的向量
    vector1 = np.array(point1) - np.array(center)
    vector2 = np.array(point2) - np.array(center)

    # 计算向量的模长
    r1 = np.linalg.norm(vector1)
    r2 = np.linalg.norm(vector2)

    # 计算向量之间的夹角
    theta1 = np.arctan2(vector1[1], vector1[0])
    theta2 = np.arctan2(vector2[1], vector2[0])

    # 确保 theta2 > theta1
    if theta2 < theta1:
        theta2 += 2 * np.pi

    # 计算圆弧上的点
    t = np.linspace(theta1, theta2, 10000)
    x = center[0] + r1 * np.cos(t)
    y = center[1] + r1 * np.sin(t)

    return [x, y]


"""通过角度画圆弧
"""


def arc_degree_p(center, radius, angle1, angle2):
    if angle1 < angle2:
        angle = np.linspace(angle1, angle2, 100000)
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
    return [x, y]


def arc_degree_p_inverse(center, radius, angle1, angle2):
    angle = np.linspace(angle2 - 2 * np.pi, angle1, 100000)
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)
    return [x, y]
