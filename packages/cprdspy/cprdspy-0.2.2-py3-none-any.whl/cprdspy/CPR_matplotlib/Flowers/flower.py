import matplotlib.pyplot as plt
import numpy as np
from cprdspy.CPR_matplotlib.Arcs.arc import *
import sys

sys.path.append("./CirclePointSourcePure.py")
"""
Flower Arc Algorithm
"""
# 花弧


def n_flower_arc(center, R, r, n, theta=0, color="b"):
    alpha = 2 * np.pi / n
    a = R * np.sin(np.pi / n)
    beta = np.arccos((a) / r)
    theta_arc = np.pi / 2 - np.pi / n + np.arccos((a) / r)
    theta_petal = 2 * theta_arc
    # circle((0, 0), R, 'g')
    # circle((0, 0), R/2, 'g')
    center1 = (
        np.cos(theta + alpha / 2) * R + center[0],
        np.sin(theta + alpha / 2) * R + center[1],
    )
    center2 = (
        np.cos(theta + alpha / 2 - 2 * np.pi / n) * R + center[0],
        np.sin(theta + alpha / 2 - 2 * np.pi / n) * R + center[1],
    )
    if abs(r - a) < 1e-12:
        arc_degree(
            center1,
            r,
            np.pi / 2 + alpha + theta,
            np.pi / 2 + alpha + theta + theta_petal,
            color,
        )
        arc_degree(
            center2, r, np.pi / 2 + theta, np.pi / 2 + theta + theta_petal, color
        )
        if r == R:
            print("r=", r, ",a=", a)
            print("r=a,r=R形成睡莲花弧。")
        elif r > R:
            print("r=", r, ",a=", a)
            print("r=a,r>R形成荷花花弧。")
        elif r < R:
            print("r=", r, ",a=", a)
            print("r=a,r<R形成特殊曼陀罗花弧。")
    elif r > a:
        arc_degree(
            center1,
            r,
            np.pi / 2 + alpha - beta + theta,
            np.pi / 2 + alpha - beta + theta + theta_petal,
            color,
        )
        arc_degree(
            center2,
            r,
            np.pi / 2 - beta + theta,
            np.pi / 2 - beta + theta + theta_petal,
            color,
        )
        if r == R:
            print("r=", r, ",a=", a)
            print("r>a,r=R形成睡莲花弧。")
        elif r > R:
            print("r=", r, ",a=", a)
            print("r>a,r>R形成荷花花弧。")
        elif r < R:
            print("r=", r, ",a=", a)
            print("r>a,r<R形成普通曼陀罗花弧。")
    elif r < a:
        print("r=", r, ",a=", a)
        print("r<a,不能形成花瓣。")
    # plt.plot(center1[0], center1[1], marker='o', color='r')
    # plt.plot(center2[0], center2[1], marker='o', color='b')


def n_flowers_arc_p(center, R, r, n, theta=0):
    alpha = 2 * np.pi / n
    a = R * np.sin(np.pi / n)
    beta = np.arccos((a) / r)
    theta_arc = np.pi / 2 - np.pi / n + np.arccos((a) / r)
    theta_petal = 2 * theta_arc
    # circle((0, 0), R, 'g')
    # circle((0, 0), R/2, 'g')
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
            center1,
            r,
            np.pi / 2 + alpha + theta,
            np.pi / 2 + alpha + theta + theta_petal,
        )
        arc_inverse = arc_degree_p(
            center2, r, np.pi / 2 + theta, np.pi / 2 + theta + theta_petal
        )
    elif r > a:
        arc = arc_degree_p(
            center1,
            r,
            np.pi / 2 + alpha - beta + theta,
            np.pi / 2 + alpha - beta + theta + theta_petal,
        )
        arc_inverse = arc_degree_p(
            center2, r, np.pi / 2 - beta + theta, np.pi / 2 - beta + theta + theta_petal
        )
    elif r < a:
        print("r=", r, ",a=", a)
        print("r<a,不能形成花瓣。")
    # plt.plot(center1[0], center1[1], marker='o', color='r')
    # plt.plot(center2[0], center2[1], marker='o', color='b')
    x1 = arc[0]
    y1 = arc[1]
    x2 = arc_inverse[0]
    y2 = arc_inverse[1]
    merged_x = np.concatenate((x1, x2))
    merged_y = np.concatenate((y1, y2))
    # plt.fill(merged_x, merged_y, colorf)
    # # plt.fill(x1, y1, colorf)
    # # plt.fill(x2, y2, colorf)
    # plt.plot(x1, y1, color, alpha)
    # plt.plot(x2, y2, color, alpha)
    # plt.axis('equal')
    return [merged_x, merged_y]


