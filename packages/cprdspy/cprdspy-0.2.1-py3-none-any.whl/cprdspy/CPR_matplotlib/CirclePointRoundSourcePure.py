import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('./CirclePointSourcePure.py')

'''this is a circle source
这是圈的注释
'''
# 基础工具(Basic_Tools)

'''
圈(Circles)
'''


def circle(center, radius, color='b'):
    angle = np.linspace(0, 2*np.pi, 1000)
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)
    plt.axis('equal')
    plt.plot(x, y, color)


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


'''
波(Waves)
'''
# 圈上波

# 等差

# 向外


def wave_circle_ari_o(A, F, P, color, theta=0, R=1):
    ConcentricCircles_o((0, 0), F, A, R, 'g')
    for i in range(P+1):
        ConcentricCircles_o((np.cos(i*2*np.pi/P+np.pi/2+theta),
                            np.sin(i*2*np.pi/P+np.pi/2+theta)), F, A, R, color)
# 向内


def wave_circle_ari_i(A, F, P, color, theta=0, R=1):
    ConcentricCircles_i((0, 0), F, A, R, 'g')
    for i in range(P+1):
        ConcentricCircles_i((np.cos(i*2*np.pi/P+np.pi/2+theta),
                            np.sin(i*2*np.pi/P+np.pi/2+theta)), F, A, R, color)

# 双向


def wave_circle_ari(A, F, P, color, theta=0, R=1):
    ConcentricCircles((0, 0), F, A, R, 'g')
    for i in range(P+1):
        ConcentricCircles((np.cos(i*2*np.pi/P+np.pi/2+theta),
                           np.sin(i*2*np.pi/P+np.pi/2+theta)), F, A, R, color)


# 等比


# 向外
def wave_circle_pro_o(A, F, P, color, theta=0, R=1):
    ConcentricCircles_Pro_o((0, 0), F, np.sqrt(A), R, color)
    for i in range(P+1):
        ConcentricCircles_Pro_o(
            ((np.cos(i*2*np.pi/P+np.pi/2+theta)), np.sin(i*2*np.pi/P+np.pi/2+theta)), F, np.sqrt(A), R, color)


# 向内
def wave_circle_pro_i(A, F, P, color, theta=0, R=1):
    ConcentricCircles_Pro_i((0, 0), F, np.sqrt(A), R, color)
    for i in range(P+1):
        ConcentricCircles_Pro_i(
            ((np.cos(i*2*np.pi/P+np.pi/2+theta)), np.sin(i*2*np.pi/P+np.pi/2+theta)), F, np.sqrt(A), R, color)
# 双向


def wave_circle_pro(A, F, P, color, theta=0, R=1):
    ConcentricCircles_Pro((0, 0), F, np.sqrt(A), R, color)
    for i in range(P+1):
        ConcentricCircles_Pro(
            ((np.cos(i*2*np.pi/P+np.pi/2+theta)), np.sin(i*2*np.pi/P+np.pi/2+theta)), F, np.sqrt(A), R, color)


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


"""通过角度画圆弧
"""


def flower_arc_degree(center, radius, angle1, angle2, color='b'):
    if angle1 < angle2:
        angle = np.linspace(angle1, angle2, 1000)
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        plt.axis('equal')
        plt.plot(x, y, color)


def flower_arc_degree_inverse(center, radius, angle1, angle2, color='b'):
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


'''
画花算法(Flower Drawing Algorithm)
'''

"""_summary_: 画空心花(Draw Hollow Flowers)
"""
# 花瓣


def n_flower_petal(center, R, r, n, theta=0, color='b'):
    alpha = 2*np.pi/n
    a = R*np.sin(np.pi/n)
    beta = np.arccos((a)/r)
    theta_arc = np.pi/2-np.pi/n+np.arccos((a)/r)
    theta_petal = 2*theta_arc
    # circle((0, 0), R, 'g')
    # circle((0, 0), R/2, 'g')
    center1 = (np.cos(theta+alpha/2)*R +
               center[0], np.sin(theta+alpha/2)*R+center[1])
    center2 = (np.cos(theta+alpha/2-2*np.pi/n)*R +
               center[0], np.sin(theta+alpha/2-2*np.pi/n)*R+center[1])
    if abs(r - a) < 1e-12:
        flower_arc_degree(center1, r, np.pi+alpha/2+theta,
                          np.pi+alpha/2+theta+theta_arc, color)
        flower_arc_degree(center2, r, np.pi/2+theta,
                          np.pi/2+theta+theta_arc, color)
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
        flower_arc_degree(center1, r, np.pi+alpha/2+theta,
                          np.pi+alpha/2+theta+theta_arc, color)
        flower_arc_degree(center2, r, np.pi/2-beta+theta,
                          np.pi/2-beta+theta+theta_arc, color)
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
        print('r<a,不能形成花瓣。')
    # plt.plot(center1[0], center1[1], marker='o', color='r')
    # plt.plot(center2[0], center2[1], marker='o', color='b')
