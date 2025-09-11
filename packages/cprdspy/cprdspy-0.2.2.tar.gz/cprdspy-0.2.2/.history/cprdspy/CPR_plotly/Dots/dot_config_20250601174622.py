from typing import Tuple, List, Optional, Union, Dict, Any, Literal
import numpy as np
import plotly.graph_objects as go
from functools import lru_cache


class DotError(Exception):
    """点阵绘制相关的自定义异常"""

    pass


class DotConfig:
    """点阵绘制的配置管理类"""

    def __init__(self):
        self.default_size = 10  # 默认点大小
        self.default_color = "#1f77b4"  # 默认蓝色
        self.opacity = 1.0  # 默认透明度
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
config = DotConfig()


@lru_cache(maxsize=128)
def _calculate_n_points(n: int, radius: float, theta: float = 0) -> List[List[float]]:
    """计算圆上均匀分布的n个点的坐标（带缓存）

    Args:
        n: 点的数量
        radius: 圆的半径
        theta: 旋转角度（弧度）

    Returns:
        点坐标列表 [[x1, y1], [x2, y2], ...]
    """
    if n <= 0:
        raise DotError("Number of points must be positive")
    if radius < 0:
        raise DotError("Radius must be non-negative")

    return [
        [
            radius * np.cos(i * 2 * np.pi / n + np.pi / 2 + theta),
            radius * np.sin(i * 2 * np.pi / n + np.pi / 2 + theta),
        ]
        for i in range(n)
    ]


def create_dots_trace(
    points: List[List[float]],
    color: Optional[str] = None,
    size: Optional[int] = None,
    opacity: Optional[float] = None,
    symbol: Optional[str] = None,
    name: Optional[str] = None,
) -> go.Scatter:
    """创建点阵的轨迹对象

    Args:
        points: 点坐标列表 [[x1, y1], [x2, y2], ...]
        color: 点的颜色
        size: 点的大小
        opacity: 透明度
        symbol: 点的形状
        name: 图例名称

    Returns:
        plotly Scatter对象
    """
    x = [p[0] for p in points]
    y = [p[1] for p in points]

    return go.Scatter(
        x=x,
        y=y,
        mode="markers",
        marker=dict(
            color=color or config.default_color,
            size=size or config.default_size,
            opacity=opacity or config.opacity,
            symbol=symbol or config.marker_symbol,
            line=dict(width=config.marker_line_width, color=config.marker_line_color),
        ),
        name=name or "Dots",
    )


def n_points(n: int, radius: float, theta: float = 0) -> List[List[float]]:
    """生成半径为radius的圆上均匀分布的n个点

    Args:
        n: 点的数量
        radius: 圆的半径
        theta: 旋转角度（弧度）

    Returns:
        点坐标列表 [[x1, y1], [x2, y2], ...]
    """
    try:
        return _calculate_n_points(n, radius, theta)
    except Exception as e:
        raise DotError(f"Error generating n points: {str(e)}")


