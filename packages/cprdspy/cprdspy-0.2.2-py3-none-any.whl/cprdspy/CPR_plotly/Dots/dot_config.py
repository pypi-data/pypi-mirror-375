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
    """创建点阵的轨迹对象"""
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
    """生成半径为radius的圆上均匀分布的n个点"""
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
    """绘制点阵"""
    try:
        fig = go.Figure()
        fig.add_trace(create_dots_trace(points, color, size, opacity, symbol, name))
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise DotError(f"Error drawing points: {str(e)}")


def n_points_array(
    n: int, m: int, direction: Literal["both", "in", "out"] = "both", theta: float = 0
) -> List[List[float]]:
    """生成点阵

    Args:
        n: 每圈点的数量
        m: 圈数
        direction: 生成方向，可选 "both"/"in"/"out"
        theta: 旋转角度（弧度）

    Returns:
        点坐标列表 [[x1, y1], [x2, y2], ...]
    """
    try:
        points = []

        if direction in ["both", "in"]:
            for i in range(m):
                points.extend(
                    n_points(n, (np.cos(np.pi / n)) ** i, i * (np.pi / n + theta))
                )

        if direction in ["both", "out"]:
            for i in range(m):
                points.extend(
                    n_points(n, (np.cos(np.pi / n)) ** (-i), i * (np.pi / n + theta))
                )

        return points
    except Exception as e:
        raise DotError(f"Error generating n points array: {str(e)}")


# 为了保持向后兼容性，提供原有函数名的别名
def n_points_array_inner(*args, **kwargs):
    """向内生成点阵（兼容函数）"""
    return n_points_array(*args, direction="in", **kwargs)


def n_points_array_outer(*args, **kwargs):
    """向外生成点阵（兼容函数）"""
    return n_points_array(*args, direction="out", **kwargs)


def n_points_array_rotate(
    n: int,
    m: int,
    direction: Literal["both", "in", "out"] = "both",
    alpha: float = 0,
    theta: float = 0,
) -> List[List[float]]:
    """旋转生成点阵

    Args:
        n: 每圈点的数量
        m: 圈数
        direction: 生成方向，可选 "both"/"in"/"out"
        alpha: 整体旋转角度（弧度）
        theta: 每圈额外旋转角度（弧度）

    Returns:
        点坐标列表 [[x1, y1], [x2, y2], ...]
    """
    try:
        points = []

        if direction in ["both", "in"]:
            for i in range(m):
                points.extend(
                    n_points(
                        n, (np.cos(np.pi / n)) ** i, alpha + i * (np.pi / n + theta)
                    )
                )

        if direction in ["both", "out"]:
            for i in range(m):
                points.extend(
                    n_points(
                        n, (np.cos(np.pi / n)) ** (-i), alpha + i * (np.pi / n + theta)
                    )
                )

        return points
    except Exception as e:
        raise DotError(f"Error generating rotated n points array: {str(e)}")


# 为了保持向后兼容性，提供原有函数名的别名
def n_points_array_inner_rotate(*args, **kwargs):
    """向内旋转生成点阵（兼容函数）"""
    return n_points_array_rotate(*args, direction="in", **kwargs)


def n_points_array_outer_rotate(*args, **kwargs):
    """向外旋转生成点阵（兼容函数）"""
    return n_points_array_rotate(*args, direction="out", **kwargs)


def draw_n_points_array(
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
    """画点阵

    Args:
        n: 每圈点的数量
        m: 圈数
        direction: 绘制方向，可选 "both"/"in"/"out"
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

        if direction in ["both", "in"]:
            for i in range(m):
                points = n_points(n, (np.cos(np.pi / n)) ** i, i * (np.pi / n + theta))
                trace_name = f"{name or 'Dots'} Inner {i+1}" if name else f"Inner {i+1}"
                fig.add_trace(
                    create_dots_trace(points, color, size, opacity, symbol, trace_name)
                )

        if direction in ["both", "out"]:
            for i in range(m):
                points = n_points(
                    n, (np.cos(np.pi / n)) ** (-i), i * (np.pi / n + theta)
                )
                trace_name = f"{name or 'Dots'} Outer {i+1}" if name else f"Outer {i+1}"
                fig.add_trace(
                    create_dots_trace(points, color, size, opacity, symbol, trace_name)
                )

        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise DotError(f"Error drawing n points array: {str(e)}")


# 为了保持向后兼容性，提供原有函数名的别名
def draw_n_points_array_inner(*args, **kwargs):
    """向内画点阵（兼容函数）"""
    return draw_n_points_array(*args, direction="in", **kwargs)


def draw_n_points_array_outer(*args, **kwargs):
    """向外画点阵（兼容函数）"""
    return draw_n_points_array(*args, direction="out", **kwargs)


def colorful_dots(
    points: List[List[float]],
    colors: List[str],
    size: Optional[int] = None,
    opacity: Optional[float] = None,
    symbol: Optional[str] = None,
) -> go.Figure:
    """绘制彩色点阵"""
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
    "n_points_array_rotate",
    "n_points_array_inner_rotate",
    "n_points_array_outer_rotate",
    "draw_n_points_array",
    "draw_n_points_array_inner",
    "draw_n_points_array_outer",
    "colorful_dots",
]