"""
Flower Petal Algorithm
"""
# 花瓣


def n_flower_petal(center, R, r, n, theta=0, color="b"):
    alpha = 2 * np.pi / n
    a = R * np.sin(np.pi / n)
    beta = np.arccos((a) / r)
    theta_arc = np.pi / 2 - np.pi / n + np.arccos((a) / r)
    theta_petal = 2 * theta_arc
    # circle((0, 0), R, 'g')
    # circle((0, 0), R/2, 'g')
    center1 = (
        np.cos(theta + alpha / 2) * R + center[0],
        np.sin(theta + alpha / 2) * R + center[1],
    )
    center2 = (
        np.cos(theta + alpha / 2 - 2 * np.pi / n) * R + center[0],
        np.sin(theta + alpha / 2 - 2 * np.pi / n) * R + center[1],
    )
    if abs(r - a) < 1e-12:
        arc_degree(
            center1,
            r,
            np.pi + alpha / 2 + theta,
            np.pi + alpha / 2 + theta + theta_arc,
            color,
        )
        arc_degree(
            center2, r, np.pi / 2 + theta, np.pi / 2 + theta + theta_arc, color
        )
        # if r == R:
        #     print("r=", r, ",a=", a)
        #     print('r=a,r=R形成睡莲花瓣。')
        # elif r > R:
        #     print("r=", r, ",a=", a)
        #     print('r=a,r>R形成荷花花瓣。')
        # elif r < R:
        #     print("r=", r, ",a=", a)
        #     print('r=a,r<R形成特殊曼陀罗花瓣。')
    elif r > a:
        arc_degree(
            center1,
            r,
            np.pi + alpha / 2 + theta,
            np.pi + alpha / 2 + theta + theta_arc,
            color,
        )
        arc_degree(
            center2,
            r,
            np.pi / 2 - beta + theta,
            np.pi / 2 - beta + theta + theta_arc,
            color,
        )
        # if r == R:
        #     print("r=", r, ",a=", a)
        #     print('r>a,r=R形成睡莲花瓣。')
        # elif r > R:
        #     print("r=", r, ",a=", a)
        #     print('r>a,r>R形成荷花花瓣。')
        # elif r < R:
        #     print("r=", r, ",a=", a)
        #     print('r>a,r<R形成普通曼陀罗花瓣。')
    elif r < a:
        print("r=", r, ",a=", a)
        print("r<a,不能形成花瓣。")
    # plt.plot(center1[0], center1[1], marker='o', color='r')
    # plt.plot(center2[0], center2[1], marker='o', color='b')


def one_flower_petal(center, R, r, n, theta=0, color="b"):
    n_flower_petal(center, R, r, n, theta + np.pi / 2, color)


# 一朵向上花弧


def one_flower_arc(center, R, r, n, theta=0, color="b"):
    n_flower_arc(center, R, r, n, theta + np.pi / 2, color)


# 一朵向上花瓣场


def one_flower_flower_arc_with_field(
    center, R, r, n, theta=0, color="b", colorfield="#ff0"
):
    n_flowers_flower_arc_with_field(
        center, R, r, n, theta + np.pi / 2, color, colorfield
    )


# 花瓣形成的单层花


def flowers_flower_by_petal(center, R, r, N, n, theta, color="b"):
    for i in range(0, N):
        one_flower_petal(center, R, r, n, 2 * i * np.pi / N + theta, color)