def draw_points(
    points: List[List[float]],
    color: Optional[str] = None,
    size: Optional[int] = None,
    opacity: Optional[float] = None,
    symbol: Optional[str] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """绘制点阵

    Args:
        points: 点坐标列表 [[x1, y1], [x2, y2], ...]
        color: 点的颜色
        size: 点的大小
        opacity: 透明度
        symbol: 点的形状
        name: 图例名称

    Returns:
        plotly Figure对象
    """
    try:
        fig = go.Figure()
        fig.add_trace(create_dots_trace(points, color, size, opacity, symbol, name))
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise DotError(f"Error drawing points: {str(e)}")


def n_points_array(n: int, m: int, theta: float = 0) -> List[List[float]]:
    """双向生成点阵

    Args:
        n: 每圈点的数量
        m: 圈数
        theta: 旋转角度（弧度）

    Returns:
        点坐标列表 [[x1, y1], [x2, y2], ...]
    """
    try:
        points = []
        for i in range(m):
            points.extend(
                n_points(n, (np.cos(np.pi / n)) ** i, i * (np.pi / n + theta))
            )
            points.extend(
                n_points(n, (np.cos(np.pi / n)) ** (-i), i * (np.pi / n - theta))
            )
        return points
    except Exception as e:
        raise DotError(f"Error generating n points array: {str(e)}")


def n_points_array_inner(n: int, m: int, theta: float = 0) -> List[List[float]]:
    """向内生成点阵

    Args:
        n: 每圈点的数量
        m: 圈数
        theta: 旋转角度（弧度）

    Returns:
        点坐标列表 [[x1, y1], [x2, y2], ...]
    """
    try:
        points = []
        for i in range(m):
            points.extend(
                n_points(n, (np.cos(np.pi / n)) ** i, i * (np.pi / n + theta))
            )
        return points
    except Exception as e:
        raise DotError(f"Error generating inner n points array: {str(e)}")


def n_points_array_outer(n: int, m: int, theta: float = 0) -> List[List[float]]:
    """向外生成点阵

    Args:
        n: 每圈点的数量
        m: 圈数
        theta: 旋转角度（弧度）

    Returns:
        点坐标列表 [[x1, y1], [x2, y2], ...]
    """
    try:
        points = []
        for i in range(m):
            points.extend(
                n_points(n, (np.cos(np.pi / n)) ** (-i), i * (np.pi / n + theta))
            )
        return points
    except Exception as e:
        raise DotError(f"Error generating outer n points array: {str(e)}")


def n_points_array_outer_rotate(
    n: int, m: int, alpha: float = 0, theta: float = 0
) -> List[List[float]]:
    """向外旋转生成点阵

    Args:
        n: 每圈点的数量
        m: 圈数
        alpha: 整体旋转角度（弧度）
        theta: 每圈额外旋转角度（弧度）

    Returns:
        点坐标列表 [[x1, y1], [x2, y2], ...]
    """
    try:
        points = []
        for i in range(m):
            points.extend(
                n_points(
                    n, (np.cos(np.pi / n)) ** (-i), alpha + i * (np.pi / n + theta)
                )
            )
        return points
    except Exception as e:
        raise DotError(f"Error generating outer rotated n points array: {str(e)}")


def n_points_array_inner_rotate(
    n: int, m: int, alpha: float = 0, theta: float = 0
) -> List[List[float]]:
    """向内旋转生成点阵

    Args:
        n: 每圈点的数量
        m: 圈数
        alpha: 整体旋转角度（弧度）
        theta: 每圈额外旋转角度（弧度）

    Returns:
        点坐标列表 [[x1, y1], [x2, y2], ...]
    """
    try:
        points = []
        for i in range(m):
            points.extend(
                n_points(n, (np.cos(np.pi / n)) ** i, alpha + i * (np.pi / n + theta))
            )
        return points
    except Exception as e:
        raise DotError(f"Error generating inner rotated n points array: {str(e)}")


def draw_n_points_array(
    n: int,
    m: int,
    theta: float = 0,
    color: Optional[str] = None,
    size: Optional[int] = None,
    opacity: Optional[float] = None,
    symbol: Optional[str] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """画N边形点阵（双向）

    Args:
        n: 每圈点的数量
        m: 圈数
        theta: 旋转角度（弧度）
        color: 点的颜色
        size: 点的大小
        opacity: 透明度
        symbol: 点的形状
        name: 图例名称

    Returns:
        plotly Figure对象
    """
    try:
        fig = go.Figure()

        for i in range(m):
            # 向内点阵
            inner_points = n_points(
                n, (np.cos(np.pi / n)) ** i, i * (np.pi / n + theta)
            )
            inner_name = f"{name or 'Dots'} Inner {i+1}" if name else f"Inner {i+1}"
            fig.add_trace(
                create_dots_trace(
                    inner_points, color, size, opacity, symbol, inner_name
                )
            )

            # 向外点阵
            outer_points = n_points(
                n, (np.cos(np.pi / n)) ** (-i), i * (np.pi / n - theta)
            )
            outer_name = f"{name or 'Dots'} Outer {i+1}" if name else f"Outer {i+1}"
            fig.add_trace(
                create_dots_trace(
                    outer_points, color, size, opacity, symbol, outer_name
                )
            )

        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise DotError(f"Error drawing n points array: {str(e)}")


def draw_n_points_array_outer(
    n: int,
    m: int,
    theta: float = 0,
    color: Optional[str] = None,
    size: Optional[int] = None,
    opacity: Optional[float] = None,
    symbol: Optional[str] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """向外画点阵

    Args:
        n: 每圈点的数量
        m: 圈数
        theta: 旋转角度（弧度）
        color: 点的颜色
        size: 点的大小
        opacity: 透明度
        symbol: 点的形状
        name: 图例名称

    Returns:
        plotly Figure对象
    """
    try:
        fig = go.Figure()

        for i in range(m):
            points = n_points(n, (np.cos(np.pi / n)) ** (-i), i * (np.pi / n + theta))
            trace_name = f"{name or 'Dots'} {i+1}" if name else f"Layer {i+1}"
            fig.add_trace(
                create_dots_trace(points, color, size, opacity, symbol, trace_name)
            )

        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise DotError(f"Error drawing outer n points array: {str(e)}")


def draw_n_points_array_inner(
    n: int,
    m: int,
    theta: float = 0,
    color: Optional[str] = None,
    size: Optional[int] = None,
    opacity: Optional[float] = None,
    symbol: Optional[str] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """向内画点阵

    Args:
        n: 每圈点的数量
        m: 圈数
        theta: 旋转角度（弧度）
        color: 点的颜色
        size: 点的大小
        opacity: 透明度
        symbol: 点的形状
        name: 图例名称

    Returns:
        plotly Figure对象
    """
    try:
        fig = go.Figure()

        for i in range(m):
            points = n_points(n, (np.cos(np.pi / n)) ** i, i * (np.pi / n - theta))
            trace_name = f"{name or 'Dots'} {i+1}" if name else f"Layer {i+1}"
            fig.add_trace(
                create_dots_trace(points, color, size, opacity, symbol, trace_name)
            )

        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise DotError(f"Error drawing inner n points array: {str(e)}")


def draw_n_points_array_with_direction(
    n: int,
    m: int,
    direction: Literal["both", "in", "out"] = "both",
    theta: float = 0,
    color: Optional[str] = None,
    size: Optional[int] = None,
    opacity: Optional[float] = None,
    symbol: Optional[str] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """根据方向绘制点阵

    Args:
        n: 每圈点的数量
        m: 圈数
        direction: 方向，可选 "both"/"in"/"out"
        theta: 旋转角度（弧度）
        color: 点的颜色
        size: 点的大小
        opacity: 透明度
        symbol: 点的形状
        name: 图例名称

    Returns:
        plotly Figure对象
    """
    if direction == "both":
        return draw_n_points_array(n, m, theta, color, size, opacity, symbol, name)
    elif direction == "in":
        return draw_n_points_array_inner(
            n, m, theta, color, size, opacity, symbol, name
        )
    elif direction == "out":
        return draw_n_points_array_outer(
            n, m, theta, color, size, opacity, symbol, name
        )
    else:
        raise DotError(f"Invalid direction: {direction}")


def colorful_dots(
    points: List[List[float]],
    colors: List[str],
    size: Optional[int] = None,
    opacity: Optional[float] = None,
    symbol: Optional[str] = None,
) -> go.Figure:
    """绘制彩色点阵

    Args:
        points: 点坐标列表 [[x1, y1], [x2, y2], ...]
        colors: 颜色列表，长度应与points相同
        size: 点的大小
        opacity: 透明度
        symbol: 点的形状

    Returns:
        plotly Figure对象
    """
    try:
        if len(colors) < len(points):
            raise DotError(
                f"Not enough colors provided. Need {len(points)}, got {len(colors)}"
            )

        fig = go.Figure()

        for i, point in enumerate(points):
            fig.add_trace(
                go.Scatter(
                    x=[point[0]],
                    y=[point[1]],
                    mode="markers",
                    marker=dict(
                        color=colors[i],
                        size=size or config.default_size,
                        opacity=opacity or config.opacity,
                        symbol=symbol or config.marker_symbol,
                        line=dict(
                            width=config.marker_line_width,
                            color=config.marker_line_color,
                        ),
                    ),
                    name=f"Dot {i+1}",
                )
            )

        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise DotError(f"Error drawing colorful dots: {str(e)}")


# 导出主要的函数和类
__all__ = [
    "DotConfig",
    "DotError",
    "config",
    "n_points",
    "draw_points",
    "n_points_array",
    "n_points_array_inner",
    "n_points_array_outer",
    "n_points_array_outer_rotate",
    "n_points_array_inner_rotate",
    "draw_n_points_array",
    "draw_n_points_array_outer",
    "draw_n_points_array_inner",
    "draw_n_points_array_with_direction",
    "colorful_dots",
]
