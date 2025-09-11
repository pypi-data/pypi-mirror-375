from typing import Tuple, List, Optional, Union, Dict, Any
import numpy as np
import plotly.graph_objects as go
from functools import lru_cache
from cprdspy.CPR_plotly.Arcs.arc_config import *


class FlowerError(Exception):
    """花朵绘制相关的自定义异常"""

    pass


class FlowerConfig:
    """花朵绘制的配置管理类"""

    def __init__(self):
        self.num_points = 10000  # 默认采样点数
        self.default_color = "#1f77b4"  # 默认蓝色
        self.default_fill_color = "#ff7f0e"  # 默认填充色（橙色）
        self.line_width = 2  # 默认线宽
        self.opacity = 1.0  # 默认透明度
        self.fill_opacity = 0.3  # 默认填充透明度

    @property
    def layout(self) -> Dict[str, Any]:
        """获取默认布局配置"""
        return {
            "showlegend": True,
            "margin": dict(l=20, r=20, t=20, b=20),
            "yaxis": {"scaleanchor": "x", "scaleratio": 1},
        }


# 创建全局配置实例
config = FlowerConfig()


@lru_cache(maxsize=128)
def _calculate_flower_centers(
    center: Tuple[float, float], R: float, n: int, theta: float = 0
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """计算花瓣的两个圆心坐标（带缓存）"""
    alpha = 2 * np.pi / n
    center1 = (
        np.cos(theta + alpha / 2) * R + center[0],
        np.sin(theta + alpha / 2) * R + center[1],
    )
    center2 = (
        np.cos(theta + alpha / 2 - 2 * np.pi / n) * R + center[0],
        np.sin(theta + alpha / 2 - 2 * np.pi / n) * R + center[1],
    )
    return center1, center2


def n_flower_petal(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    n: int,
    theta: float = 0,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制花瓣

    Args:
        center: 中心点坐标
        R: 大圆半径
        r: 小圆半径
        n: 分割数
        theta: 旋转角度
        color: 线条颜色
        width: 线条宽度
        opacity: 透明度
    """
    try:
        alpha = 2 * np.pi / n
        a = R * np.sin(np.pi / n)

        if r < a:
            raise FlowerError(f"r ({r}) < a ({a}), cannot form petal")

        beta = np.arccos(a / r)
        theta_arc = np.pi / 2 - np.pi / n + beta
        center1, center2 = _calculate_flower_centers(tuple(center), R, n, theta)

        fig = go.Figure()

        if abs(r - a) < 1e-12:
            arc1 = arc_degree(
                center1,
                r,
                np.pi + alpha / 2 + theta,
                np.pi + alpha / 2 + theta + theta_arc,
                color=color or config.default_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
                num_points=config.num_points,
            )
            arc2 = arc_degree(
                center2,
                r,
                np.pi / 2 + theta,
                np.pi / 2 + theta + theta_arc,
                color=color or config.default_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
                num_points=config.num_points,
            )
        else:
            arc1 = arc_degree(
                center1,
                r,
                np.pi + alpha / 2 + theta,
                np.pi + alpha / 2 + theta + theta_arc,
                color=color or config.default_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )
            arc2 = arc_degree(
                center2,
                r,
                np.pi / 2 - beta + theta,
                np.pi / 2 - beta + theta + theta_arc,
                color=color or config.default_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )

        if arc1 and arc2:
            fig.add_traces(arc1.data)
            fig.add_traces(arc2.data)
            fig.update_layout(**config.layout)

        return fig
    except Exception as e:
        raise FlowerError(f"Error drawing flower petal: {str(e)}")


def n_flower_arc(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    n: int,
    theta: float = 0,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制花弧

    Args:
        center: 中心点坐标
        R: 大圆半径
        r: 小圆半径
        n: 分割数
        theta: 旋转角度
        color: 线条颜色
        width: 线条宽度
        opacity: 透明度
    """
    try:
        alpha = 2 * np.pi / n
        a = R * np.sin(np.pi / n)

        if r < a:
            raise FlowerError(f"r ({r}) < a ({a}), cannot form arc")

        beta = np.arccos(a / r)
        theta_arc = np.pi / 2 - np.pi / n + beta
        theta_petal = 2 * theta_arc
        center1, center2 = _calculate_flower_centers(tuple(center), R, n, theta)

        fig = go.Figure()

        if abs(r - a) < 1e-12:
            arc1 = arc_degree(
                center1,
                r,
                np.pi / 2 + alpha + theta,
                np.pi / 2 + alpha + theta + theta_petal,
                color=color or config.default_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )
            arc2 = arc_degree(
                center2,
                r,
                np.pi / 2 + theta,
                np.pi / 2 + theta + theta_petal,
                color=color or config.default_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )
        else:
            arc1 = arc_degree(
                center1,
                r,
                np.pi / 2 + alpha - beta + theta,
                np.pi / 2 + alpha - beta + theta + theta_petal,
                color=color or config.default_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )
            arc2 = arc_degree(
                center2,
                r,
                np.pi / 2 - beta + theta,
                np.pi / 2 - beta + theta + theta_petal,
                color=color or config.default_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )

        if arc1 and arc2:
            fig.add_traces(arc1.data)
            fig.add_traces(arc2.data)
            fig.update_layout(**config.layout)

        return fig
    except Exception as e:
        raise FlowerError(f"Error drawing flower arc: {str(e)}")


def n_flowers_flower_arc_with_field(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    n: int,
    theta: float = 0,
    color: Optional[str] = None,
    field_color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制带场的花弧

    Args:
        center: 中心点坐标
        R: 大圆半径
        r: 小圆半径
        n: 分割数
        theta: 旋转角度
        color: 线条颜色
        field_color: 场的颜色
        width: 线条宽度
        opacity: 透明度
    """
    try:
        alpha = 2 * np.pi / n
        a = R * np.sin(np.pi / n)

        if r < a:
            raise FlowerError(f"r ({r}) < a ({a}), cannot form arc")

        beta = np.arccos(a / r)
        theta_arc = np.pi / 2 - np.pi / n + beta
        theta_petal = 2 * theta_arc
        center1, center2 = _calculate_flower_centers(tuple(center), R, n, theta)

        fig = go.Figure()

        if abs(r - a) < 1e-12:
            arc1 = arc_degree(
                center1,
                r,
                np.pi / 2 + alpha + theta,
                np.pi / 2 + alpha + theta + theta_petal,
                color=color or config.default_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )
            arc2 = arc_degree(
                center2,
                r,
                np.pi / 2 + theta,
                np.pi / 2 + theta + theta_petal,
                color=color or config.default_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )
            arc1_inv = arc_degree_inverse(
                center1,
                r,
                np.pi / 2 + alpha + theta,
                np.pi / 2 + alpha + theta + theta_petal,
                color=field_color or config.default_fill_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )
            arc2_inv = arc_degree_inverse(
                center2,
                r,
                np.pi / 2 + theta,
                np.pi / 2 + theta + theta_petal,
                color=field_color or config.default_fill_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )
        else:
            arc1 = arc_degree(
                center1,
                r,
                np.pi / 2 + alpha - beta + theta,
                np.pi / 2 + alpha - beta + theta + theta_petal,
                color=color or config.default_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )
            arc2 = arc_degree(
                center2,
                r,
                np.pi / 2 - beta + theta,
                np.pi / 2 - beta + theta + theta_petal,
                color=color or config.default_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )
            arc1_inv = arc_degree_inverse(
                center1,
                r,
                np.pi / 2 + alpha - beta + theta,
                np.pi / 2 + alpha - beta + theta + theta_petal,
                color=field_color or config.default_fill_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )
            arc2_inv = arc_degree_inverse(
                center2,
                r,
                np.pi / 2 - beta + theta,
                np.pi / 2 - beta + theta + theta_petal,
                color=field_color or config.default_fill_color,
                width=width or config.line_width,
                opacity=opacity or config.opacity,
            )

        if all([arc1, arc2, arc1_inv, arc2_inv]):
            fig.add_traces(arc1.data)
            fig.add_traces(arc2.data)
            fig.add_traces(arc1_inv.data)
            fig.add_traces(arc2_inv.data)
            fig.update_layout(**config.layout)

        return fig
    except Exception as e:
        raise FlowerError(f"Error drawing flower arc with field: {str(e)}")


def one_flower_petal(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    n: int,
    theta: float = 0,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制一朵向上的花瓣"""
    return n_flower_petal(center, R, r, n, theta + np.pi / 2, color, width, opacity)


def one_flower_arc(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    n: int,
    theta: float = 0,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制一朵向上的花弧"""
    return n_flower_arc(center, R, r, n, theta + np.pi / 2, color, width, opacity)


def one_flower_flower_arc_with_field(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    n: int,
    theta: float = 0,
    color: Optional[str] = None,
    field_color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制一朵向上的带场花弧"""
    return n_flowers_flower_arc_with_field(
        center, R, r, n, theta + np.pi / 2, color, field_color, width, opacity
    )


def flowers_flower_by_petal(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    N: int,
    n: int,
    theta: float = 0,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制花瓣形成的单层花"""
    try:
        fig = go.Figure()
        for i in range(N):
            sub_fig = one_flower_petal(
                center, R, r, n, 2 * i * np.pi / N + theta, color, width, opacity
            )
            fig.add_traces(sub_fig.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise FlowerError(f"Error drawing flower by petal: {str(e)}")


def flowers_flower_by_arc(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    N: int,
    n: int,
    theta: float = 0,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制花弧形成的单层花"""
    try:
        fig = go.Figure()
        for i in range(N):
            sub_fig = one_flower_arc(
                center, R, r, n, 2 * i * np.pi / N + theta, color, width, opacity
            )
            fig.add_traces(sub_fig.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise FlowerError(f"Error drawing flower by arc: {str(e)}")


def flowers_flower_by_flower_arc_with_field(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    N: int,
    n: int,
    theta: float = 0,
    color: Optional[str] = None,
    field_color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制带场花弧形成的单层花"""
    try:
        fig = go.Figure()
        for i in range(N):
            sub_fig = one_flower_flower_arc_with_field(
                center,
                R,
                r,
                n,
                2 * i * np.pi / N + theta,
                color,
                field_color,
                width,
                opacity,
            )
            fig.add_traces(sub_fig.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise FlowerError(f"Error drawing flower by arc with field: {str(e)}")


def flowers_flower_by_petal_multi(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    n: int,
    ratio: float,
    M: int,
    N: int,
    theta: float = 0,
    color: Optional[str] = None,
    width: Optional[float] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制花瓣形成的多层花"""
    try:
        fig = go.Figure()
        for j in range(M):
            scale = ratio**j
            for i in range(N):
                sub_fig = one_flower_petal(
                    center,
                    R * scale,
                    r * scale,
                    n,
                    2 * i * np.pi / N + j * np.pi / N + theta,
                    color,
                    width,
                    opacity,
                )
                fig.add_traces(sub_fig.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise FlowerError(f"Error drawing multi-layer flower: {str(e)}")


def flower_by_petal_fill(
    center: Union[List[float], Tuple[float, float]],
    r: float,
    M: int,
    N: int,
    n: int,
    theta: float = 0,
    fill_color: Optional[str] = None,
    color: Optional[str] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制带填充的花瓣形成的花"""
    try:
        fig = go.Figure()
        for j in range(M, 0, -1):
            scale = (np.sqrt(2 * np.cos(np.pi / n))) ** (2 * j + 1)
            for i in range(N):
                sub_fig = n_lily_petal_fill(
                    center,
                    r * scale,
                    n,
                    2 * i * np.pi / N + j * np.pi / N + theta,
                    fill_color or config.default_fill_color,
                    color or config.default_color,
                    opacity or config.fill_opacity,
                )
                fig.add_traces(sub_fig.data)
        fig.update_layout(**config.layout)
        return fig
    except Exception as e:
        raise FlowerError(f"Error drawing flower with filled petals: {str(e)}")


def n_lily_petal_fill(
    center: Union[List[float], Tuple[float, float]],
    r: float,
    n: int,
    theta: float = 0,
    fill_color: Optional[str] = None,
    color: Optional[str] = None,
    opacity: Optional[float] = None,
) -> go.Figure:
    """绘制带填充的百合花瓣"""
    try:
        alpha = np.pi / n
        beta = np.pi - alpha
        center1, center2 = _calculate_flower_centers(tuple(center), r, n, theta)

        arc = arc_degree(
            center1,
            r,
            alpha + np.pi + theta,
            alpha + np.pi + theta + np.pi * (n - 2) / n,
            color=color or config.default_color,
            width=config.line_width,
            opacity=opacity or config.opacity,
        )

        arc_inv = arc_degree_inverse(
            center2,
            r,
            beta + theta,
            beta + theta + np.pi * (n + 2) / n,
            color=color or config.default_color,
            width=config.line_width,
            opacity=opacity or config.opacity,
        )

        if arc and arc_inv:
            fig = go.Figure()

            # 添加填充区域
            x1 = arc.data[0].x
            y1 = arc.data[0].y
            x2 = arc_inv.data[0].x
            y2 = arc_inv.data[0].y

            fig.add_trace(
                go.Scatter(
                    x=x1,
                    y=y1,
                    fill="toself",
                    fillcolor=fill_color or config.default_fill_color,
                    line=dict(color=color or config.default_color),
                    opacity=opacity or config.fill_opacity,
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=x2,
                    y=y2,
                    fill="toself",
                    fillcolor=fill_color or config.default_fill_color,
                    line=dict(color=color or config.default_color),
                    opacity=opacity or config.fill_opacity,
                )
            )

            fig.update_layout(**config.layout)
            return fig

    except Exception as e:
        raise FlowerError(f"Error drawing lily petal with fill: {str(e)}")


# 导出主要的函数和类
__all__ = [
    "FlowerConfig",
    "FlowerError",
    "config",
    "n_flower_petal",
    "n_flower_arc",
    "n_flowers_flower_arc_with_field",
    "one_flower_petal",
    "one_flower_arc",
    "one_flower_flower_arc_with_field",
    "flowers_flower_by_petal",
    "flowers_flower_by_arc",
    "flowers_flower_by_flower_arc_with_field",
    "flowers_flower_by_petal_multi",
    "flower_by_petal_fill",
    "n_lily_petal_fill",
]
