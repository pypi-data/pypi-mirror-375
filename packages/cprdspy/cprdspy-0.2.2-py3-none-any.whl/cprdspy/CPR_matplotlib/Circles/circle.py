import numpy as np
import matplotlib.pyplot as plt


def circle(
    radius=1,
    color="#0F0",
    alpha=1,
    center=(0, 0),
    points=100,
    linestyle="-",
    linewidth=1,
    label=None,
    marker=None,
    markersize=5,
    markerfacecolor="r",
    markeredgecolor="k",
    markeredgewidth=1,
    ax=None,
    **kwargs
):
    """
    绘制一个圆。

    参数:
        radius (float): 圆的半径，默认为1。
        color (str): 圆的颜色，默认为绿色("#0F0")。
        alpha (float): 透明度，默认为1（不透明）。
        center (tuple): 圆心坐标，默认为(0, 0)。
        points (int): 用于绘制圆的点数，默认为100。
        linestyle (str): 线型，默认为实线("-")。
        linewidth (int): 线宽，默认为1。
        label (str): 图例标签，默认为None。
        marker (str): 标记样式，默认为None。
        markersize (int): 标记大小，默认为5。
        markerfacecolor (str): 标记填充颜色，默认为红色("r")。
        markeredgecolor (str): 标记边缘颜色，默认为黑色("k")。
        markeredgewidth (int): 标记边缘宽度，默认为1。
        ax (matplotlib.axes.Axes): 目标坐标轴，默认为None（使用当前坐标轴）。
        **kwargs: 其他传递给plt.plot的参数。

    返回:
        matplotlib.lines.Line2D: 绘制的圆对象。
    """
    angle = np.linspace(0, 2 * np.pi, points)
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)

    if ax is None:
        ax = plt.gca()

    line = ax.plot(
        x,
        y,
        color=color,
        alpha=alpha,
        linestyle=linestyle,
        linewidth=linewidth,
        label=label,
        marker=marker,
        markersize=markersize,
        markerfacecolor=markerfacecolor,
        markeredgecolor=markeredgecolor,
        markeredgewidth=markeredgewidth,
        **kwargs
    )

    ax.axis("equal")
    return line[0] if line else None

def draw_circle(
    radius=1,
    color="#0F0",
    alpha=1,
    center=(0, 0),
    points=100,
    linestyle="-",
    linewidth=1,
    label=None,
    marker=None,
    markersize=5,
    markerfacecolor="r",
    markeredgecolor="k",
    markeredgewidth=1,
):
    angle = np.linspace(0, 2 * np.pi, points)
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)
    plt.axis("equal")
    plt.plot(
        x,
        y,
        color=color,
        alpha=alpha,
        linestyle=linestyle,
        linewidth=linewidth,
        label=label,
        marker=marker,
        markersize=markersize,
        markerfacecolor=markerfacecolor,
        markeredgecolor=markeredgecolor,
        markeredgewidth=markeredgewidth,
    )

# def circle(center, radius, color='b'):
#     angle = np.linspace(0, 2*np.pi, 1000)
#     x = center[0] + radius * np.cos(angle)
#     y = center[1] + radius * np.sin(angle)
#     plt.axis('equal')
#     plt.plot(x, y, color)


def circle_p(center, point, color='b'):
    # 计算圆的半径
    radius = np.sqrt((point[0] - center[0])
                     ** 2 + (point[1] - center[1]) ** 2)
    # 生成圆上的点
    theta = np.linspace(0, 2 * np.pi, 100)
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    # 绘制图形
    plt.axis('equal')
    plt.plot(x, y, color)

# 椭圆

def ellipse(a, b, angle=0, color='#0f0',alpha=1, center=(0,0), points=1000):
    theta = np.linspace(0,  2*np.pi,  points)
    angle_rad = np.deg2rad(angle) 
    x = a * np.cos(theta)  * np.cos(angle_rad)  - b * np.sin(theta)  * np.sin(angle_rad)  + center[0]
    y = a * np.cos(theta)  * np.sin(angle_rad)  + b * np.sin(theta)  * np.cos(angle_rad)  + center[1]
    plt.plot(x,y,color,alpha)
# 同心圆
# 等差
# 双向


def ConcentricCircles(center, n, d, radius, color='b'):
    plt.plot(center[0], center[1], marker='o', color=color)
    for i in range(n):
        circle(center, radius-i*d, color)
        circle(center, radius+i*d, color)
    circle(center, radius, color)

# 向外


def ConcentricCircles_o(center, n, d, radius, color='b'):
    plt.plot(center[0], center[1], marker='o', color=color)
    for i in range(n):
        circle(center, radius+d*i, color)
    circle(center, radius, color)

# 向内


def ConcentricCircles_i(center, n, d, radius, color='b'):
    plt.plot(center[0], center[1], marker='o', color=color)
    for i in range(n):
        circle(center, radius-d*i, color)
    circle(center, radius, color)

# 等比数列
# 双向


def ConcentricCircles_Pro(center, n, q, radius, color='b'):
    plt.plot(center[0], center[1], marker='o', color=color)
    for i in range(n):
        circle(center, radius/(q**i), color)
        circle(center, radius*(q**i), color)
    circle(center, radius, color)

# 向外


def ConcentricCircles_Pro_o(center, n, q, radius, color='b'):
    plt.plot(center[0], center[1], marker='o', color=color)
    for i in range(n):
        circle(center, radius*(q**i), color)
    circle(center, radius, color)

# 向内


def ConcentricCircles_Pro_i(center, n, q, radius, color='b'):
    plt.plot(center[0], center[1], marker='o', color=color)
    for i in range(n):
        circle(center, radius/(q**i), color)
    circle(center, radius, color)
