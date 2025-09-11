from typing import Tuple, List, Optional, Union, Dict, Any
import numpy as np
import plotly.graph_objects as go
from functools import lru_cache


class CircleError(Exception):
    """圆形绘制相关的自定义异常"""

    pass


class CircleConfig:
    """圆形绘制的配置管理类"""

    def __init__(self):
        self.num_points = 10000  # 默认采样点数
        self.default_color = "#1f77b4"  # 默认蓝色
        self.line_width = 2
        self.opacity = 1.0
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


@lru_cache(maxsize=128)
def _calculate_circle_points(
    center: Tuple[float, float], radius: float, num_points: int = None
) -> Tuple[np.ndarray, np.ndarray]:
    """计算圆上的点坐标（带缓存）"""
    if radius <= 0:
        raise CircleError("Radius must be positive")

    num_points = num_points or config.num_points
    theta = np.linspace(0, 2 * np.pi, num_points)
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    return x, y


def create_circle_trace(
    x: np.ndarray,
    y: np.ndarray,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    name: Optional[str] = None,
) -> go.Scatter:
    """创建圆形的轨迹对象"""
    return go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(
            color=color or config.default_color, width=width or config.line_width
        ),
        opacity=opacity or config.opacity,
        name=name or "Circle",
    )


def circle(
    center: Union[List[float], Tuple[float, float]],
    radius: float,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """绘制单个圆"""
    try:
        x, y = _calculate_circle_points(tuple(center), radius)
        fig = go.Figure()

        if config.show_center:
            fig.add_trace(
                go.Scatter(
                    x=[center[0]],
                    y=[center[1]],
                    mode="markers",
                    marker=dict(color=color or config.default_color),
                    name=f"{name or 'Circle'} center",
                )
            )

        fig.add_trace(create_circle_trace(x, y, color, width, opacity, name))
        fig.update_layout(**config.layout)
        return fig

    except Exception as e:
        raise CircleError(f"Error drawing circle: {str(e)}")


def circle_from_point(
    center: Union[List[float], Tuple[float, float]],
    point: Union[List[float], Tuple[float, float]],
    **kwargs,
) -> go.Figure:
    """通过圆心和圆上一点绘制圆"""
    radius = np.sqrt((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2)
    return circle(center, radius, **kwargs)


def concentric_circles(
    center: Union[List[float], Tuple[float, float]],
    n: int,
    d: float,
    radius: float,
    direction: str = "both",
    **kwargs,
) -> go.Figure:
    """绘制等差同心圆

    Args:
        center: 圆心坐标
        n: 圆的数量
        d: 半径差值
        radius: 基准半径
        direction: 扩展方向，可选 "both"/"in"/"out"
    """
    try:
        fig = go.Figure()

        if direction in ["both", "in"]:
            for i in range(n):
                r = radius - i * d
                if r > 0:
                    x, y = _calculate_circle_points(tuple(center), r)
                    fig.add_trace(create_circle_trace(x, y, **kwargs))

        if direction in ["both", "out"]:
            for i in range(n):
                r = radius + i * d
                x, y = _calculate_circle_points(tuple(center), r)
                fig.add_trace(create_circle_trace(x, y, **kwargs))

        # 添加基准圆
        x, y = _calculate_circle_points(tuple(center), radius)
        fig.add_trace(create_circle_trace(x, y, **kwargs))

        fig.update_layout(**config.layout)
        return fig

    except Exception as e:
        raise CircleError(f"Error drawing concentric circles: {str(e)}")


def concentric_circles_geometric(
    center: Union[List[float], Tuple[float, float]],
    n: int,
    q: float,
    radius: float,
    direction: str = "both",
    **kwargs,
) -> go.Figure:
    """绘制等比同心圆

    Args:
        center: 圆心坐标
        n: 圆的数量
        q: 半径比例系数
        radius: 基准半径
        direction: 扩展方向，可选 "both"/"in"/"out"
    """
    try:
        if q <= 0:
            raise CircleError("Ratio q must be positive")

        fig = go.Figure()

        if direction in ["both", "in"]:
            for i in range(n):
                r = radius / (q**i)
                x, y = _calculate_circle_points(tuple(center), r)
                fig.add_trace(create_circle_trace(x, y, **kwargs))

        if direction in ["both", "out"]:
            for i in range(n):
                r = radius * (q**i)
                x, y = _calculate_circle_points(tuple(center), r)
                fig.add_trace(create_circle_trace(x, y, **kwargs))

        # 添加基准圆
        x, y = _calculate_circle_points(tuple(center), radius)
        fig.add_trace(create_circle_trace(x, y, **kwargs))

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
    "circle_from_point",
    "concentric_circles",
    "concentric_circles_geometric",
]