# 花弧


def n_flower_arc(center, R, r, n, theta=0, color='b'):
    alpha = 2*np.pi/n
    a = R*np.sin(np.pi/n)
    beta = np.arccos((a)/r)
    theta_arc = np.pi/2-np.pi/n+np.arccos((a)/r)
    theta_petal = 2*theta_arc
    # circle((0, 0), R, 'g')
    # circle((0, 0), R/2, 'g')
    center1 = (np.cos(theta+alpha/2)*R +
               center[0], np.sin(theta+alpha/2)*R+center[1])
    center2 = (np.cos(theta+alpha/2-2*np.pi/n)*R +
               center[0], np.sin(theta+alpha/2-2*np.pi/n)*R+center[1])
    if abs(r - a) < 1e-12:
        flower_arc_degree(center1, r, np.pi/2+alpha+theta,
                          np.pi/2+alpha+theta+theta_petal, color)
        flower_arc_degree(center2, r, np.pi/2+theta,
                          np.pi/2+theta+theta_petal, color)
        if r == R:
            print("r=", r, ",a=", a)
            print('r=a,r=R形成睡莲花弧。')
        elif r > R:
            print("r=", r, ",a=", a)
            print('r=a,r>R形成荷花花弧。')
        elif r < R:
            print("r=", r, ",a=", a)
            print('r=a,r<R形成特殊曼陀罗花弧。')
    elif r > a:
        flower_arc_degree(center1, r, np.pi/2+alpha-beta+theta,
                          np.pi/2+alpha-beta+theta+theta_petal, color)
        flower_arc_degree(center2, r, np.pi/2-beta+theta,
                          np.pi/2-beta+theta+theta_petal, color)
        if r == R:
            print("r=", r, ",a=", a)
            print('r>a,r=R形成睡莲花弧。')
        elif r > R:
            print("r=", r, ",a=", a)
            print('r>a,r>R形成荷花花弧。')
        elif r < R:
            print("r=", r, ",a=", a)
            print('r>a,r<R形成普通曼陀罗花弧。')
    elif r < a:
        print("r=", r, ",a=", a)
        print('r<a,不能形成花瓣。')
    # plt.plot(center1[0], center1[1], marker='o', color='r')
    # plt.plot(center2[0], center2[1], marker='o', color='b')

# 带场花弧


def n_flowers_flower_arc_with_field(center, R, r, n, theta=0, color='b', colorfield='#ff0'):
    alpha = 2*np.pi/n
    a = R*np.sin(np.pi/n)
    beta = np.arccos((a)/r)
    theta_arc = np.pi/2-np.pi/n+np.arccos((a)/r)
    theta_petal = 2*theta_arc
    # circle((0, 0), R, 'g')
    # circle((0, 0), R/2, 'g')
    center1 = (np.cos(theta+alpha/2)*R +
               center[0], np.sin(theta+alpha/2)*R+center[1])
    center2 = (np.cos(theta+alpha/2-2*np.pi/n)*R +
               center[0], np.sin(theta+alpha/2-2*np.pi/n)*R+center[1])
    if abs(r - a) < 1e-12:
        flower_arc_degree(center1, r, np.pi/2+alpha+theta,
                          np.pi/2+alpha+theta+theta_petal, color)
        flower_arc_degree_inverse(center1, r, np.pi/2+alpha+theta,
                                  np.pi/2+alpha+theta+theta_petal, colorfield)
        flower_arc_degree(center2, r, np.pi/2+theta,
                          np.pi/2+theta+theta_petal, color)
        flower_arc_degree_inverse(center2, r, np.pi/2+theta,
                                  np.pi/2+theta+theta_petal, colorfield)
    elif r > a:
        flower_arc_degree(center1, r, np.pi/2+alpha-beta+theta,
                          np.pi/2+alpha-beta+theta+theta_petal, color)
        flower_arc_degree_inverse(center1, r, np.pi/2+alpha-beta+theta,
                                  np.pi/2+alpha-beta+theta+theta_petal, colorfield)
        flower_arc_degree(center2, r, np.pi/2-beta+theta,
                          np.pi/2-beta+theta+theta_petal, color)
        flower_arc_degree_inverse(center2, r, np.pi/2-beta+theta,
                                  np.pi/2-beta+theta+theta_petal, colorfield)
    elif r < a:
        print("r=", r, ",a=", a)
        print('r<a,不能形成花瓣。')
    # plt.plot(center1[0], center1[1], marker='o', color='r')
    # plt.plot(center2[0], center2[1], marker='o', color='b')

