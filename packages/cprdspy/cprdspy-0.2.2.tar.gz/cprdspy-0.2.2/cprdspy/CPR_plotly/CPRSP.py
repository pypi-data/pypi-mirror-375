import plotly.graph_objects as go
import numpy as np
import sys

sys.path.append("./CPRSP.py")

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
        go.Scatter(
            x=[center[0]], y=[center[1]], mode="markers", marker=dict(color=color)
        )
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
        go.Scatter(
            x=[center[0]], y=[center[1]], mode="markers", marker=dict(color=color)
        )
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
        go.Scatter(
            x=[center[0]], y=[center[1]], mode="markers", marker=dict(color=color)
        )
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
        go.Scatter(
            x=[center[0]], y=[center[1]], mode="markers", marker=dict(color=color)
        )
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
        go.Scatter(
            x=[center[0]], y=[center[1]], mode="markers", marker=dict(color=color)
        )
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
        go.Scatter(
            x=[center[0]], y=[center[1]], mode="markers", marker=dict(color=color)
        )
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
        go.Scatter(
            x=[center[0]], y=[center[1]], mode="markers", marker=dict(color=color)
        )
    )
    for i in range(n):
        fig.add_traces(circle(center, radius / (q**i), color).data)
    fig.add_traces(circle(center, radius, color).data)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


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


"""弧(Arcs)
"""
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


def flowers_flower_by_petal_fill_data(
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
