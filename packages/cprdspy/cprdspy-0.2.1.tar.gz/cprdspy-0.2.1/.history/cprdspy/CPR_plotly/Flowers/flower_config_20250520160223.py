import numpy as np
import plotly.graph_objects as go
from functools import lru_cache
from typing import Tuple, List, Optional, Union, Dict, Any
import os
import sys

# 添加 cprdspy 文件夹到 sys.path
sys.path.append("./flower_config")

# 导入arc_config中的主题和配置
from arc_config import (
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
        self.num_points = 1000  # 采样点数
        self.default_color = "#FF69B4"  # 默认粉色
        self.line_width = 2
        self.opacity = 1.0
        self.show_hover = True
        self.animation_duration = 1500  # 动画持续时间（毫秒）
        self.animation_easing = "cubic-in-out"  # 动画缓动函数
        self.show_center = True  # 是否显示花朵中心点
        self.center_marker_size = 8  # 中心点大小
        self.center_marker_color = "#FFD700"  # 中心点颜色（金色）
        self.show_petals_count = True  # 是否显示花瓣数量标签
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


@lru_cache(maxsize=128, typed=True)
def _calculate_flower_points(
    n: int, d: int, a: float = 1.0, theta_max: float = 2 * np.pi, num_points: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """计算花朵点坐标（带缓存）"""
    if n <= 0 or d <= 0:
        raise FlowerError("Parameters n and d must be positive")
    if num_points < 2:
        raise FlowerError("Number of points must be at least 2")

    theta = np.linspace(0, theta_max, num_points)
    k = n / d
    r = a * np.cos(k * theta)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y


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
) -> go.Scatter:
    """创建花朵的跟踪对象"""
    trace = go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(color=color, width=width, dash=dash),
        opacity=opacity,
        hoverinfo="x+y" if show_hover else "none",
        hoverlabel=dict(bgcolor="white", font=dict(color="black")),
        name=name or "Flower",
    )

    if animate:
        trace.update(
            mode="lines+markers",
            marker=dict(size=5, symbol="circle", color=color),
        )

    return trace


def add_center_point(
    fig: go.Figure, size: int = 8, color: Optional[str] = None
) -> None:
    """添加花朵中心点"""
    if color is None:
        color = config.center_marker_color

    fig.add_trace(
        go.Scatter(
            x=[0],
            y=[0],
            mode="markers",
            marker=dict(
                size=size,
                color=color,
                symbol="circle",
                line=dict(color="white", width=1),
            ),
            name="Center",
            hoverinfo="name",
        )
    )


def add_petals_count_annotation(fig: go.Figure, n: int, d: int) -> None:
    """添加花瓣数量标注"""
    gcd = np.gcd(n, d)
    petals_count = n // gcd if d % 2 == 0 else n

    fig.add_annotation(
        x=0.95,
        y=0.95,
        xref="paper",
        yref="paper",
        text=f"花瓣数: {petals_count}",
        showarrow=False,
        font=dict(size=14, color=config.get_theme()["font"]["color"]),
        bgcolor=config.get_theme()["bgcolor"],
        bordercolor=config.get_theme()["linecolor"],
        borderwidth=1,
        borderpad=4,
        opacity=0.8,
    )