# 一朵向上花瓣


def one_flower_petal(center, R, r, n, theta=0, color='b'):
    n_flower_petal(center, R, r, n, theta+np.pi/2, color)

# 一朵向上花弧


def one_flower_arc(center, R, r, n, theta=0, color='b'):
    n_flower_arc(center, R, r, n, theta+np.pi/2, color)

# 一朵向上花瓣场


def one_flower_flower_arc_with_field(center, R, r, n, theta=0, color='b', colorfield='#ff0'):
    n_flowers_flower_arc_with_field(center, R, r, n, theta +
                                    np.pi/2, color, colorfield)

# 花瓣形成的单层花


def flowers_flower_by_petal(center, R, r, N, n, theta, color='b'):
    for i in range(0, N):
        one_flower_petal(center, R, r, n, 2*i*np.pi/N+theta, color)


# 花弧形成的单层花


def flowers_flower_by_arc(center, R, r, N, n, theta, color='b'):
    for i in range(0, N):
        one_flower_arc(center, R, r, n, 2*i*np.pi/N+theta, color)

# 单层花带场


def flowers_flower_by_flower_arc_with_field(center, R, r, N, n, theta, color='b', colorfield='#ff0'):
    for i in range(0, N):
        one_flower_flower_arc_with_field(
            center, R, r, n, 2*i*np.pi/N+theta, color)

# 花瓣形成的多层花


def flowers_flower_by_petal_multi(center, R, r, n, ratio, M, N, theta, color='b'):
    for j in range(1, M+1):
        for i in range(0, N):
            one_flower_petal(center, R*(ratio**(j-1)), r*(ratio**(j-1)),
                             n, 2*i*np.pi/N+(j-1)*np.pi/N+theta, color)


"""_summary_: 画带上色花(Draw Colored Flowers)
"""
########################
########################
########################
########################
########################
########################
########################
########################


# def onearc_lily_n(center, r, n, theta, color='b'):
#     # (n-2)/n个圆弧
#     arc_degree(center, r, theta, theta+2*np.pi*(n-2)/n, color)


# def onearc_lily_n_inverse(center, r, n, theta, color='b'):
#     # (n-2)/n个圆弧
#     arc_degree_inverse(center, r, theta, theta+2*np.pi*(n-2)/n, color)


def n_lily_petal_fill(center, r, n, theta, colorf='b', color='r', alpha=0.1):
    alpha = np.pi/n
    beta = np.pi-np.pi/n
    center1 = (np.cos(theta+alpha)*r +
               center[0], np.sin(theta+alpha)*r+center[1])
    center2 = (np.cos(theta+alpha-2*np.pi/n)*r +
               center[0], np.sin(theta+alpha-2*np.pi/n)*r+center[1])
    # 圆心
    # plt.plot(center1[0], center1[1], marker='o', color='r')
    # plt.plot(center2[0], center2[1], marker='o', color='b')
    arc = arc_degree_p(center1, r, alpha+np.pi+theta,
                       alpha+np.pi+theta+np.pi*(n-2)/n)
    arc_inverse = arc_degree_p_inverse(center2, r, beta+theta,
                                       beta+theta+np.pi*(n+2)/n)
    x = arc[0]
    y = arc[1]
    x1 = arc_inverse[0]
    y1 = arc_inverse[1]
    # X,Y轴等长
    plt.axis('equal')
    plt.fill(x, y, colorf)
    plt.fill(x1, y1, colorf)
    plt.plot(x, y, color, alpha)
    plt.plot(x1, y1, color, alpha)


