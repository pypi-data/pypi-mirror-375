import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('./CirclePointSourcePure.py')
'''弧(Arcs)
'''
""""""
# 从point1到point2的圆弧
""""""

# 顺时针


def arc(center, point1, point2, color='b'):
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
    t = np.linspace(theta1, theta2, 100)
    x = center[0] + r1 * np.cos(t)
    y = center[1] + r1 * np.sin(t)

    # X,Y轴等长
    plt.axis('equal')
    # 绘制圆弧
    plt.plot(x, y, color)

# 逆时针


def arc_inverse(center, point1, point2, color='b'):
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
    t = np.linspace(theta1, theta2, 100)
    x = center[0] + r1 * np.cos(t)
    y = center[1] + r1 * np.sin(t)

    # X,Y轴等长
    plt.axis('equal')
    # 绘制圆弧
    plt.plot(x, y, color)


"""通过角度画圆弧
"""


def arc_degree(center, radius, angle1, angle2, color='b'):
    if angle1 < angle2:
        angle = np.linspace(angle1, angle2, 1000)
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        plt.axis('equal')
        plt.plot(x, y, color)


def arc_degree_inverse(center, radius, angle1, angle2, color='b'):
    angle = np.linspace(angle2-2*np.pi, angle1, 1000)
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)
    plt.axis('equal')
    plt.plot(x, y, color)

'''带填充的弧(Arcs With Fills)
'''
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
    t = np.linspace(theta1, theta2, 100)
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
    t = np.linspace(theta1, theta2, 100)
    x = center[0] + r1 * np.cos(t)
    y = center[1] + r1 * np.sin(t)

    return [x, y]


"""通过角度画圆弧
"""


def arc_degree_p(center, radius, angle1, angle2):
    if angle1 < angle2:
        angle = np.linspace(angle1, angle2, 1000)
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
    return [x, y]


def arc_degree_p_inverse(center, radius, angle1, angle2):
    angle = np.linspace(angle2-2*np.pi, angle1, 1000)
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)
    return [x, y]

# def oval_arc(a,b,angle1,angle2,angle=0,color='#0f0',alpha=1,center=(0,0),points=1000):
#     theta = np.linspace(angle1, angle2, points)
#     angle_rad = angle
#     x = a * np.cos(theta)  * np.cos(angle_rad)  - b * np.sin(theta)  * np.sin(angle_rad)  + center[0]
#     y = a * np.cos(theta)  * np.sin(angle_rad)  + b * np.sin(theta)  * np.cos(angle_rad)  + center[1]
#     plt.plot(x,y,color=color,alpha=alpha)
#     plt.axis('equal')


def oval_arc(
    a=2,
    b=1,
    angle1=45,
    angle2=135,
    angle=0,
    color="#0f0",
    alpha=1,
    center=(0, 0),
    points=1000,
    linestyle="-",
    linewidth=1,
    label=None,
    marker=None,
    markersize=5,
    markerfacecolor="r",
    markeredgecolor="k",
    markeredgewidth=1,
    ax=None,
    use_degree=True,
    plot=True,
    **kwargs
):
    """
    绘制一段椭圆弧或返回计算得到的 x 和 y 值。

    参数:
        a (float): 椭圆的长轴长度。
        b (float): 椭圆的短轴长度。
        angle1 (float): 弧的起始角度（度或弧度，取决于 use_degree）。
        angle2 (float): 弧的结束角度（度或弧度，取决于 use_degree）。
        angle (float): 椭圆的旋转角度（度或弧度，取决于 use_degree），默认为0。
        color (str): 弧的颜色，默认为绿色("#0f0")。
        alpha (float): 透明度，默认为1（不透明）。
        center (tuple): 椭圆的中心坐标，默认为(0, 0)。
        points (int): 用于绘制弧的点数，默认为1000。
        linestyle (str): 线型，默认为实线("-")。
        linewidth (int): 线宽，默认为1。
        label (str): 图例标签，默认为None。
        marker (str): 标记样式，默认为None。
        markersize (int): 标记大小，默认为5。
        markerfacecolor (str): 标记填充颜色，默认为红色("r")。
        markeredgecolor (str): 标记边缘颜色，默认为黑色("k")。
        markeredgewidth (int): 标记边缘宽度，默认为1。
        ax (matplotlib.axes.Axes): 目标坐标轴，默认为None（使用当前坐标轴）。
        use_degree (bool): 是否使用角度制（True为角度，False为弧度），默认为True。
        plot (bool): 是否绘制图像，默认为True。如果为False，则返回计算得到的 x 和 y 值。
        **kwargs: 其他传递给 plt.plot 的参数。

    返回:
        如果 plot=True:
            matplotlib.lines.Line2D: 绘制的椭圆弧对象。
        如果 plot=False:
            tuple: (x, y) 计算得到的坐标值。
    """
    # 角度转换
    if use_degree:
        angle1_rad = np.deg2rad(angle1)
        angle2_rad = np.deg2rad(angle2)
        angle_rad = np.deg2rad(angle)
    else:
        angle1_rad = angle1
        angle2_rad = angle2
        angle_rad = angle

    # 生成弧上的点
    theta = np.linspace(angle1_rad, angle2_rad, points)
    x = (
        a * np.cos(theta) * np.cos(angle_rad)
        - b * np.sin(theta) * np.sin(angle_rad)
        + center[0]
    )
    y = (
        a * np.cos(theta) * np.sin(angle_rad)
        + b * np.sin(theta) * np.cos(angle_rad)
        + center[1]
    )

    # 如果不绘制图像，直接返回 x 和 y
    if not plot:
        return x, y

    # 获取目标坐标轴
    if ax is None:
        ax = plt.gca()

    # 绘制椭圆弧
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