from typing import Tuple, List, Optional, Union, Dict, Any
import numpy as np
import plotly.graph_objects as go
from ..Circles.circle_config import (
    circle,
    concentric_circles,
    concentric_circles_geometric,
    CircleConfig,
    config as circle_config,
)


class WaveError(Exception):
    """波形绘制相关的自定义异常"""

    pass


class WaveConfig:
    """波形绘制的配置管理类"""

    def __init__(self):
        self.default_color = "#1f77b4"  # 默认蓝色
        self.center_color = "#2ca02c"  # 中心点默认颜色
        self.num_points = circle_config.num_points
        self.line_width = circle_config.line_width
        self.opacity = circle_config.opacity
        self.show_center = circle_config.show_center

    @property
    def layout(self) -> Dict[str, Any]:
        """获取默认布局配置"""
        return {
            "showlegend": False,
            "margin": dict(l=20, r=20, t=20, b=20),
            "yaxis": {"scaleanchor": "x", "scaleratio": 1},
        }


# 创建全局配置实例
config = WaveConfig()


def _calculate_wave_points(P: int, theta: float = 0) -> List[Tuple[float, float]]:
    """计算波形上的点的位置"""
    points = []
    for i in range(P + 1):
        angle = i * 2 * np.pi / P + np.pi / 2 + theta
        points.append((np.cos(angle), np.sin(angle)))
    return points


def wave_circle_arithmetic(
    A: float,
    F: int,
    P: int,
    color: Optional[str] = None,
    theta: float = 0,
    R: float = 1,
    direction: str = "both",
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
    show_center: Optional[bool] = None,
) -> go.Figure:
    """绘制等差圆形波

    Args:
        A: 波的振幅（圆的半径差）
        F: 波的频率（圆的数量）
        P: 波的周期（点的数量）
        color: 波的颜色
        theta: 波的相位
        R: 基准半径
        direction: 波的方向，可选 "both"/"in"/"out"
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
        show_center: 是否显示圆心
    """
    try:
        # 使用传入的参数或默认配置
        _width = width or config.line_width
        _opacity = opacity or config.opacity
        _num_points = num_points or config.num_points
        _show_center = show_center if show_center is not None else config.show_center

        # 临时保存原始配置
        original_show_center = config.show_center
        original_num_points = config.num_points

        # 应用当前配置
        config.show_center = _show_center
        config.num_points = _num_points

        fig = concentric_circles(
            center=(0, 0),
            n=F,
            d=A,
            radius=R,
            direction=direction,
            color=config.center_color,
            width=_width,
            opacity=_opacity,
            name="Center Wave",
        )

        wave_points = _calculate_wave_points(P, theta)
        for point in wave_points:
            sub_fig = concentric_circles(
                center=point,
                n=F,
                d=A,
                radius=R,
                direction=direction,
                color=color or config.default_color,
                width=_width,
                opacity=_opacity,
                name="Wave",
            )
            fig.add_traces(sub_fig.data)

        # 恢复原始配置
        config.show_center = original_show_center
        config.num_points = original_num_points

        fig.update_layout(**config.layout)
        return fig

    except Exception as e:
        raise WaveError(f"Error drawing arithmetic wave: {str(e)}")


def wave_circle_geometric(
    A: float,
    F: int,
    P: int,
    color: Optional[str] = None,
    theta: float = 0,
    R: float = 1,
    direction: str = "both",
    width: Optional[float] = None,
    opacity: Optional[float] = None,
    num_points: Optional[int] = None,
    show_center: Optional[bool] = None,
) -> go.Figure:
    """绘制等比圆形波

    Args:
        A: 波的振幅（圆的半径比）
        F: 波的频率（圆的数量）
        P: 波的周期（点的数量）
        color: 波的颜色
        theta: 波的相位
        R: 基准半径
        direction: 波的方向，可选 "both"/"in"/"out"
        width: 线条宽度
        opacity: 透明度
        num_points: 采样点数
        show_center: 是否显示圆心
    """
    try:
        # 使用传入的参数或默认配置
        _width = width or config.line_width
        _opacity = opacity or config.opacity
        _num_points = num_points or config.num_points
        _show_center = show_center if show_center is not None else config.show_center

        # 临时保存原始配置
        original_show_center = config.show_center
        original_num_points = config.num_points

        # 应用当前配置
        config.show_center = _show_center
        config.num_points = _num_points

        fig = concentric_circles_geometric(
            center=(0, 0),
            n=F,
            q=np.sqrt(A),
            radius=R,
            direction=direction,
            color=config.center_color,
            width=_width,
            opacity=_opacity,
            name="Center Wave",
        )

        wave_points = _calculate_wave_points(P, theta)
        for point in wave_points:
            sub_fig = concentric_circles_geometric(
                center=point,
                n=F,
                q=np.sqrt(A),
                radius=R,
                direction=direction,
                color=color or config.default_color,
                width=_width,
                opacity=_opacity,
                name="Wave",
            )
            fig.add_traces(sub_fig.data)

        # 恢复原始配置
        config.show_center = original_show_center
        config.num_points = original_num_points

        fig.update_layout(**config.layout)
        return fig

    except Exception as e:
        raise WaveError(f"Error drawing geometric wave: {str(e)}")


# 为了保持向后兼容性，提供原有函数名的别名
wave_circle_ari_o = lambda A, F, P, color, theta=0, R=1: wave_circle_arithmetic(
    A, F, P, color, theta, R, direction="out"
)
wave_circle_ari_i = lambda A, F, P, color, theta=0, R=1: wave_circle_arithmetic(
    A, F, P, color, theta, R, direction="in"
)
wave_circle_ari = lambda A, F, P, color, theta=0, R=1: wave_circle_arithmetic(
    A, F, P, color, theta, R, direction="both"
)
wave_circle_pro_o = lambda A, F, P, color, theta=0, R=1: wave_circle_geometric(
    A, F, P, color, theta, R, direction="out"
)
wave_circle_pro_i = lambda A, F, P, color, theta=0, R=1: wave_circle_geometric(
    A, F, P, color, theta, R, direction="in"
)
wave_circle_pro = lambda A, F, P, color, theta=0, R=1: wave_circle_geometric(
    A, F, P, color, theta, R, direction="both"
)


# 导出主要的函数和类
__all__ = [
    "WaveConfig",
    "WaveError",
    "config",
    "wave_circle_arithmetic",
    "wave_circle_geometric",
    "wave_circle_ari_o",
    "wave_circle_ari_i",
    "wave_circle_ari",
    "wave_circle_pro_o",
    "wave_circle_pro_i",
    "wave_circle_pro",
]
