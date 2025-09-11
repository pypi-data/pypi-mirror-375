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
            color=color or config.default_color, width=width or config.line_width
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
        fig.add_trace(
            create_spiral_trace(x, y, color, width, opacity, name or "LogSpiral")
        )
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
        fig.add_trace(
            create_spiral_trace(x, y, color, width, opacity, name or "LogSpiral Out")
        )
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
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """绘制向内对数螺旋线

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
        x, y = _calculate_log_spiral_points(n, a, b, cyc, theta, "in", num_points)
        fig = go.Figure()
        fig.add_trace(
            create_spiral_trace(x, y, color, width, opacity, name or "LogSpiral In")
        )
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing inward log spiral: {str(e)}")


# 多重螺旋线
def n_spiral(
    n: int,
    cyc: float,
    color: str,
    theta: float = 0,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
) -> go.Figure:
    """绘制多重对数螺旋线

    Args:
        n: 螺旋数量和参数
        cyc: 圈数
        color: 线条颜色
        theta: 相位角
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
    """
    try:
        fig = go.Figure()
        for i in range(n):
            sub_fig1 = logSpiral(
                n,
                1,
                1,
                cyc,
                color,
                theta + i * 2 * np.pi / n,
                width,
                opacity,
                num_points,
                f"Spiral {i+1}a",
            )
            sub_fig2 = logSpiral(
                n,
                -1,
                1,
                cyc,
                color,
                theta + i * 2 * np.pi / n,
                width,
                opacity,
                num_points,
                f"Spiral {i+1}b",
            )
            fig.add_traces(sub_fig1.data)
            fig.add_traces(sub_fig2.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing multiple spirals: {str(e)}")


# 旋转螺旋线
def n_spiral_rotate(
    n: int,
    cyc: float,
    color: str,
    alpha: float = 0,
    theta: float = 0,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
) -> go.Figure:
    """绘制旋转多重对数螺旋线

    Args:
        n: 螺旋数量和参数
        cyc: 圈数
        color: 线条颜色
        alpha: 旋转角度
        theta: 相位角
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
    """
    try:
        fig = go.Figure()
        for i in range(n):
            sub_fig1 = logSpiral(
                n,
                1,
                1,
                cyc,
                color,
                alpha + theta + i * 2 * np.pi / n,
                width,
                opacity,
                num_points,
                f"Spiral {i+1}a",
            )
            sub_fig2 = logSpiral(
                n,
                -1,
                1,
                cyc,
                color,
                alpha - theta + i * 2 * np.pi / n,
                width,
                opacity,
                num_points,
                f"Spiral {i+1}b",
            )
            fig.add_traces(sub_fig1.data)
            fig.add_traces(sub_fig2.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing rotated multiple spirals: {str(e)}")


# 向外旋转螺旋线
def n_spiral_rotate_out(
    n: int,
    cyc: float,
    color: str,
    theta: float = 0,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
) -> go.Figure:
    """绘制向外旋转多重对数螺旋线

    Args:
        n: 螺旋数量和参数
        cyc: 圈数
        color: 线条颜色
        theta: 相位角
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
    """
    try:
        fig = go.Figure()
        for i in range(n):
            sub_fig1 = logSpiral_out(
                n,
                1,
                1,
                cyc,
                color,
                theta + i * 2 * np.pi / n,
                width,
                opacity,
                num_points,
                f"Spiral {i+1}a",
            )
            sub_fig2 = logSpiral_out(
                n,
                -1,
                1,
                cyc,
                color,
                -theta + i * 2 * np.pi / n,
                width,
                opacity,
                num_points,
                f"Spiral {i+1}b",
            )
            fig.add_traces(sub_fig1.data)
            fig.add_traces(sub_fig2.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing outward rotated multiple spirals: {str(e)}")


# 向内旋转螺旋线
def n_spiral_rotate_in(
    n: int,
    cyc: float,
    color: str,
    theta: float = 0,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
) -> go.Figure:
    """绘制向内旋转多重对数螺旋线

    Args:
        n: 螺旋数量和参数
        cyc: 圈数
        color: 线条颜色
        theta: 相位角
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
    """
    try:
        fig = go.Figure()
        for i in range(n):
            sub_fig1 = logSpiral_in(
                n,
                1,
                1,
                cyc,
                color,
                theta + i * 2 * np.pi / n,
                width,
                opacity,
                num_points,
                f"Spiral {i+1}a",
            )
            sub_fig2 = logSpiral_in(
                n,
                -1,
                1,
                cyc,
                color,
                -theta + i * 2 * np.pi / n,
                width,
                opacity,
                num_points,
                f"Spiral {i+1}b",
            )
            fig.add_traces(sub_fig1.data)
            fig.add_traces(sub_fig2.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing inward rotated multiple spirals: {str(e)}")


# 画花算法 - 单瓣
def calla_petal(
    n: int,
    cyc: float,
    theta: float,
    color: str,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
) -> go.Figure:
    """绘制花瓣（正反螺旋组合）

    Args:
        n: 螺旋参数
        cyc: 圈数
        theta: 相位角
        color: 线条颜色
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
    """
    try:
        fig = go.Figure()
        sub_fig1 = logSpiral(
            n, 1, 1, cyc * 1.25, color, theta, width, opacity, num_points, "Petal Out"
        )
        sub_fig2 = logSpiral(
            n, -1, 1, cyc * 1.25, color, -theta, width, opacity, num_points, "Petal In"
        )
        fig.add_traces(sub_fig1.data)
        fig.add_traces(sub_fig2.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing calla petal: {str(e)}")


# 画花算法 - 多瓣
def calla_by_petal(
    n: int,
    cyc: float,
    N: int,
    theta: float,
    colors: List[str],
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
) -> go.Figure:
    """绘制多瓣花朵

    Args:
        n: 螺旋参数
        cyc: 圈数
        N: 花瓣数量
        theta: 相位角
        colors: 各花瓣颜色列表
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
    """
    try:
        if len(colors) < N:
            raise SpiralError(
                f"Not enough colors provided. Need {N}, got {len(colors)}"
            )

        fig = go.Figure()
        for i in range(N):
            sub_fig = calla_petal(
                n, cyc, theta + i * 2 * np.pi / N, colors[i], width, opacity, num_points
            )
            fig.add_traces(sub_fig.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing calla flower: {str(e)}")


# 罗丹线圈
def rodincoil(
    R: float,
    r: float,
    n: int,
    color: str = "b",
    theta: float = 0,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制罗丹线圈

    Args:
        R: 大圆半径
        r: 小圆半径
        n: 小圆数量
        color: 线条颜色
        theta: 相位角
        width: 线条宽度
        opacity: 透明度
    """
    try:
        fig = go.Figure()
        for i in range(n):
            angle = i * 2 * np.pi / n + theta
            center = (R * np.cos(angle), R * np.sin(angle))
            sub_fig = circle(
                center=center,
                radius=r,
                color=color,
                width=width,
                opacity=opacity,
                name=f"Circle {i+1}",
            )
            fig.add_traces(sub_fig.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing rodin coil: {str(e)}")


# 罗丹线圈带颜色
def rodincoil_colorful(
    R: float,
    r: float,
    n: int,
    colors: List[str],
    theta: float = 0,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制彩色罗丹线圈

    Args:
        R: 大圆半径
        r: 小圆半径
        n: 小圆数量
        colors: 各小圆颜色列表
        theta: 相位角
        width: 线条宽度
        opacity: 透明度
    """
    try:
        if len(colors) < n:
            raise SpiralError(
                f"Not enough colors provided. Need {n}, got {len(colors)}"
            )

        fig = go.Figure()
        for i in range(n):
            angle = i * 2 * np.pi / n + theta
            center = (R * np.cos(angle), R * np.sin(angle))
            sub_fig = circle(
                center=center,
                radius=r,
                color=colors[i],
                width=width,
                opacity=opacity,
                name=f"Circle {i+1}",
            )
            fig.add_traces(sub_fig.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing colorful rodin coil: {str(e)}")


# 导出主要的函数和类
__all__ = [
    "SpiralConfig",
    "SpiralError",
    "config",
    "logSpiral",
    "logSpiral_out",
    "logSpiral_in",
    "n_spiral",
    "n_spiral_rotate",
    "n_spiral_rotate_out",
    "n_spiral_rotate_in",
    "calla_petal",
    "calla_by_petal",
    "rodincoil",
    "rodincoil_colorful",
]
