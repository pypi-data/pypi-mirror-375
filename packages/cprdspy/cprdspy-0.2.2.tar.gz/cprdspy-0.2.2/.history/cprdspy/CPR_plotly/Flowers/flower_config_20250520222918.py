           import numpy as np
import plotly.graph_objects as go
from functools import lru_cache
from typing import Tuple, List, Optional, Union, Dict, Any
import os
import sys

# 导入arc_config中的主题和配置
from cprdspy.CPR_plotly.Arcs.arc_config import (
    PLOTLY_DARK,
    DEEP_SEA,
    CYBERPUNK,
    AURORA,
    SUNSET,
    FOREST,
    ArcConfig,
    config as arc_config,
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


@lru_cache(maxsize=128, typed=True)
def _calculate_flower_points(
    center: Tuple[float, float],
    R: float,
    r: float,
    n: int,
    theta: float = 0,
    num_points: int = 1000,
) -> Tuple[np.ndarray, np.ndarray]:
    """计算花朵点坐标（带缓存）"""
    if R <= 0 or r <= 0:
        raise FlowerError("Radius must be positive")
    if n <= 0:
        raise FlowerError("n must be positive")
    if num_points < 2:
        raise FlowerError("Number of points must be at least 2")

    alpha = 2 * np.pi / n
    a = R * np.sin(np.pi / n)

    if r < a:
        raise FlowerError(f"r ({r}) must be greater than or equal to a ({a})")

    beta = np.arccos(a / r)
    theta_arc = np.pi / 2 - np.pi / n + beta

    t = np.linspace(0, theta_arc, num_points)

    center1 = (
        np.cos(theta + alpha / 2) * R + center[0],
        np.sin(theta + alpha / 2) * R + center[1],
    )
    center2 = (
        np.cos(theta + alpha / 2 - 2 * np.pi / n) * R + center[0],
        np.sin(theta + alpha / 2 - 2 * np.pi / n) * R + center[1],
    )

    x1 = center1[0] + r * np.cos(t + np.pi + alpha / 2 + theta)
    y1 = center1[1] + r * np.sin(t + np.pi + alpha / 2 + theta)

    x2 = center2[0] + r * np.cos(t + np.pi / 2 - beta + theta)
    y2 = center2[1] + r * np.sin(t + np.pi / 2 - beta + theta)

    return np.concatenate([x1, x2]), np.concatenate([y1, y2])


def create_flower_trace(
    x: np.ndarray,
    y: np.ndarray,
    color: str,
    width: float = 2,
    dash: Optional[str] = None,
    opacity: float = 1.0,
    name: Optional[str] = None,
    show_hover: bool = True,
    animate: bool = False,
    show_markers: Optional[bool] = None,
    marker_size: Optional[int] = None,
    marker_color: Optional[str] = None,
) -> go.Scatter:
    """创建花朵的跟踪对象"""
    # 使用配置默认值
    if show_markers is None:
        show_markers = config.show_markers
    if marker_size is None:
        marker_size = config.marker_size
    if marker_color is None:
        marker_color = config.marker_color or color

    # 设置模式
    mode = "lines"
    if show_markers or animate:
        mode += "+markers"

    # 创建基本轨迹
    trace = go.Scatter(
        x=x,
        y=y,
        mode=mode,
        line=dict(color=color, width=width, dash=dash),
        opacity=opacity,
        hoverinfo="x+y" if show_hover else "none",
        hoverlabel=dict(bgcolor="white", font=dict(color="black")),
        name=name or "Flower",
    )

    # 如果需要显示标记点，添加标记配置
    if show_markers or animate:
        trace.update(
            marker=dict(
                size=marker_size,
                symbol="circle",
                color=marker_color,
            )
        )

    return trace


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
) -> Optional[go.Figure]:
    """画花瓣"""
    try:
        x, y = _calculate_flower_points(
            tuple(center), R, r, n, theta, config.num_points
        )

        fig = go.Figure()
        trace = create_flower_trace(
            x,
            y,
            color,
            width,
            dash,
            opacity,
            f"Flower Petal (R={R:.2f}, r={r:.2f})",
            config.show_hover,
            animate,
        )
        fig.add_trace(trace)

        if animate:
            frames = []
            for k in range(2, len(x), max(1, len(x) // 100)):
                frames.append(
                    go.Frame(
                        data=[
                            go.Scatter(
                                x=x[:k],
                                y=y[:k],
                                mode="lines+markers",
                                line=dict(color=color, width=width),
                                marker=dict(size=5, symbol="circle", color=color),
                            )
                        ]
                    )
                )

            fig.frames = frames

            fig.update_layout(
                updatemenus=[
                    {
                        "type": "buttons",
                        "showactive": False,
                        "buttons": [
                            {
                                "label": "播放",
                                "method": "animate",
                                "args": [
                                    None,
                                    {
                                        "frame": {
                                            "duration": config.animation_duration
                                            / len(frames)
                                        },
                                        "fromcurrent": True,
                                        "transition": {
                                            "duration": 0,
                                            "easing": config.animation_easing,
                                        },
                                    },
                                ],
                            }
                        ],
                    }
                ]
            )

        fig.update_layout(**config.layout)
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
    width: float = 1,
    dash: Optional[str] = None,
    opacity: float = 1.0,
    animate: bool = False,
) -> Optional[go.Figure]:
    """画多层花"""
    try:
        if color is None:
            color = config.get_color_from_theme()

        fig = go.Figure()

        for j in range(1, M + 1):
            current_R = R * (ratio ** (j - 1))
            current_r = r * (ratio ** (j - 1))

            for i in range(N):
                current_theta = 2 * i * np.pi / N + (j - 1) * np.pi / N + theta

                x, y = _calculate_flower_points(
                    tuple(center),
                    current_R,
                    current_r,
                    n,
                    current_theta + np.pi / 2,
                    config.num_points,
                )

                trace = create_flower_trace(
                    x,
                    y,
                    color,
                    width,
                    dash,
                    opacity * (1 - 0.2 * (j - 1) / M),  # 渐变透明度
                    f"Layer {j}, Petal {i+1}",
                    config.show_hover,
                    animate,
                )
                fig.add_trace(trace)

        if animate:
            # 为每一层创建动画帧
            all_traces = []
            for trace in fig.data:
                x = trace.x
                y = trace.y
                all_traces.append((x, y))

            frames = []
            max_points = max(len(x) for x, y in all_traces)

            for k in range(2, max_points, max(1, max_points // 100)):
                frame_data = []
                for x, y in all_traces:
                    current_k = min(k, len(x))
                    frame_data.append(
                        go.Scatter(
                            x=x[:current_k],
                            y=y[:current_k],
                            mode="lines+markers",
                            line=dict(color=color, width=width),
                            marker=dict(size=5, symbol="circle", color=color),
                        )
                    )
                frames.append(go.Frame(data=frame_data))

            fig.frames = frames

            fig.update_layout(
                updatemenus=[
                    {
                        "type": "buttons",
                        "showactive": False,
                        "buttons": [
                            {
                                "label": "播放",
                                "method": "animate",
                                "args": [
                                    None,
                                    {
                                        "frame": {
                                            "duration": config.animation_duration
                                            / len(frames)
                                        },
                                        "fromcurrent": True,
                                        "transition": {
                                            "duration": 0,
                                            "easing": config.animation_easing,
                                        },
                                    },
                                ],
                            }
                        ],
                    }
        if fig:
            )

        fig.update_layout(**config.layout)
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