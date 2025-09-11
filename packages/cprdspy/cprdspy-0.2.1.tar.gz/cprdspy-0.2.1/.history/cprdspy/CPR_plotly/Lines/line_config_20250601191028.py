from typing import Tuple, List, Optional, Union, Dict, Any, Literal
import numpy as np
import plotly.graph_objects as go
from functools import lru_cache


class LineError(Exception):
    """线条绘制相关的自定义异常"""

    pass


class LineConfig:
    """线条绘制的配置管理类"""

    def __init__(self):
        self.num_points = 10000  # 默认采样点数
        self.default_color = "#1f77b4"  # 默认蓝色
        self.line_width = 2  # 默认线宽
        self.opacity = 1.0  # 默认透明度
        self.marker_size = 8  # 默认点大小
        self.marker_symbol = "circle"  # 默认标记符号
        self.marker_line_width = 1  # 默认标记线宽
        self.marker_line_color = "#444"  # 默认标记线颜色

    @property
    def layout(self) -> Dict[str, Any]:
        """获取默认布局配置"""
        return {
            "showlegend": True,
            "margin": dict(l=20, r=20, t=20, b=20),
            "yaxis": {"scaleanchor": "x", "scaleratio": 1},
        }


# 创建全局配置实例
config = LineConfig()


@lru_cache(maxsize=128)
def _calculate_n_points(n: int, radius: float, theta: float = 0) -> List[List[float]]:
    """计算圆上均匀分布的n个点的坐标（带缓存）"""
    if n <= 0:
        raise LineError("Number of points must be positive")
    if radius < 0:
        raise LineError("Radius must be non-negative")

    return [
        [
            radius * np.cos(i * 2 * np.pi / n + np.pi / 2 + theta),
            radius * np.sin(i * 2 * np.pi / n + np.pi / 2 + theta),
        ]
        for i in range(n)
    ]


@lru_cache(maxsize=128)
def _calculate_swastika_points(
    n: int, radius: float, theta: float = 0
) -> List[List[float]]:
    """计算卍字图案的点坐标（带缓存）"""
    return [
        [
            radius * np.sqrt(2) ** i * np.cos(i * np.pi / 4 + theta),
            radius * np.sqrt(2) ** i * np.sin(i * np.pi / 4 + theta),
        ]
        for i in range(n)
    ]


def create_line_trace(
    x: List[float],
    y: List[float],
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    name: Optional[str] = None,
) -> go.Scatter:
    """创建线条的轨迹对象"""
    return go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(
            color=color or config.default_color,
            width=width or config.line_width,
        ),
        opacity=opacity or config.opacity,
        name=name or "Line",
    )


def create_point_trace(
    x: List[float],
    y: List[float],
    color: Optional[str] = None,
    size: Optional[int] = None,
    opacity: Optional[float] = None,
    symbol: Optional[str] = None,
    name: Optional[str] = None,
) -> go.Scatter:
    """创建点的轨迹对象"""
    return go.Scatter(
        x=x,
        y=y,
        mode="markers",
        marker=dict(
            color=color or config.default_color,
            size=size or config.marker_size,
            opacity=opacity or config.opacity,
            symbol=symbol or config.marker_symbol,
            line=dict(
                width=config.marker_line_width,
                color=config.marker_line_color,
            ),
        ),
        name=name or "Points",
    )


def n_points(n: int, radius: float, theta: float = 0) -> List[List[float]]:
    """生成圆上均匀分布的n个点"""
    try:
        return _calculate_n_points(n, radius, theta)
    except Exception as e:
        raise LineError(f"Error generating n points: {str(e)}")