def n_flowers_petal_fill(center, R, r, n, theta=0, colorf='b', color='r', alpha=0.1):
    alpha = 2*np.pi/n
    a = R*np.sin(np.pi/n)
    beta = np.arccos((a)/r)
    theta_arc = np.pi/2-np.pi/n+np.arccos((a)/r)
    theta_petal = 2*theta_arc
    # circle((0, 0), R, 'g')
    # circle((0, 0), R/2, 'g')
    center1 = (np.cos(theta+alpha/2)*R +
               center[0], np.sin(theta+alpha/2)*R+center[1])
    center2 = (np.cos(theta+alpha/2-2*np.pi/n)*R +
               center[0], np.sin(theta+alpha/2-2*np.pi/n)*R+center[1])
    if abs(r - a) < 1e-12:
        arc = arc_degree_p(center1, r, np.pi+alpha/2+theta,
                           np.pi+alpha/2+theta+theta_arc)
        arc_inverse = arc_degree_p(center2, r, np.pi/2+theta,
                                   np.pi/2+theta+theta_arc)
    elif r > a:
        arc = arc_degree_p(center1, r, np.pi+alpha/2+theta,
                           np.pi+alpha/2+theta+theta_arc)
        arc_inverse = arc_degree_p(center2, r, np.pi/2-beta+theta,
                                   np.pi/2-beta+theta+theta_arc)
    elif r < a:
        print("r=", r, ",a=", a)
        print('r<a,不能形成花瓣。')
    # plt.plot(center1[0], center1[1], marker='o', color='r')
    # plt.plot(center2[0], center2[1], marker='o', color='b')
    x1 = arc[0]
    y1 = arc[1]
    x2 = arc_inverse[0]
    y2 = arc_inverse[1]
    merged_x = np.concatenate((x1, x2))
    merged_y = np.concatenate((y1, y2))
    plt.axis('equal')

    plt.fill(merged_x, merged_y, colorf)
    # plt.fill(x1, y1, colorf)
    # plt.fill(x2, y2, colorf)
    plt.plot(x1, y1, color, alpha)
    plt.plot(x2, y2, color, alpha)

# 带填充的花瓣形成的花


def one_petal_fill(center, r, n, theta, colorf='r', color='b'):
    n_lily_petal_fill(center, r, n, theta+np.pi/2, colorf, color)


def one_layer_flower_by_petal_fill(center, R, n, theta, colorf='r', color='b'):
    for i in range(0, n):
        one_petal_fill(center, R, n, 2 * i * np.pi /
                       n + theta, colorf, color)


# one_layer_flower_by_petal_fill((0, 0), 1, 1, 0, '#0f0', 'b')


def flower_by_petal_fill(center, r, M, N, n, theta, colorf='r', color='b'):
    for j in range(1, M+1):
        for i in range(0, N):
            one_petal_fill(center, (np.sqrt(2*np.cos(np.pi/n))**(2*j-1)*r),
                           n, 2*i*np.pi/N+(j-1)*np.pi/N+theta, colorf, color)

# 一朵向上花瓣带填充


def one_flower_petal_fill(center, R, r, n, theta=0, colorf='r', color='b', alpha=0.5):
    n_flowers_petal_fill(center, R, r, n, theta+np.pi/2, colorf, color, alpha)

# 花瓣形成的单层花带填充


def flowers_flower_by_petal_fill(center, R, r, N, n, theta, colorf='r', color='b', alpha=0.5):
    for i in range(0, N):
        one_flower_petal_fill(center, R, r, n, 2*i *
                              np.pi/N+theta, colorf, color, alpha)

# 花弧