def flower_by_petal(
    n: int,
    d: int,
    a: float = 1.0,
    theta_max: float = 2 * np.pi,
    color: Optional[str] = None,
    width: float = 2,
    dash: Optional[str] = None,
    opacity: float = 1.0,
    title: Optional[str] = None,
    animate: bool = False,
    show_center: Optional[bool] = None,
    show_petals_count: Optional[bool] = None,
) -> Optional[go.Figure]:
    """绘制玫瑰线花朵

    参数:
        n: 分子参数，控制花瓣数量
        d: 分母参数，控制花瓣形状
        a: 振幅参数，控制花朵大小
        theta_max: 最大角度，默认为2π（完整花朵）
        color: 花朵颜色
        width: 线宽
        dash: 线型（实线、虚线等）
        opacity: 透明度
        title: 图表标题
        animate: 是否启用动画
        show_center: 是否显示中心点
        show_petals_count: 是否显示花瓣数量

    返回:
        plotly图表对象
    """
    try:
        if color is None:
            color = config.get_color_from_theme()

        if show_center is None:
            show_center = config.show_center

        if show_petals_count is None:
            show_petals_count = config.show_petals_count

        x, y = _calculate_flower_points(n, d, a, theta_max, config.num_points)

        fig = go.Figure()

        # 添加花朵轮廓
        trace = create_flower_trace(
            x,
            y,
            color,
            width,
            dash,
            opacity,
            f"花朵 n={n}, d={d}",
            config.show_hover,
            animate,
        )
        fig.add_trace(trace)

        # 添加中心点
        if show_center:
            add_center_point(fig, config.center_marker_size, config.center_marker_color)

        # 添加花瓣数量标注
        if show_petals_count:
            add_petals_count_annotation(fig, n, d)

        # 添加动画
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

        # 更新布局
        layout_updates = config.layout.copy()
        if title:
            layout_updates["title"] = title

        fig.update_layout(**layout_updates)
        fig.update_xaxes(range=[-1.5, 1.5])
        fig.update_yaxes(range=[-1.5, 1.5])

        return fig

    except Exception as e:
        print(f"Error drawing flower: {str(e)}")
        return None


def flower_multi(
    flowers_params: List[Dict[str, Any]],
    title: Optional[str] = None,
    show_center: bool = True,
) -> Optional[go.Figure]:
    """绘制多个花朵在同一图表上

    参数:
        flowers_params: 花朵参数列表，每个元素是一个字典，包含flower_by_petal的参数
        title: 图表标题
        show_center: 是否显示中心点

    返回:
        plotly图表对象
    """
    try:
        fig = go.Figure()

        for i, params in enumerate(flowers_params):
            n = params.get("n", 3)
            d = params.get("d", 1)
            a = params.get("a", 1.0)
            theta_max = params.get("theta_max", 2 * np.pi)
            color = params.get("color", config.get_color_from_theme(i))
            width = params.get("width", config.line_width)
            dash = params.get("dash", None)
            opacity = params.get("opacity", config.opacity)
            name = params.get("name", f"花朵 {i+1}")

            x, y = _calculate_flower_points(n, d, a, theta_max, config.num_points)

            trace = create_flower_trace(
                x,
                y,
                color,
                width,
                dash,
                opacity,
                name,
                config.show_hover,
                False,  # 多花朵模式下不使用动画
            )
            fig.add_trace(trace)

        # 添加中心点
        if show_center:
            add_center_point(fig, config.center_marker_size, config.center_marker_color)

        # 更新布局
        layout_updates = config.layout.copy()
        if title:
            layout_updates["title"] = title

        fig.update_layout(**layout_updates)
        fig.update_xaxes(range=[-1.5, 1.5])
        fig.update_yaxes(range=[-1.5, 1.5])

        return fig

    except Exception as e:
        print(f"Error drawing multiple flowers: {str(e)}")
        return None


# 测试代码
if __name__ == "__main__":
    # 测试主题切换
    for theme_name in config.themes.keys():
        print(f"Testing theme: {theme_name}")
        config.set_theme(theme_name)

        # 测试基本花朵
        fig = flower_by_petal(
            n=5,
            d=2,
            a=1.0,
            color=None,  # 使用主题颜色
            width=3,
            title=f"玫瑰线花朵 (n=5, d=2) - {theme_name}主题",
            animate=True,
        )
        if fig:
            fig.show()

        # 测试多花朵
        fig = flower_multi(
            [
                {"n": 3, "d": 1, "a": 1.0},
                {"n": 5, "d": 2, "a": 0.8, "opacity": 0.7},
                {"n": 7, "d": 3, "a": 0.6, "opacity": 0.5},
            ],
            title=f"多层花朵 - {theme_name}主题",
        )
        if fig:
            fig.show()