# 花弧形成的单层花


def flowers_flower_by_arc(center, R, r, N, n, theta, color="b"):
    for i in range(0, N):
        one_flower_arc(center, R, r, n, 2 * i * np.pi / N + theta, color)


# 单层花带场


def flowers_flower_by_flower_arc_with_field(
    center, R, r, N, n, theta, color="b", colorfield="#ff0"
):
    for i in range(0, N):
        one_flower_flower_arc_with_field(
            center, R, r, n, 2 * i * np.pi / N + theta, color
        )


# 花瓣形成的多层花


def flowers_flower_by_petal_multi(
    R=1, r=1, n=4, ratio=np.sqrt(2), M=3, N=12, color="b", theta=0, center=(0, 0)
):
    for j in range(1, M + 1):
        for i in range(0, N):
            one_flower_petal(
                center,
                R * (ratio ** (j - 1)),
                r * (ratio ** (j - 1)),
                n,
                2 * i * np.pi / N + (j - 1) * np.pi / N + theta,
                color,
            )


# def oval_petal(a,b,d,rotate_theta=0,color='#0f0',alpha=1,center=(0,0),points=1000):
#     # x0=a/b*np.sqrt(4*(b/d)**2-1)
#     # x0=a/(2*b)*np.sqrt(4*(b)**2-d**2)/(d/2)
#     x0=b/(2*a)*np.sqrt(4*a**2-d**2)/(d/2)
#     # print(x0)
#     beta=np.arctan(x0)
#     beta_b1=np.pi/2-beta
#     beta_e1=np.pi/2+beta
#     beta_b2=3*np.pi/2-beta
#     beta_e2=3*np.pi/2+beta
#     center1=(center[0],center[1]-d/2)
#     center2=(center[0],center[1]+d/2)
#     center1_rot = rotate_point(center1, rotate_theta)
#     center2_rot = rotate_point(center2, rotate_theta)
#     oval_arc(a,b,beta_b1,beta_e1,angle=rotate_theta,color=color,alpha=alpha,center=center1_rot,points=points)
#     oval_arc(a,b,beta_b2,beta_e2,angle=rotate_theta,color=color,alpha=alpha,center=center2_rot,points=points)
#     # print(center1,center2)


def oval_petal_a(
    a, b, d, rotate_theta=0, color="b", alpha=1, center=(0, 0), points=1000
):
    x0 = b / (2 * a) * np.sqrt(4 * a**2 - d**2) / (d / 2)
    # x0=a/(2*b)*np.sqrt(4*(b)**2-d**2)/(d/2)
    beta = np.arctan(x0)
    beta_b1 = np.pi / 2 - beta
    beta_e1 = np.pi / 2 + beta
    beta_b2 = 3 * np.pi / 2 - beta
    beta_e2 = 3 * np.pi / 2 + beta
    center1 = (center[0], center[1] - d / 2)
    center2 = (center[0], center[1] + d / 2)
    center1_rot = rotate_point((a, center[1] - d / 2), rotate_theta)
    center2_rot = rotate_point((a, center[1] + d / 2), rotate_theta)
    oval_arc(
        a,
        b,
        beta_b1,
        beta_e1,
        angle=rotate_theta,
        color=color,
        alpha=alpha,
        center=center1_rot,
        points=points,
        use_degree=False,
    )
    oval_arc(
        a,
        b,
        beta_b2,
        beta_e2,
        angle=rotate_theta,
        color=color,
        alpha=alpha,
        center=center2_rot,
        points=points,
        use_degree=False,
    )


def rotate_point(point, theta):
    """
    将点绕原点旋转 theta 角度（弧度）。

    参数:
        point (tuple): 点的坐标 (x, y)。
        theta (float): 旋转角度（弧度）。

    返回:
        tuple: 旋转后的新坐标 (x_new, y_new)。
    """
    x, y = point
    x_new = x * np.cos(theta) - y * np.sin(theta)
    y_new = x * np.sin(theta) + y * np.cos(theta)
    return (x_new, y_new)