def n_flowers_arc_p(center, R, r, n, theta=0):
    alpha = 2*np.pi/n
    a = R*np.sin(np.pi/n)
    beta = np.arccos((a)/r)
    theta_arc = np.pi/2-np.pi/n+np.arccos((a)/r)
    theta_petal = 2*theta_arc
    # circle((0, 0), R, 'g')
    # circle((0, 0), R/2, 'g')
    center1 = (np.cos(theta+alpha/2)*R +
               center[0], np.sin(theta+alpha/2)*R+center[1])
    center2 = (np.cos(theta+alpha/2-2*np.pi/n)*R +
               center[0], np.sin(theta+alpha/2-2*np.pi/n)*R+center[1])
    if abs(r - a) < 1e-12:
        arc = arc_degree_p(center1, r, np.pi/2+alpha+theta,
                           np.pi/2+alpha+theta+theta_petal)
        arc_inverse = arc_degree_p(center2, r, np.pi/2+theta,
                                   np.pi/2+theta+theta_petal)
    elif r > a:
        arc = arc_degree_p(center1, r, np.pi/2+alpha-beta+theta,
                           np.pi/2+alpha-beta+theta+theta_petal)
        arc_inverse = arc_degree_p(center2, r, np.pi/2-beta+theta,
                                   np.pi/2-beta+theta+theta_petal)
    elif r < a:
        print("r=", r, ",a=", a)
        print('r<a,不能形成花瓣。')
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
############################################################
# 一朵向上花弧


# def one_flowers_arc_p(center, R, r, n, theta=0):
#     points = n_flowers_arc_p(center, R, r, n, theta+np.pi/2)
#     return points
# # 花弧形成的单层花


# def flowers_flower_by_arc_p(center, R, r, N, n, theta):
#     points = [0, 0]
#     for i in range(0, N):
#         points[0] += one_flowers_arc_p(center, R, r, n, 2*i*np.pi/N+theta)[0]
#         points[1] += one_flowers_arc_p(center, R, r, n, 2*i*np.pi/N+theta)[1]
#     return [points[0], points[1]]


# def n_flowers_arc_fill(center, R, r, n, N, theta=0, colorf='b', color='r', alpha=0.1):
#     points = flowers_flower_by_arc_p(center, R, r, N, n, theta)
#     # print(points)
#     plt.fill(points[0], points[1], colorf)
#     # plt.fill(x1, y1, colorf)
#     # plt.fill(x2, y2, colorf)
#     plt.plot(points[0], points[1], color, alpha)
#     plt.scatter(points[0][0], points[1][0], s=1, color='r')
#     plt.axis('equal')
############################################################


"""
罗丹线圈注释
this is a rose curve source
"""


def rodincoil(R, r, n, color='b', theta=0):
    for i in range(0, n):
        circle((R*np.cos(i*2*np.pi/n+theta), R *
               np.sin(i*2*np.pi/n+theta)), r, color)


def rodincoil_colorful(R, r, n, colors, theta=0):
    for i in range(0, n):
        circle((R*np.cos(i*2*np.pi/n+theta), R *
               np.sin(i*2*np.pi/n+theta)), r, colors[i])


"""
螺旋线注释
this is a spiral source
"""


def logSpiral(n, a, b, cyc, color='b', theta=0):
    t = np.linspace(-cyc * 2 * np.pi, cyc * 2 * np.pi, 100)
    x = a*(np.cos(np.pi/n)) ** (-n*t / np.pi) * np.cos(t+theta)
    y = b*(np.cos(np.pi/n)) ** (-n*t / np.pi) * np.sin(t+theta)
    plt.plot(x, y, color)
    # plt.axis('equal')


def logSpiral_out(n, a, b, cyc, color='b', theta=0):
    t = np.linspace(0, cyc * 2 * np.pi, 100)
    x = a*(np.cos(np.pi/n)) ** (-n*t / np.pi) * np.cos(t+theta)
    y = b*(np.cos(np.pi/n)) ** (-n*t / np.pi) * np.sin(t+theta)
    plt.plot(x, y, color)


def logSpiral_in(n, a, b, cyc, color='b', theta=0):
    t = np.linspace(0, -cyc * 2 * np.pi, 100)
    x = a*(np.cos(np.pi/n)) ** (-n*t / np.pi) * np.cos(t+theta)
    y = b*(np.cos(np.pi/n)) ** (-n*t / np.pi) * np.sin(t+theta)
    plt.plot(x, y, color)


def n_spiral(n, cyc, color, theta=0):
    for i in range(n):
        logSpiral(n, 1, 1, cyc, color, theta+i*2*np.pi/n)
        logSpiral(n, -1, 1, cyc, color, theta+i*2*np.pi/n)


def n_spiral_rotate(n, cyc, color, alpha=0, theta=0):
    for i in range(n):
        logSpiral(n, 1, 1, cyc, color, alpha+theta+i*2*np.pi/n)
        logSpiral(n, -1, 1, cyc, color, alpha-theta+i*2*np.pi/n)


