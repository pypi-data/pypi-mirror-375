import numpy as np
import plotly.graph_objects as go
from functools import lru_cache
from typing import Tuple, List, Optional, Union, Dict, Any
import os
import sys

# 导入arc_config中的函数和配置
from cprdspy.CPR_plotly.Arcs.arc_config import (
    PLOTLY_DARK,
    DEEP_SEA,
    CYBERPUNK,
    AURORA,
    SUNSET,
    FOREST,
    ArcConfig,
    config as arc_config,
    arc,  # 导入arc函数
    arc_inverse,  # 导入arc_inverse函数
)


class FlowerError(Exception):
    """自定义花朵绘制错误类"""

    pass


class FlowerConfig:
    """统一管理花朵绘图配置"""

    def __init__(self):
        self.num_points = 200  # 减少采样点数以提高性能
        self.default_color = "#FF69B4"  # 默认粉色
        self.line_width = 2
        self.opacity = 1.0
        self.show_hover = True
        self.animation_duration = 1000  # 动画持续时间（毫秒）
        self.animation_easing = "cubic-in-out"  # 动画缓动函数
        self.animation_frame_gap = 5  # 动画帧间隔（采样点数）
        self.show_markers = False  # 默认不显示标记点
        self.show_markers_in_animation = False  # 动画中也不显示标记点
        self.marker_size = 4  # 默认标记点大小
        self.marker_color = None  # 默认使用线条颜色
        self.themes = arc_config.themes  # 使用arc_config中的主题
        self.theme = arc_config.theme  # 默认使用arc_config的主题

    def set_theme(self, theme_name: str) -> None:
        """设置主题，同时更新arc_config的主题"""
        if theme_name not in self.themes:
            raise ValueError(
                f"Unknown theme: {theme_name}. Available themes: {list(self.themes.keys())}"
            )
        self.theme = theme_name
        arc_config.set_theme(theme_name)  # 同步更新arc_config的主题

    @property
    def layout(self) -> Dict:
        """获取布局配置"""
        theme = self.get_theme()
        return {
            "template": "plotly_dark",
            "showlegend": True,
            "margin": dict(l=20, r=20, t=30, b=20),
            "plot_bgcolor": theme["bgcolor"],
            "paper_bgcolor": theme["paper_bgcolor"],
            "font": theme["font"],
            "title": {
                "font": {"size": 24, "color": theme["font"]["color"]},
                "x": 0.5,
                "xanchor": "center",
            },
            "xaxis": {
                "gridcolor": theme["gridcolor"],
                "linecolor": theme["linecolor"],
                "showline": True,
                "mirror": True,
                "zeroline": True,
                "zerolinecolor": theme["linecolor"],
                "zerolinewidth": 1.5,
            },
            "yaxis": {
                "gridcolor": theme["gridcolor"],
                "linecolor": theme["linecolor"],
                "showline": True,
                "mirror": True,
                "scaleanchor": "x",
                "scaleratio": 1,
                "zeroline": True,
                "zerolinecolor": theme["linecolor"],
                "zerolinewidth": 1.5,
            },
            "updatemenus": [
                {
                    "type": "buttons",
                    "showactive": False,
                    "y": 0,
                    "x": 1.05,
                    "xanchor": "left",
                    "yanchor": "bottom",
                    "buttons": [
                        {
                            "label": "重置视图",
                            "method": "relayout",
                            "args": ["xaxis.range", [-1.5, 1.5]],
                        },
                        {
                            "label": "重置视图",
                            "method": "relayout",
                            "args": ["yaxis.range", [-1.5, 1.5]],
                        },
                    ],
                }
            ],
        }

    def get_theme(self) -> Dict:
        """获取主题配置"""
        return self.themes.get(self.theme, self.themes["plotly_dark"])

    def get_color_from_theme(self, index: int = 0) -> str:
        """从当前主题的配色方案中获取颜色"""
        theme = self.get_theme()
        colorway = theme.get("colorway", [self.default_color])
        return colorway[index % len(colorway)]


# 创建全局配置实例
config = FlowerConfig()