def oval_petal(
    a=2,
    b=1,
    d=0.5,
    rotate_theta=0,
    rot_by_center=True,
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
    **kwargs,
):
    """
    绘制一个椭圆花瓣形状。

    参数:
        a (float): 椭圆的长轴长度。
        b (float): 椭圆的短轴长度。
        d (float): 花瓣的垂直距离。
        rotate_theta (float): 旋转角度（度或弧度，取决于 use_degree），默认为0。
        color (str): 颜色，默认为绿色("#0f0")。
        alpha (float): 透明度，默认为1（不透明）。
        center (tuple): 中心坐标，默认为(0, 0)。
        points (int): 用于绘制弧的点数，默认为1000。
        use_degree (bool): 是否使用角度制（True为角度，False为弧度），默认为True。
        linestyle (str): 线型，默认为实线("-")。
        linewidth (int): 线宽，默认为1。
        label (str): 图例标签，默认为None。
        marker (str): 标记样式，默认为None。
        markersize (int): 标记大小，默认为5。
        markerfacecolor (str): 标记填充颜色，默认为红色("r")。
        markeredgecolor (str): 标记边缘颜色，默认为黑色("k")。
        markeredgewidth (int): 标记边缘宽度，默认为1。
        ax (matplotlib.axes.Axes): 目标坐标轴，默认为None（使用当前坐标轴）。
        plot (bool): 是否绘制图像，默认为True。如果为False，则返回计算得到的坐标。
        **kwargs: 其他传递给 plt.plot 的参数。

    返回:
        如果 plot=True:
            None
        如果 plot=False:
            tuple: (x1, y1, x2, y2) 计算得到的两个弧的坐标值。
    """
    # 计算 beta 角度
    x0 = b / (2 * a) * np.sqrt(4 * a**2 - d**2) / (d / 2)
    beta = np.arctan(x0)
    beta_b1 = np.pi / 2 - beta
    beta_e1 = np.pi / 2 + beta
    beta_b2 = 3 * np.pi / 2 - beta
    beta_e2 = 3 * np.pi / 2 + beta

    # 角度转换
    if use_degree:
        beta_b1 = np.rad2deg(beta_b1)
        beta_e1 = np.rad2deg(beta_e1)
        beta_b2 = np.rad2deg(beta_b2)
        beta_e2 = np.rad2deg(beta_e2)
        rotate_theta_rad = np.deg2rad(rotate_theta)
    else:
        rotate_theta_rad = rotate_theta

    # 计算中心点
    center1 = (center[0], center[1] - d / 2)
    center2 = (center[0], center[1] + d / 2)
    if rot_by_center:
        center1_rot = rotate_point(center1, rotate_theta_rad)
        center2_rot = rotate_point(center2, rotate_theta_rad)
    else:
        center1_rot = rotate_point((a, center[1] - d / 2), rotate_theta_rad)
        center2_rot = rotate_point((a, center[1] + d / 2), rotate_theta_rad)
    # 如果不绘制图像，返回坐标值
    if not plot:
        # 计算第一个弧的坐标
        theta1 = np.linspace(beta_b1, beta_e1, points)
        x1 = (
            a * np.cos(theta1) * np.cos(rotate_theta_rad)
            - b * np.sin(theta1) * np.sin(rotate_theta_rad)
            + center1_rot[0]
        )
        y1 = (
            a * np.cos(theta1) * np.sin(rotate_theta_rad)
            + b * np.sin(theta1) * np.cos(rotate_theta_rad)
            + center1_rot[1]
        )

        # 计算第二个弧的坐标
        theta2 = np.linspace(beta_b2, beta_e2, points)
        x2 = (
            a * np.cos(theta2) * np.cos(rotate_theta_rad)
            - b * np.sin(theta2) * np.sin(rotate_theta_rad)
            + center2_rot[0]
        )
        y2 = (
            a * np.cos(theta2) * np.sin(rotate_theta_rad)
            + b * np.sin(theta2) * np.cos(rotate_theta_rad)
            + center2_rot[1]
        )

        return (x1, y1, x2, y2)

    # 绘制第一个弧
    oval_arc(
        a,
        b,
        beta_b1,
        beta_e1,
        angle=rotate_theta,
        color=color,
        alpha=alpha,
        center=center1_rot,
        points=points,
        linestyle=linestyle,
        linewidth=linewidth,
        label=label,
        marker=marker,
        markersize=markersize,
        markerfacecolor=markerfacecolor,
        markeredgecolor=markeredgecolor,
        markeredgewidth=markeredgewidth,
        ax=ax,
        use_degree=use_degree,
        **kwargs,
    )

    # 绘制第二个弧
    oval_arc(
        a,
        b,
        beta_b2,
        beta_e2,
        angle=rotate_theta,
        color=color,
        alpha=alpha,
        center=center2_rot,
        points=points,
        linestyle=linestyle,
        linewidth=linewidth,
        label=label,
        marker=marker,
        markersize=markersize,
        markerfacecolor=markerfacecolor,
        markeredgecolor=markeredgecolor,
        markeredgewidth=markeredgewidth,
        ax=ax,
        use_degree=use_degree,
        **kwargs,
    )

    """
    Flower Petal Fill
    """

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
        # 圆心
        # plt.plot(center1[0], center1[1], marker='o', color='r')
        # plt.plot(center2[0], center2[1], marker='o', color='b')
        arc = arc_degree_p(
            center1,
            r,
            alpha + np.pi + theta,
            alpha + np.pi + theta + np.pi * (n - 2) / n,
        )
        arc_inverse = arc_degree_p_inverse(
            center2, r, beta + theta, beta + theta + np.pi * (n + 2) / n
        )
        x = arc[0]
        y = arc[1]
        x1 = arc_inverse[0]
        y1 = arc_inverse[1]
        # X,Y轴等长
        plt.axis("equal")
        plt.fill(x, y, colorf)
        plt.fill(x1, y1, colorf)
        plt.plot(x, y, color, alpha)
        plt.plot(x1, y1, color, alpha)