def n_spiral_rotate_out(n, cyc, color, theta=0):
    for i in range(n):
        logSpiral_out(n, 1, 1, cyc, color, theta+i*2*np.pi/n)
        logSpiral_out(n, -1, 1, cyc, color, -theta+i*2*np.pi/n)


def n_spiral_rotate_in(n, cyc, color, theta=0):
    for i in range(n):
        logSpiral_in(n, 1, 1, cyc, color, theta+i*2*np.pi/n)
        logSpiral_in(n, -1, 1, cyc, color, -theta+i*2*np.pi/n)


def calla_petal(n, cyc, theta, color):
    logSpiral(n, 1, 1, cyc*1.25, color, theta)
    logSpiral(n, -1, 1, cyc*1.25, color, -theta)


def calla_by_petal(n, cyc, N, theta, colors):
    for i in range(N):
        calla_petal(n, cyc, theta+i*2*np.pi/N, colors[i])


"""
this is a  point source
这是点的注释
"""
# 生成半径R圆上均匀N等分点


def n_points(N, R, theta=0):
    return [[R*np.cos(i*2 * np.pi/N+np.pi/2+theta), R*np.sin(i*2 * np.pi/N+np.pi/2+theta)] for i in range(N)]

# 画出点


def draw_points(points, colorp='b', size=100):
    for i in range(len(points)):
        plt.scatter(points[i][0], points[i][1], s=size, color=colorp)

# 双向生成点阵


def n_points_array(n, m, theta=0):
    points = []
    for i in range(m):
        points += n_points(n, (np.cos(np.pi/n))**i, i*(np.pi/n+theta))
        points += n_points(n, (np.cos(np.pi/n))
                           ** (-i), i*(np.pi/n-theta))
    return points


# 向内生成点阵
def n_points_array_inner(n, m, theta=0):
    points = []
    for i in range(m):
        points += n_points(n, (np.cos(np.pi/n))
                           ** i, i*(np.pi/n+theta))
    return points


# 向外生成点阵
def n_points_array_outer(n, m, theta=0):
    points = []
    for i in range(m):
        points += n_points(n, (np.cos(np.pi/n))
                           ** (-i), i*(np.pi/n+theta))
    return points


def n_points_array_outer_rotate(n, m, alpha=0, theta=0):
    points = []
    for i in range(m):
        points += n_points(n, (np.cos(np.pi/n))
                           ** (-i), alpha+i*(np.pi/n+theta))
    return points


def n_points_array_inner_rotate(n, m, alpha=0, theta=0):
    points = []
    for i in range(m):
        points += n_points(n, (np.cos(np.pi/n))
                           ** (i), alpha+i*(np.pi/n+theta))
    return points
# 画N边形点阵
# n:边数
# m: 阵列层数


def draw_n_points_array(n, m, theta=0, color='b', size=100):
    for i in range(m):
        draw_points(
            n_points(n, (np.cos(np.pi/n))**i, i*(np.pi/n+theta)), color, size)
        draw_points(
            n_points(n, (np.cos(np.pi/n))**(-i), i*(np.pi/n-theta)), color, size)

# 向外画点阵


def draw_n_points_array_outer(n, m, theta=0, color='b', size=100):
    for i in range(m):
        draw_points(
            n_points(n, (np.cos(np.pi/n))**(-i), i*(np.pi/n+theta)), color, size)

# 向内画点阵


def draw_n_points_array_inner(n, m, theta=0, color='b', size=100):
    for i in range(m):
        draw_points(
            n_points(n, (np.cos(np.pi/n))**(i), i*(np.pi/n-theta)), color, size)


def swastika(N, R=1, theta=0):
    points = [(R*np.sqrt(2)**i*np.cos(i*np.pi/4+theta), R*np.sqrt(2)
               ** i*np.sin(i*np.pi/4+theta)) for i in range(N)]
    return points


"""
这是线的注释
this is a  line source
"""
# 生成半径R圆上N等分点


def n_points(N, R, theta=0):
    return [[R*np.cos(i*2 * np.pi/N+np.pi/2+theta), R*np.sin(i*2 * np.pi/N+np.pi/2+theta)] for i in range(N)]


# 两两连接所有点


def connect_all(points, color='g'):
    for i in range(len(points)):
        for j in range(i+1, len(points)):
            plt.plot([points[i][0], points[j][0]],
                     [points[i][1], points[j][1]], color)


