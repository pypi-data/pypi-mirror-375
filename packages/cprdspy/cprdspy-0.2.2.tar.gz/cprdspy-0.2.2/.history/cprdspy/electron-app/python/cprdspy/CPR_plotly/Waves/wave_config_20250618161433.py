from typing import Tuple, List, Optional, Union, Dict, Any
import numpy as np
import plotly.graph_objects as go
from cprdspy.CPR_plotly.Circles.circle_config import (
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
        self.center_color = "#0f0"  # 中心点默认颜色
        self.num_points = circle_config.num_points
        self.line_width = circle_config.line_width
        self.opacity = circle_config.opacity
        self.show_center = circle_config.show_center
        self.theme = "classic"  # 默认主题

    @property
    def layout(self) -> Dict[str, Any]:
        """获取默认布局配置"""
        return {
            "showlegend": False,
            "margin": dict(l=20, r=20, t=20, b=20),
            "yaxis": {"scaleanchor": "x", "scaleratio": 1},
        }

    def apply_to_figure(self, fig):
        """应用主题配置到图形"""
        fig.update_layout(**self.layout)
        return fig


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
        # 创建基础图形
        fig = go.Figure()

        # 计算波形上的点的位置
        wave_points = _calculate_wave_points(P, theta)

        # 为每个点创建同心圆
        for point in wave_points:
            # 计算圆的半径
            radii = [R + i * A for i in range(F)]

            # 创建圆形轨迹
            for r in radii:
                t = np.linspace(0, 2 * np.pi, 100)
                x = point[0] + r * np.cos(t)
                y = point[1] + r * np.sin(t)

                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        mode="lines",
                        line=dict(
                            color=color or config.default_color,
                            width=width or config.line_width,
                        ),
                        opacity=opacity or config.opacity,
                        showlegend=False,
                    )
                )

        # 更新布局
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
        # 创建基础图形
        fig = go.Figure()

        # 计算波形上的点的位置
        wave_points = _calculate_wave_points(P, theta)

        # 为每个点创建同心圆
        for point in wave_points:
            # 计算圆的半径（等比数列）
            radii = [R * (A ** (i / 2)) for i in range(F)]

            # 创建圆形轨迹
            for r in radii:
                t = np.linspace(0, 2 * np.pi, 100)
                x = point[0] + r * np.cos(t)
                y = point[1] + r * np.sin(t)

                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        mode="lines",
                        line=dict(
                            color=color or config.default_color,
                            width=width or config.line_width,
                        ),
                        opacity=opacity or config.opacity,
                        showlegend=False,
                    )
                )

        # 更新布局
        fig.update_layout(**config.layout)
        return fig

    except Exception as e:
        raise WaveError(f"Error drawing geometric wave: {str(e)}")


# 为了保持向后兼容性，提供原有函数名的别名
def wave_circle_ari_o(A, F, P, color, theta=0, R=1, **kwargs):
    return wave_circle_arithmetic(A, F, P, color, theta, R, direction="out", **kwargs)


def wave_circle_ari_i(A, F, P, color, theta=0, R=1, **kwargs):
    return wave_circle_arithmetic(A, F, P, color, theta, R, direction="in", **kwargs)


def wave_circle_ari(A, F, P, color, theta=0, R=1, **kwargs):
    return wave_circle_arithmetic(A, F, P, color, theta, R, direction="both", **kwargs)


def wave_circle_pro_o(A, F, P, color, theta=0, R=1, **kwargs):
    return wave_circle_geometric(A, F, P, color, theta, R, direction="out", **kwargs)


def wave_circle_pro_i(A, F, P, color, theta=0, R=1, **kwargs):
    return wave_circle_geometric(A, F, P, color, theta, R, direction="in", **kwargs)


def wave_circle_pro(A, F, P, color, theta=0, R=1, **kwargs):
    return wave_circle_geometric(A, F, P, color, theta, R, direction="both", **kwargs)


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
