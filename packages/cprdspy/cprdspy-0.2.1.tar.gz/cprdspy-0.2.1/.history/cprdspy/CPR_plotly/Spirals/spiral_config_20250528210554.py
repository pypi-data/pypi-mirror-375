from typing import Tuple, List, Optional, Union, Dict, Any
import numpy as np
import plotly.graph_objects as go
from functools import lru_cache
from ..Circles.circle_config import circle


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
            color=color or config.default_color, 
            width=width or config.line_width
        ),
        opacity=opacity or config.opacity,
        name=name or "Spiral",
    )


@lru_cache(maxsize=128)
def _calculate_log_spiral_points(
    n: int,
    a: float,
    b: float,
    cyc: float,
    theta: float = 0,
    direction: str = "both",
    num_points: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """计算对数螺旋线上的点坐标（带缓存）"""
    _num_points = num_points or config.num_points
    
    if direction == "both":
        t = np.linspace(-cyc * 2 * np.pi, cyc * 2 * np.pi, _num_points)
    elif direction == "out":
        t = np.linspace(0, cyc * 2 * np.pi, _num_points)
    elif direction == "in":
        t = np.linspace(0, -cyc * 2 * np.pi, _num_points)
    else:
        raise SpiralError(f"Invalid direction: {direction}")
    
    x = a * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.cos(t + theta)
    y = b * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.sin(t + theta)
    return x, y


# 螺旋线
def logSpiral(
    n: int, 
    a: float, 
    b: float, 
    cyc: float, 
    color: str = "b", 
    theta: float = 0,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """绘制对数螺旋线（双向）
    
    Args:
        n: 螺旋参数
        a: x方向系数
        b: y方向系数
        cyc: 圈数
        color: 线条颜色
        theta: 相位角
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
        name: 图例名称
    """
    try:
        x, y = _calculate_log_spiral_points(n, a, b, cyc, theta, "both", num_points)
        fig = go.Figure()
        fig.add_trace(create_spiral_trace(x, y, color, width, opacity, name or "LogSpiral"))
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing log spiral: {str(e)}")


# 向外螺旋线
def logSpiral_out(
    n: int, 
    a: float, 
    b: float, 
    cyc: float, 
    color: str = "b", 
    theta: float = 0,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """绘制向外对数螺旋线
    
    Args:
        n: 螺旋参数
        a: x方向系数
        b: y方向系数
        cyc: 圈数
        color: 线条颜色
        theta: 相位角
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
        name: 图例名称
    """
    try:
        x, y = _calculate_log_spiral_points(n, a, b, cyc, theta, "out", num_points)
        fig = go.Figure()
        fig.add_trace(create_spiral_trace(x, y, color, width, opacity, name or "LogSpiral Out"))
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing outward log spiral: {str(e)}")


# 向内螺旋线
def logSpiral_in(
    n: int, 
    a: float, 
    b: float, 
    cyc: float, 
    color: str = "b", 
    theta: float = 0,
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
