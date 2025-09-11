"""
圆形图案配置模块

此模块提供了用于创建和配置圆形图案的基本功能。
"""

from typing import Tuple, List, Optional, Dict, Any
import numpy as np
import plotly.graph_objects as go


class CircleError(Exception):
    """圆形图案相关的自定义异常"""

    pass


class CircleConfig:
    """圆形图案的配置管理类"""

    def __init__(self):
        self.num_points = 100  # 圆上的点数
        self.line_width = 2  # 线条宽度
        self.opacity = 1.0  # 透明度
        self.show_center = True  # 是否显示圆心

    @property
    def layout(self) -> Dict[str, Any]:
        """获取默认布局配置"""
        return {
            "showlegend": False,
            "margin": dict(l=20, r=20, t=20, b=20),
            "yaxis": {"scaleanchor": "x", "scaleratio": 1},
        }


# 创建全局配置实例
config = CircleConfig()


def circle(
    center: Tuple[float, float],
    radius: float,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """创建单个圆形

    Args:
        center: 圆心坐标 (x, y)
        radius: 圆的半径
        color: 圆的颜色
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
        name: 图形名称
    """
    try:
        # 使用传入的参数或默认配置
        _num_points = num_points or config.num_points
        _width = width or config.line_width
        _opacity = opacity or config.opacity

        # 生成圆上的点
        t = np.linspace(0, 2 * np.pi, _num_points)
        x = center[0] + radius * np.cos(t)
        y = center[1] + radius * np.sin(t)

        # 创建图形
        fig = go.Figure()

        # 添加圆形轨迹
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                line=dict(color=color, width=_width),
                opacity=_opacity,
                name=name,
                showlegend=False,
            )
        )

        # 如果需要显示圆心
        if config.show_center:
            fig.add_trace(
                go.Scatter(
                    x=[center[0]],
                    y=[center[1]],
                    mode="markers",
                    marker=dict(color=color, size=4),
                    showlegend=False,
                )
            )

        # 更新布局
        fig.update_layout(**config.layout)
        return fig

    except Exception as e:
        raise CircleError(f"Error drawing circle: {str(e)}")


def concentric_circles(
    center: Tuple[float, float],
    n: int,
    d: float,
    radius: float = 1,
    direction: str = "both",
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """创建同心圆组（等差）

    Args:
        center: 圆心坐标 (x, y)
        n: 圆的数量
        d: 相邻圆的半径差
        radius: 基准半径
        direction: 圆的方向，可选 "both"/"in"/"out"
        color: 圆的颜色
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
        name: 图形名称
    """
    try:
        fig = go.Figure()

        # 根据方向确定半径列表
        if direction == "both":
            radii = [radius + i * d for i in range(-n, n + 1)]
        elif direction == "out":
            radii = [radius + i * d for i in range(n)]
        elif direction == "in":
            radii = [radius - i * d for i in range(n)]
        else:
            raise ValueError(f"Invalid direction: {direction}")

        # 创建每个圆
        for r in radii:
            sub_fig = circle(
                center=center,
                radius=abs(r),  # 使用绝对值确保半径为正
                color=color,
                width=width,
                opacity=opacity,
                num_points=num_points,
                name=name,
            )
            fig.add_traces(sub_fig.data)

        # 更新布局
        fig.update_layout(**config.layout)
        return fig

    except Exception as e:
        raise CircleError(f"Error drawing concentric circles: {str(e)}")


def concentric_circles_geometric(
    center: Tuple[float, float],
    n: int,
    q: float,
    radius: float = 1,
    direction: str = "both",
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """创建同心圆组（等比）

    Args:
        center: 圆心坐标 (x, y)
        n: 圆的数量
        q: 相邻圆的半径比
        radius: 基准半径
        direction: 圆的方向，可选 "both"/"in"/"out"
        color: 圆的颜色
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
        name: 图形名称
    """
    try:
        fig = go.Figure()

        # 根据方向确定半径列表
        if direction == "both":
            radii = [radius * (q**i) for i in range(-n, n + 1)]
        elif direction == "out":
            radii = [radius * (q**i) for i in range(n)]
        elif direction == "in":
            radii = [radius * (q**-i) for i in range(n)]
        else:
            raise ValueError(f"Invalid direction: {direction}")

        # 创建每个圆
        for r in radii:
            sub_fig = circle(
                center=center,
                radius=r,
                color=color,
                width=width,
                opacity=opacity,
                num_points=num_points,
                name=name,
            )
            fig.add_traces(sub_fig.data)

        # 更新布局
        fig.update_layout(**config.layout)
        return fig

    except Exception as e:
        raise CircleError(f"Error drawing geometric concentric circles: {str(e)}")


# 导出主要的函数和类
__all__ = [
    "CircleConfig",
    "CircleError",
    "config",
    "circle",
    "concentric_circles",
    "concentric_circles_geometric",
]