# 带点两两连接所有点
def connect_all_with_points(points, colorp='b', colorl='g'):
    for i in range(len(points)):
        for j in range(i+1, len(points)):
            plt.plot([points[i][0], points[j][0]],
                     [points[i][1], points[j][1]], colorl)
    for i in range(len(points)):
        plt.scatter(points[i][0], points[i][1], color=colorp)

# 首尾连接


def connect(points, color='g'):
    num = len(points)
    for i in range(-1, num-1):
        plt.plot([points[i][0], points[i+1][0]],
                 [points[i][1], points[i+1][1]], color)


def connect_in_order(points, color='g'):
    num = len(points)
    for i in range(0, num-1):
        plt.plot([points[i][0], points[i+1][0]],
                 [points[i][1], points[i+1][1]], color)

# 带点首位连接


def connect_with_points(points, colorp='b', colorl='g'):
    num = len(points)
    for i in range(-1, num-1):
        plt.plot([points[i][0], points[i+1][0]],
                 [points[i][1], points[i+1][1]], colorl)
    for i in range(len(points)):
        plt.scatter(points[i][0], points[i][1], color=colorp)

# 多重多边形


def multi_polygon(n, m, color='b', alpha=0, theta=0):
    for i in range(m):
        connect(n_points(n, (np.cos(np.pi/n)) **
                (-i), alpha+i*(np.pi/n+theta)), color)

# 类梅塔特隆立方体连接


def connect_like_metatron(n, m, color='b', theta=0):
    points = []
    for i in range(m):
        points += n_points(n, i+1, theta)
    connect_all(points, color)

# 卍字连接


def draw_swastika(n, R, theta=0, color='b'):
    if n == 2:
        for i in range(4):
            plt.plot([R*np.sqrt(2)**(n-2)*np.cos(i*2*np.pi/4+theta), 0],
                     [R*np.sqrt(2) ** (n-2)*np.sin(i*2*np.pi/4+theta), 0], color)
    elif n % 2 == 1:
        for i in range(4):
            plt.plot([R*np.sqrt(2)**(n-3)*np.cos(i*2*np.pi/4+theta), 0],
                     [R*np.sqrt(2) ** (n-3)*np.sin(i*2*np.pi/4+theta), 0], color)
            plt.plot([R*np.sqrt(2)**(n-2)*np.cos(i*2*np.pi/4+np.pi/4+theta), 0],
                     [R*np.sqrt(2) ** (n-2)*np.sin(i*2*np.pi/4+np.pi/4+theta), 0], color)
    else:
        for i in range(4):
            plt.plot([R*np.sqrt(2)**(n-2)*np.cos(i*2*np.pi/4+theta), 0],
                     [R*np.sqrt(2) ** (n-2)*np.sin(i*2*np.pi/4+theta), 0], color)
            plt.plot([R*np.sqrt(2)**(n-3)*np.cos(i*2*np.pi/4+np.pi/4+theta), 0],
                     [R*np.sqrt(2) ** (n-3)*np.sin(i*2*np.pi/4+np.pi/4+theta), 0], color)
    for i in range(4):
        points = swastika(n, R, i*2*np.pi/4+theta)
        connect_in_order(points, color)


def draw_swastikas(n, R, m, color='b', theta=0):
    for i in range(m):
        draw_swastika(n, R, i*np.pi/m+theta, color)


def rotate_point(point, theta):
    """将点绕原点旋转theta角度"""
    x, y = point
    x_new = x * np.cos(theta) - y * np.sin(theta)
    y_new = x * np.sin(theta) + y * np.cos(theta)
    return (x_new, y_new)

def draw_petal_any(center, r, d, rotate_theta=0, color='b'):
    a = np.sqrt(r**2 - d**2 / 4)
    theta = 2 * np.arctan(2 * a / d)
    theta_b1 = np.pi + np.pi / 2 - theta / 2
    theta_e1 = np.pi + np.pi / 2 + theta / 2
    theta_b2 = np.pi / 2 - theta / 2
    theta_e2 = np.pi / 2 + theta / 2
    center1 = (a + center[0], d / 2 + center[1])
    center2 = (a + center[0], center[1] - d / 2)
    # 关键点整体绕原点旋转
    center1_rot = rotate_point(center1, rotate_theta)
    center2_rot = rotate_point(center2, rotate_theta)
    arc_degree(center1_rot, r, theta_b1 + rotate_theta, theta_e1 + rotate_theta, color)
    arc_degree(center2_rot, r, theta_b2 + rotate_theta, theta_e2 + rotate_theta, color)