def draw_points(
    points: List[List[float]],
    color: Optional[str] = None,
    size: Optional[int] = None,
    opacity: Optional[float] = None,
    symbol: Optional[str] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """绘制点集"""
    try:
        fig = go.Figure()
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        fig.add_trace(create_point_trace(x, y, color, size, opacity, symbol, name))
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise LineError(f"Error drawing points: {str(e)}")


def connect_points(
    points: List[List[float]],
    mode: Literal["all", "sequence", "closed"] = "all",
    show_points: bool = False,
    line_color: Optional[str] = None,
    point_color: Optional[str] = None,
    line_width: Optional[float] = None,
    point_size: Optional[int] = None,
    opacity: Optional[float] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """连接点集

    Args:
        points: 点坐标列表
        mode: 连接模式
            - "all": 两两连接所有点
            - "sequence": 按顺序连接点
            - "closed": 首尾相连形成闭合图形
        show_points: 是否显示点
        line_color: 线条颜色
        point_color: 点的颜色
        line_width: 线条宽度
        point_size: 点的大小
        opacity: 透明度
        name: 图例名称
    """
    try:
        fig = go.Figure()

        # 添加线条
        if mode == "all":
            # 两两连接所有点
            for i in range(len(points)):
                for j in range(i + 1, len(points)):
                    fig.add_trace(
                        create_line_trace(
                            [points[i][0], points[j][0]],
                            [points[i][1], points[j][1]],
                            line_color,
                            line_width,
                            opacity,
                            f"{name} Line {i}-{j}" if name else None,
                        )
                    )
        else:
            # 按顺序连接或首尾相连
            for i in range(len(points) - (0 if mode == "closed" else 1)):
                j = (i + 1) % len(points)
                fig.add_trace(
                    create_line_trace(
                        [points[i][0], points[j][0]],
                        [points[i][1], points[j][1]],
                        line_color,
                        line_width,
                        opacity,
                        f"{name} Line {i}-{j}" if name else None,
                    )
                )

        # 添加点
        if show_points:
            x = [p[0] for p in points]
            y = [p[1] for p in points]
            fig.add_trace(
                create_point_trace(
                    x,
                    y,
                    point_color,
                    point_size,
                    opacity,
                    name=f"{name} Points" if name else None,
                )
            )

        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise LineError(f"Error connecting points: {str(e)}")


def multi_polygon(
    n: int,
    m: int,
    direction: Literal["in", "out"] = "out",
    alpha: float = 0,
    theta: float = 0,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制多重多边形

    Args:
        n: 边数
        m: 层数
        direction: 方向，"in" 向内，"out" 向外
        alpha: 整体旋转角度
        theta: 每层额外旋转角度
        color: 线条颜色
        width: 线条宽度
        opacity: 透明度
    """
    try:
        fig = go.Figure()

        for i in range(m):
            radius = (np.cos(np.pi / n)) ** (i if direction == "in" else -i)
            points = n_points(n, radius, alpha + i * (np.pi / n + theta))
            sub_fig = connect_points(
                points,
                mode="closed",
                line_color=color,
                line_width=width,
                opacity=opacity,
                name=f"Layer {i+1}",
            )
            fig.add_traces(sub_fig.data)

        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise LineError(f"Error drawing multiple polygons: {str(e)}")


def metatron_cube(
    n: int,
    m: int,
    theta: float = 0,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制类梅塔特隆立方体连接

    Args:
        n: 每层点数
        m: 层数
        theta: 旋转角度
        color: 线条颜色
        width: 线条宽度
        opacity: 透明度
    """
    try:
        points = []
        for i in range(m):
            points.extend(n_points(n, i + 1, theta))

        return connect_points(
            points,
            mode="all",
            line_color=color,
            line_width=width,
            opacity=opacity,
            name="Metatron",
        )
    except Exception as e:
        raise LineError(f"Error drawing metatron cube: {str(e)}")


def swastika(
    n: int,
    radius: float = 1,
    theta: float = 0,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    show_points: bool = False,
) -> go.Figure:
    """绘制卍字图案

    Args:
        n: 点的数量
        radius: 基准半径
        theta: 旋转角度
        color: 线条颜色
        width: 线条宽度
        opacity: 透明度
        show_points: 是否显示点
    """
    try:
        fig = go.Figure()
        points = _calculate_swastika_points(n, radius, theta)

        # 添加中心射线
        if n == 2:
            rays = 4
            ray_length = radius * np.sqrt(2) ** (n - 2)
        elif n % 2 == 1:
            rays = 8
            ray_length_1 = radius * np.sqrt(2) ** (n - 3)
            ray_length_2 = radius * np.sqrt(2) ** (n - 2)
        else:
            rays = 8
            ray_length_1 = radius * np.sqrt(2) ** (n - 2)
            ray_length_2 = radius * np.sqrt(2) ** (n - 3)

        if n == 2:
            for i in range(rays):
                angle = i * 2 * np.pi / 4 + theta
                fig.add_trace(
                    create_line_trace(
                        [0, ray_length * np.cos(angle)],
                        [0, ray_length * np.sin(angle)],
                        color,
                        width,
                        opacity,
                        f"Ray {i+1}",
                    )
                )
        else:
            for i in range(4):
                angle_1 = i * 2 * np.pi / 4 + theta
                angle_2 = i * 2 * np.pi / 4 + np.pi / 4 + theta

                # 主射线
                fig.add_trace(
                    create_line_trace(
                        [0, ray_length_1 * np.cos(angle_1)],
                        [0, ray_length_1 * np.sin(angle_1)],
                        color,
                        width,
                        opacity,
                        f"Ray {2*i+1}",
                    )
                )

                # 次射线
                fig.add_trace(
                    create_line_trace(
                        [0, ray_length_2 * np.cos(angle_2)],
                        [0, ray_length_2 * np.sin(angle_2)],
                        color,
                        width,
                        opacity,
                        f"Ray {2*i+2}",
                    )
                )

        # 添加螺旋线
        for i in range(4):
            angle = i * 2 * np.pi / 4 + theta
            spiral_points = _calculate_swastika_points(n, radius, angle)
            x = [p[0] for p in spiral_points]
            y = [p[1] for p in spiral_points]
            fig.add_trace(
                create_line_trace(x, y, color, width, opacity, f"Spiral {i+1}")
            )

        # 添加点
        if show_points:
            for i in range(4):
                angle = i * 2 * np.pi / 4 + theta
                points = _calculate_swastika_points(n, radius, angle)
                x = [p[0] for p in points]
                y = [p[1] for p in points]
                fig.add_trace(
                    create_point_trace(
                        x, y, color, config.marker_size, opacity, name=f"Points {i+1}"
                    )
                )

        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise LineError(f"Error drawing swastika: {str(e)}")


def multi_swastika(
    n: int,
    m: int,
    radius: float = 1,
    theta: float = 0,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    show_points: bool = False,
) -> go.Figure:
    """绘制多重卍字图案

    Args:
        n: 点的数量
        radius: 基准半径
        m: 重复次数
        theta: 初始旋转角度
        color: 线条颜色
        width: 线条宽度
        opacity: 透明度
        show_points: 是否显示点
    """
    try:
        fig = go.Figure()

        for i in range(m):
            sub_fig = swastika(
                n, radius, theta + i * np.pi / m, color, width, opacity, show_points
            )
            fig.add_traces(sub_fig.data)

        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise LineError(f"Error drawing multiple swastikas: {str(e)}")


# 导出主要的函数和类
__all__ = [
    "LineConfig",
    "LineError",
    "config",
    "n_points",
    "draw_points",
    "connect_points",
    "multi_polygon",
    "metatron_cube",
    "swastika",
    "multi_swastika",
]