def create_petal_points(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    n: int,
    theta: float = 0,
) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
    """计算花瓣的起点和终点坐标"""
    if R <= 0 or r <= 0:
        raise FlowerError("Radius must be positive")
    if n <= 0:
        raise FlowerError("n must be positive")

    alpha = 2 * np.pi / n
    a = R * np.sin(np.pi / n)

    if r < a:
        raise FlowerError(f"r ({r}) must be greater than or equal to a ({a})")

    # 计算花瓣的起点和终点
    points = []
    for i in range(n):
        current_theta = theta + i * alpha
        # 花瓣的起点（在大圆上）
        start_point = (
            center[0] + R * np.cos(current_theta),
            center[1] + R * np.sin(current_theta),
        )
        # 花瓣的终点（在大圆上）
        end_point = (
            center[0] + R * np.cos(current_theta + alpha),
            center[1] + R * np.sin(current_theta + alpha),
        )
        points.append((start_point, end_point))

    return points


def n_flower_petal(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    n: int,
    theta: float = 0,
    color: str = "blue",
    width: float = 2,
    dash: Optional[str] = None,
    opacity: float = 1.0,
    animate: bool = False,
    show_markers: Optional[bool] = None,
) -> Optional[go.Figure]:
    """使用arc函数画花瓣"""
    try:
        if color is None:
            color = config.get_color_from_theme()

        # 创建图表
        fig = go.Figure()

        # 获取花瓣的起点和终点
        petal_points = create_petal_points(center, R, r, n, theta)

        # 为每个花瓣创建两个弧线
        for i, (start, end) in enumerate(petal_points):
            # 创建第一个弧（顺时针）
            arc_fig = arc(
                center=start,
                point1=center,
                point2=end,
                color=color,
                width=width,
                dash=dash,
                opacity=opacity,
                animate=animate,
                label=f"Petal {i+1}" if i == 0 else None,
            )
            if arc_fig and arc_fig.data:
                for trace in arc_fig.data:
                    fig.add_trace(trace)

            # 创建第二个弧（逆时针）
            arc_inv_fig = arc_inverse(
                center=end,
                point1=center,
                point2=start,
                color=color,
                width=width,
                dash=dash,
                opacity=opacity,
                animate=animate,
            )
            if arc_inv_fig and arc_inv_fig.data:
                for trace in arc_inv_fig.data:
                    fig.add_trace(trace)

        # 更新布局
        fig.update_layout(**config.layout)
        fig.update_xaxes(range=[-1.5 * R, 1.5 * R])
        fig.update_yaxes(range=[-1.5 * R, 1.5 * R])

        return fig

    except Exception as e:
        print(f"Error drawing flower petal: {str(e)}")
        return None


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
    width: float = 2,
    dash: Optional[str] = None,
    opacity: float = 1.0,
    animate: bool = False,
    show_markers: Optional[bool] = None,
) -> Optional[go.Figure]:
    """画多层花"""
    try:
        if color is None:
            color = config.get_color_from_theme()

        fig = go.Figure()

        for j in range(1, M + 1):
            current_R = R * (ratio ** (j - 1))
            current_r = r * (ratio ** (j - 1))
            current_opacity = opacity * (1 - 0.2 * (j - 1) / M)  # 渐变透明度

            # 获取当前层的花瓣点
            for i in range(N):
                current_theta = theta + 2 * i * np.pi / N + (j - 1) * np.pi / N

                # 创建单个花瓣
                petal_fig = n_flower_petal(
                    center=center,
                    R=current_R,
                    r=current_r,
                    n=n,
                    theta=current_theta,
                    color=color,
                    width=width,
                    dash=dash,
                    opacity=current_opacity,
                    animate=animate,
                    show_markers=show_markers,
                )

                if petal_fig and petal_fig.data:
                    for trace in petal_fig.data:
                        trace.name = f"Layer {j}, Petal {i+1}"
                        fig.add_trace(trace)

        # 更新布局
        fig.update_layout(**config.layout)
        max_R = R * (ratio ** (M - 1))
        fig.update_xaxes(range=[-1.5 * max_R, 1.5 * max_R])
        fig.update_yaxes(range=[-1.5 * max_R, 1.5 * max_R])

        return fig

    except Exception as e:
        print(f"Error drawing multi-layer flower: {str(e)}")
        return None


# 测试代码
if __name__ == "__main__":
    # 测试主题切换
    for theme_name in config.themes.keys():
        print(f"Testing theme: {theme_name}")
        config.set_theme(theme_name)

        # 测试基本花瓣
        fig = n_flower_petal(
            [0, 0], 1.0, 1.2, 6, theta=0, color=None, width=2, animate=True
        )
        if fig:
            fig.show()

        # 测试多层花
        fig = flowers_flower_by_petal_multi(
            [0, 0], 1.0, 1.2, 6, np.sqrt(2), 3, 12, theta=0, color=None, animate=True
        )
        if fig:
            fig.show()