def any_s_petal_flower(center, r, d, n, theta=0, color='#0f0'):
    for i in range(n):
        draw_petal_any(center, r, d, theta+i*2*np.pi/n, color)



# 椭圆及椭圆弧
def ellipse(a, b, angle=0, color='#0f0',alpha=1, center=(0,0), points=1000):
    theta = np.linspace(0,  2*np.pi,  points)
    angle_rad = np.deg2rad(angle) 
    x = a * np.cos(theta)  * np.cos(angle_rad)  - b * np.sin(theta)  * np.sin(angle_rad)  + center[0]
    y = a * np.cos(theta)  * np.sin(angle_rad)  + b * np.sin(theta)  * np.cos(angle_rad)  + center[1]
    plt.plot(x,y,color,alpha)
    
def oval_arc(a,b,angle1,angle2,angle=0,color='#0f0',alpha=1,center=(0,0),points=1000):
    theta = np.linspace(angle1, angle2, points)
    angle_rad = angle
    x = a * np.cos(theta)  * np.cos(angle_rad)  - b * np.sin(theta)  * np.sin(angle_rad)  + center[0]
    y = a * np.cos(theta)  * np.sin(angle_rad)  + b * np.sin(theta)  * np.cos(angle_rad)  + center[1]
    plt.plot(x,y,color=color,alpha=alpha)
    plt.axis('equal')
def oval_petal(a,b,d,rotate_theta=0,color='#0f0',alpha=1,center=(0,0),points=1000):
    # x0=a/b*np.sqrt(4*(b/d)**2-1)
    # x0=a/(2*b)*np.sqrt(4*(b)**2-d**2)/(d/2)
    x0=b/(2*a)*np.sqrt(4*a**2-d**2)/(d/2)
    # print(x0)
    beta=np.arctan(x0)
    beta_b1=np.pi/2-beta
    beta_e1=np.pi/2+beta
    beta_b2=3*np.pi/2-beta
    beta_e2=3*np.pi/2+beta
    center1=(center[0],center[1]-d/2)
    center2=(center[0],center[1]+d/2)
    center1_rot = rotate_point(center1, rotate_theta)
    center2_rot = rotate_point(center2, rotate_theta)
    oval_arc(a,b,beta_b1,beta_e1,angle=rotate_theta,color=color,alpha=alpha,center=center1_rot,points=points)
    oval_arc(a,b,beta_b2,beta_e2,angle=rotate_theta,color=color,alpha=alpha,center=center2_rot,points=points)
    # print(center1,center2)

def oval_petal_a(a,b,d,rotate_theta=0,color='b',alpha=1,center=(0,0),points=1000):
    x0=b/(2*a)*np.sqrt(4*a**2-d**2)/(d/2)
    # x0=a/(2*b)*np.sqrt(4*(b)**2-d**2)/(d/2)
    beta=np.arctan(x0)
    beta_b1=np.pi/2-beta
    beta_e1=np.pi/2+beta
    beta_b2=3*np.pi/2-beta
    beta_e2=3*np.pi/2+beta
    center1=(center[0],center[1]-d/2)
    center2=(center[0],center[1]+d/2)
    center1_rot = rotate_point((a,center[1]-d/2), rotate_theta)
    center2_rot = rotate_point((a,center[1]+d/2), rotate_theta)
    oval_arc(a,b,beta_b1,beta_e1,angle=rotate_theta,color=color,alpha=alpha,center=center1_rot,points=points)
    oval_arc(a,b,beta_b2,beta_e2,angle=rotate_theta,color=color,alpha=alpha,center=center2_rot,points=points)

def oval_petal_flower(a,b,d,n=12,rotate_theta=0,color='#0f0',alpha=1,center=(0,0),points=1000):
    for i in range(n):
        oval_petal(a,b,d,rotate_theta+i*2*np.pi/n,color,alpha,center,points)


def oval_petal_flower_a(a,b,d,n=12,rotate_theta=0,color='#0f0',alpha=1,center=(0,0),points=1000):
    for i in range(n):
        oval_petal_a(a,b,d,rotate_theta+i*2*np.pi/n,color,alpha,center,points)