def n_flowers_petal_fill(center, R, r, n, theta=0, colorf="b", color="r", alpha=0.1):
    alpha = 2 * np.pi / n
    a = R * np.sin(np.pi / n)
    beta = np.arccos((a) / r)
    theta_arc = np.pi / 2 - np.pi / n + np.arccos((a) / r)
    theta_petal = 2 * theta_arc
    # circle((0, 0), R, 'g')
    # circle((0, 0), R/2, 'g')
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
    # plt.plot(center1[0], center1[1], marker='o', color='r')
    # plt.plot(center2[0], center2[1], marker='o', color='b')
    x1 = arc[0]
    y1 = arc[1]
    x2 = arc_inverse[0]
    y2 = arc_inverse[1]
    merged_x = np.concatenate((x1, x2))
    merged_y = np.concatenate((y1, y2))
    plt.axis("equal")

    plt.fill(merged_x, merged_y, colorf)
    # plt.fill(x1, y1, colorf)
    # plt.fill(x2, y2, colorf)
    plt.plot(x1, y1, color, alpha)
    plt.plot(x2, y2, color, alpha)


"""
Flower Algorithm
"""


def oval_petal_flower(
    a, b, d, n=12, rotate_theta=0, color="#0f0", alpha=1, center=(0, 0), points=1000
):
    for i in range(n):
        oval_petal(
            a,
            b,
            d,
            rotate_theta + i * 2 * np.pi / n,
            1,
            color,
            alpha,
            center,
            points,
            use_degree=False,
        )


def oval_petal_flower_a(
    a, b, d, n=12, rotate_theta=0, color="#0f0", alpha=1, center=(0, 0), points=1000
):
    for i in range(n):
        oval_petal(
            a,
            b,
            d,
            rotate_theta + i * 2 * np.pi / n,
            False,
            color,
            alpha,
            center,
            points,
            use_degree=False,
        )
