from typing import Tuple, List, Optional, Union, Dict, Any
import numpy as np
import plotly.graph_objects as go
from functools import lru_cache


class SpiralError(Exception):
    """螺旋线绘制相关的自定义异常"""

    pass


class SpiralConfig:
    """螺旋线绘制的配置管理类"""

    def __init__(self):
        self.num_points = 10000  # 默认采样点数
        self.default_color = "#1f77b4"  # 默认蓝色
        self.line_width = 2
        self.opacity = 1.0
        self.show_center = False  # 是否显示螺旋起点
        self.rotation_direction = "clockwise"  # 旋转方向：clockwise或counterclockwise
        self.start_theta = 0  # 起始角度
        self.end_theta = 6 * np.pi  # 结束角度（默认3圈）

    @property
    def layout(self) -> Dict[str, Any]:
        """获取默认布局配置"""
        return {
            "showlegend": True,
            "margin": dict(l=20, r=20, t=20, b=20),
            "yaxis": {"scaleanchor": "x", "scaleratio": 1},
        }


# 创建全局配置实例
config = SpiralConfig()


@lru_cache(maxsize=128)
def _calculate_arithmetic_spiral_points(
    center: Tuple[float, float],
    a: float,
    b: float,
    start_theta: Optional[float] = None,
    end_theta: Optional[float] = None,
    num_points: Optional[int] = None,
    direction: Optional[str] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """计算等差螺旋线上的点坐标（带缓存）

    Args:
        center: 螺旋中心点坐标
        a: 初始半径
        b: 每圈增加的半径
        start_theta: 起始角度
        end_theta: 结束角度
        num_points: 采样点数
        direction: 旋转方向
    """
    if b == 0:
        raise SpiralError("Parameter b must not be zero")

    _start_theta = start_theta if start_theta is not None else config.start_theta
    _end_theta = end_theta if end_theta is not None else config.end_theta
    _num_points = num_points or config.num_points
    _direction = direction or config.rotation_direction

    theta = np.linspace(_start_theta, _end_theta, _num_points)
    if _direction == "counterclockwise":
        theta = -theta

    r = a + b * theta / (2 * np.pi)
    x = center[0] + r * np.cos(theta)
    y = center[1] + r * np.sin(theta)
    return x, y


@lru_cache(maxsize=128)
def _calculate_geometric_spiral_points(
    center: Tuple[float, float],
    a: float,
    b: float,
    start_theta: Optional[float] = None,
    end_theta: Optional[float] = None,
    num_points: Optional[int] = None,
    direction: Optional[str] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """计算等比螺旋线上的点坐标（带缓存）

    Args:
        center: 螺旋中心点坐标
        a: 初始半径
        b: 指数增长率
        start_theta: 起始角度
        end_theta: 结束角度
        num_points: 采样点数
        direction: 旋转方向
    """
    if a <= 0 or b <= 0:
        raise SpiralError("Parameters a and b must be positive")

    _start_theta = start_theta if start_theta is not None else config.start_theta
    _end_theta = end_theta if end_theta is not None else config.end_theta
    _num_points = num_points or config.num_points
    _direction = direction or config.rotation_direction

    theta = np.linspace(_start_theta, _end_theta, _num_points)
    if _direction == "counterclockwise":
        theta = -theta

    r = a * np.exp(b * theta)
    x = center[0] + r * np.cos(theta)
    y = center[1] + r * np.sin(theta)
    return x, y


def create_spiral_trace(
    x: np.ndarray,
    y: np.ndarray,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    name: Optional[str] = None,
) -> go.Scatter:
    """创建螺旋线的轨迹对象"""
    return go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(
            color=color or config.default_color, width=width or config.line_width
        ),
        opacity=opacity or config.opacity,
        name=name or "Spiral",
    )


def arithmetic_spiral(
    center: Union[List[float], Tuple[float, float]],
    a: float,
    b: float,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    name: Optional[str] = None,
    start_theta: Optional[float] = None,
    end_theta: Optional[float] = None,
    num_points: Optional[int] = None,
    direction: Optional[str] = None,
) -> go.Figure:
    """绘制等差螺旋线

    Args:
        center: 螺旋中心点坐标
        a: 初始半径
        b: 每圈增加的半径
        color: 线条颜色
        width: 线条宽度
        opacity: 透明度
        name: 图例名称
        start_theta: 起始角度
        end_theta: 结束角度
        num_points: 采样点数
        direction: 旋转方向，可选 "clockwise"/"counterclockwise"
    """
    try:
        x, y = _calculate_arithmetic_spiral_points(
            tuple(center), a, b, start_theta, end_theta, num_points, direction
        )
        fig = go.Figure()

        if config.show_center:
            fig.add_trace(
                go.Scatter(
                    x=[center[0]],
                    y=[center[1]],
                    mode="markers",
                    marker=dict(color=color or config.default_color),
                    name=f"{name or 'Spiral'} center",
                )
            )

        fig.add_trace(create_spiral_trace(x, y, color, width, opacity, name))
        fig.update_layout(**config.layout)
        return fig

    except Exception as e:
        raise SpiralError(f"Error drawing arithmetic spiral: {str(e)}")


def geometric_spiral(
    center: Union[List[float], Tuple[float, float]],
    a: float,
    b: float,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    name: Optional[str] = None,
    start_theta: Optional[float] = None,
    end_theta: Optional[float] = None,
    num_points: Optional[int] = None,
    direction: Optional[str] = None,
) -> go.Figure:
    """绘制等比螺旋线

    Args:
        center: 螺旋中心点坐标
        a: 初始半径
        b: 指数增长率
        color: 线条颜色
        width: 线条宽度
        opacity: 透明度
        name: 图例名称
        start_theta: 起始角度
        end_theta: 结束角度
        num_points: 采样点数
        direction: 旋转方向，可选 "clockwise"/"counterclockwise"
    """
    try:
        x, y = _calculate_geometric_spiral_points(
            tuple(center), a, b, start_theta, end_theta, num_points, direction
        )
        fig = go.Figure()

        if config.show_center:
            fig.add_trace(
                go.Scatter(
                    x=[center[0]],
                    y=[center[1]],
                    mode="markers",
                    marker=dict(color=color or config.default_color),
                    name=f"{name or 'Spiral'} center",
                )
            )

        fig.add_trace(create_spiral_trace(x, y, color, width, opacity, name))
        fig.update_layout(**config.layout)
        return fig

    except Exception as e:
        raise SpiralError(f"Error drawing geometric spiral: {str(e)}")


def multi_arithmetic_spiral(
    center: Union[List[float], Tuple[float, float]],
    a: float,
    b: float,
    n: int,
    phase_shift: float = 2 * np.pi / 4,  # 默认相位差为90度
    **kwargs,
) -> go.Figure:
    """绘制多重等差螺旋线

    Args:
        center: 螺旋中心点坐标
        a: 初始半径
        b: 每圈增加的半径
        n: 螺旋线的数量
        phase_shift: 相邻螺旋线之间的相位差
        **kwargs: 传递给arithmetic_spiral的其他参数
    """
    try:
        fig = go.Figure()

        for i in range(n):
            start_theta = (
                kwargs.pop("start_theta", config.start_theta) + i * phase_shift
            )
            sub_fig = arithmetic_spiral(
                center=center,
                a=a,
                b=b,
                start_theta=start_theta,
                name=f"Spiral {i+1}",
                **kwargs,
            )
            fig.add_traces(sub_fig.data)

        fig.update_layout(**config.layout)
        return fig

    except Exception as e:
        raise SpiralError(f"Error drawing multi arithmetic spiral: {str(e)}")


def multi_geometric_spiral(
    center: Union[List[float], Tuple[float, float]],
    a: float,
    b: float,
    n: int,
    phase_shift: float = 2 * np.pi / 4,  # 默认相位差为90度
    **kwargs,
) -> go.Figure:
    """绘制多重等比螺旋线

    Args:
        center: 螺旋中心点坐标
        a: 初始半径
        b: 指数增长率
        n: 螺旋线的数量
        phase_shift: 相邻螺旋线之间的相位差
        **kwargs: 传递给geometric_spiral的其他参数
    """
    try:
        fig = go.Figure()

        for i in range(n):
            start_theta = (
                kwargs.pop("start_theta", config.start_theta) + i * phase_shift
            )
            sub_fig = geometric_spiral(
                center=center,
                a=a,
                b=b,
                start_theta=start_theta,
                name=f"Spiral {i+1}",
                **kwargs,
            )
            fig.add_traces(sub_fig.data)

        fig.update_layout(**config.layout)
        return fig

    except Exception as e:
        raise SpiralError(f"Error drawing multi geometric spiral: {str(e)}")


# 导出主要的函数和类
__all__ = [
    "SpiralConfig",
    "SpiralError",
    "config",
    "arithmetic_spiral",
    "geometric_spiral",
    "multi_arithmetic_spiral",
    "multi_geometric_spiral",
]
