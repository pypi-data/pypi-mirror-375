from typing import Tuple, List, Optional, Union, Dict, Any, Literal
import numpy as np
import plotly.graph_objects as go
from functools import lru_cache
from cprdspy.CPR_plotly.Circles.circle_config import circle


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
    symmetry: bool,
    cyc: float,
    theta: float = 0,
    direction: Literal["both", "in", "out"] = "both",
    num_points: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """计算对数螺旋线上的点坐标（带缓存）"""
    _num_points = num_points or config.num_points

    # 根据方向设置时间范围
    if direction == "both":
        t = np.linspace(-cyc * 2 * np.pi, cyc * 2 * np.pi, _num_points)
    elif direction == "out":
        t = np.linspace(0, cyc * 2 * np.pi, _num_points)
    elif direction == "in":
        t = np.linspace(0, -cyc * 2 * np.pi, _num_points)
    else:
        raise SpiralError(f"Invalid direction: {direction}")

    # symmetry决定是否对称（True为对称，False为不对称）
    a = 1 if symmetry else -1
    b = 1  # y方向系数保持为1

    x = a * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.cos(t + theta)
    y = b * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.sin(t + theta)
    return x, y


def logSpiral(
    n: int,
    cyc: float,
    color: str = "blue",
    theta: float = 0,
    direction: Literal["both", "in", "out"] = "both",
    symmetry: bool = True,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
    name: Optional[str] = None,
) -> go.Figure:
    """绘制对数螺旋线

    Args:
        n: 螺旋参数
        cyc: 圈数
        color: 线条颜色
        theta: 相位角
        direction: 螺旋方向，可选 "both"/"in"/"out"
        symmetry: 是否对称
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
        name: 图例名称
    """
    try:
        x, y = _calculate_log_spiral_points(
            n, symmetry, cyc, theta, direction, num_points
        )
        fig = go.Figure()
        fig.add_trace(create_spiral_trace(x, y, color, width, opacity, name))
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing log spiral: {str(e)}")


# 为了保持向后兼容性，提供原有函数名的别名
def logSpiral_out(*args, **kwargs):
    """向外对数螺旋线（兼容函数）"""
    return logSpiral(*args, direction="out", **kwargs)


def logSpiral_in(*args, **kwargs):
    """向内对数螺旋线（兼容函数）"""
    return logSpiral(*args, direction="in", **kwargs)


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
            phase = theta + i * 2 * np.pi / n
            # 对称螺旋
            sub_fig1 = logSpiral(
                n,
                cyc,
                color,
                phase,
                symmetry=True,
                width=width,
                opacity=opacity,
                num_points=num_points,
                name=f"Spiral {i+1}a",
            )
            # 不对称螺旋
            sub_fig2 = logSpiral(
                n,
                cyc,
                color,
                phase,
                symmetry=False,
                width=width,
                opacity=opacity,
                num_points=num_points,
                name=f"Spiral {i+1}b",
            )
            fig.add_traces(sub_fig1.data)
            fig.add_traces(sub_fig2.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing multiple spirals: {str(e)}")


def n_spiral_rotate(
    n: int,
    cyc: float,
    color: str,
    alpha: float = 0,
    theta: float = 0,
    direction: Literal["both", "in", "out"] = "both",
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
        direction: 螺旋方向，可选 "both"/"in"/"out"
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
    """
    try:
        fig = go.Figure()
        for i in range(n):
            phase1 = alpha + theta + i * 2 * np.pi / n
            phase2 = alpha - theta + i * 2 * np.pi / n
            # 对称螺旋
            sub_fig1 = logSpiral(
                n,
                cyc,
                color,
                phase1,
                direction=direction,
                symmetry=True,
                width=width,
                opacity=opacity,
                num_points=num_points,
                name=f"Spiral {i+1}a",
            )
            # 不对称螺旋
            sub_fig2 = logSpiral(
                n,
                cyc,
                color,
                phase2,
                direction=direction,
                symmetry=False,
                width=width,
                opacity=opacity,
                num_points=num_points,
                name=f"Spiral {i+1}b",
            )
            fig.add_traces(sub_fig1.data)
            fig.add_traces(sub_fig2.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing rotated multiple spirals: {str(e)}")


# 为了保持向后兼容性，提供原有函数名的别名
def n_spiral_rotate_out(*args, **kwargs):
    """向外旋转多重对数螺旋线（兼容函数）"""
    return n_spiral_rotate(*args, direction="out", **kwargs)


def n_spiral_rotate_in(*args, **kwargs):
    """向内旋转多重对数螺旋线（兼容函数）"""
    return n_spiral_rotate(*args, direction="in", **kwargs)


def chrysanthemum_petal(
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
        # 对称螺旋
        sub_fig1 = logSpiral(
            n,
            cyc * 1.25,
            color,
            theta,
            symmetry=True,
            width=width,
            opacity=opacity,
            num_points=num_points,
            name="Petal Out",
        )
        # 不对称螺旋
        sub_fig2 = logSpiral(
            n,
            cyc * 1.25,
            color,
            -theta,
            symmetry=False,
            width=width,
            opacity=opacity,
            num_points=num_points,
            name="Petal In",
        )
        fig.add_traces(sub_fig1.data)
        fig.add_traces(sub_fig2.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing chrysanthemum petal: {str(e)}")


def chrysanthemum_by_petal(
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
            sub_fig = chrysanthemum_petal(
                n, cyc, theta + i * 2 * np.pi / N, colors[i], width, opacity, num_points
            )
            fig.add_traces(sub_fig.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise SpiralError(f"Error drawing chrysanthemum flower: {str(e)}")


def rodincoil(
    R: float,
    r: float,
    n: int,
    color: str = "blue",
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
    "chrysanthemum_petal",
    "chrysanthemum_by_petal",
    "rodincoil",
    "rodincoil_colorful",
]
