import numpy as np
import plotly.graph_objects as go
from functools import lru_cache
from typing import Tuple, List, Optional, Union, Dict
import os
import sys

# 主题配置
PLOTLY_DARK = {
    "bgcolor": "#1f2630",  # 背景色
    "gridcolor": "#506784",  # 网格线颜色
    "linecolor": "#A2B1C6",  # 线条颜色
    "paper_bgcolor": "#1f2630",  # 画布背景色
    "plot_bgcolor": "#1f2630",  # 绘图区背景色
    "font": {"color": "#A2B1C6"},  # 字体颜色
    "colorway": [  # 主要配色方案
        "#00b4ff",  # 蓝色
        "#ff7c00",  # 橙色
        "#00ff7f",  # 绿色
        "#ff2b2b",  # 红色
        "#7520ff",  # 紫色
        "#ffff00",  # 黄色
    ],
}

DEEP_SEA = {
    "bgcolor": "#0A192F",  # 深蓝背景
    "gridcolor": "#172A45",
    "linecolor": "#8892B0",
    "paper_bgcolor": "#0A192F",
    "plot_bgcolor": "#0A192F",
    "font": {"color": "#8892B0"},
    "colorway": [
        "#64FFDA",  # 青绿
        "#48BEFF",  # 浅蓝
        "#7494EA",  # 淡紫
        "#E6855E",  # 珊瑚色
        "#FF6B6B",  # 粉红
        "#FFD93D",  # 金黄
    ],
}

CYBERPUNK = {
    "bgcolor": "#000000",  # 纯黑背景
    "gridcolor": "#1A1A1A",
    "linecolor": "#FF00FF",
    "paper_bgcolor": "#000000",
    "plot_bgcolor": "#000000",
    "font": {"color": "#00FF00"},
    "colorway": [
        "#00FF00",  # 霓虹绿
        "#FF00FF",  # 霓虹粉
        "#00FFFF",  # 霓虹蓝
        "#FFD700",  # 金色
        "#FF1493",  # 深粉色
        "#4169E1",  # 皇家蓝
    ],
}

AURORA = {
    "bgcolor": "#232D3F",  # 深灰蓝背景
    "gridcolor": "#384152",
    "linecolor": "#E5E9F0",
    "paper_bgcolor": "#232D3F",
    "plot_bgcolor": "#232D3F",
    "font": {"color": "#E5E9F0"},
    "colorway": [
        "#8FBCBB",  # 青绿
        "#88C0D0",  # 浅蓝
        "#81A1C1",  # 灰蓝
        "#5E81AC",  # 深蓝
        "#B48EAD",  # 紫色
        "#A3BE8C",  # 淡绿
    ],
}

SUNSET = {
    "bgcolor": "#2D142C",  # 深紫背景
    "gridcolor": "#510A32",
    "linecolor": "#EE4540",
    "paper_bgcolor": "#2D142C",
    "plot_bgcolor": "#2D142C",
    "font": {"color": "#EE4540"},
    "colorway": [
        "#EE4540",  # 红色
        "#C72C41",  # 深红
        "#801336",  # 酒红
        "#510A32",  # 紫红
        "#2D142C",  # 深紫
        "#FFA07A",  # 橙色
    ],
}

FOREST = {
    "bgcolor": "#2F4538",  # 深绿背景
    "gridcolor": "#4A6741",
    "linecolor": "#AAC0AA",
    "paper_bgcolor": "#2F4538",
    "plot_bgcolor": "#2F4538",
    "font": {"color": "#AAC0AA"},
    "colorway": [
        "#8CB369",  # 青草绿
        "#F4E285",  # 淡黄
        "#F4A259",  # 橙色
        "#5B8E7D",  # 墨绿
        "#BC4B51",  # 深红
        "#6B4423",  # 棕色
    ],
}


class ArcError(Exception):
    """自定义弧线绘制错误类"""

    pass


class ArcConfig:
    """统一管理弧线绘图配置"""

    def __init__(self):
        self.num_points = 1000  # 采样点数
        self.default_color = "blue"
        self.line_width = 2
        self.opacity = 1.0
        self.show_hover = True
        self.animation_duration = 1000  # 动画持续时间（毫秒）
        self.themes = {
            "plotly_dark": PLOTLY_DARK,
            "deep_sea": DEEP_SEA,
            "cyberpunk": CYBERPUNK,
            "aurora": AURORA,
            "sunset": SUNSET,
            "forest": FOREST,
        }
        self.theme = "plotly_dark"  # 默认主题

    def set_theme(self, theme_name: str) -> None:
        """设置主题"""
        if theme_name not in self.themes:
            raise ValueError(
                f"Unknown theme: {theme_name}. Available themes: {list(self.themes.keys())}"
            )
        self.theme = theme_name

    @property
    def layout(self) -> Dict:
        """获取布局配置"""
        theme = self.get_theme()
        return {
            "template": "plotly_dark",
            "showlegend": True,
            "margin": dict(l=20, r=20, t=20, b=20),
            "plot_bgcolor": theme["bgcolor"],
            "paper_bgcolor": theme["paper_bgcolor"],
            "font": theme["font"],
            "xaxis": {
                "gridcolor": theme["gridcolor"],
                "linecolor": theme["linecolor"],
                "showline": True,
                "mirror": True,
            },
            "yaxis": {
                "gridcolor": theme["gridcolor"],
                "linecolor": theme["linecolor"],
                "showline": True,
                "mirror": True,
                "scaleanchor": "x",
                "scaleratio": 1,
            },
        }

    def get_theme(self) -> Dict:
        """获取主题配置"""
        return self.themes.get(self.theme, self.themes["plotly_dark"])


# 创建全局配置实例
config = ArcConfig()


@lru_cache(maxsize=128, typed=True)
def _calculate_arc_points(
    center: Tuple[float, float],
    radius: float,
    angle1: float,
    angle2: float,
    num_points: int = 1000,
) -> Tuple[np.ndarray, np.ndarray]:
    """计算弧线点坐标（带缓存）"""
    if radius <= 0:
        raise ArcError("Radius must be positive")
    if num_points < 2:
        raise ArcError("Number of points must be at least 2")

    t = np.linspace(angle1, angle2, num_points)
    x = center[0] + radius * np.cos(t)
    y = center[1] + radius * np.sin(t)
    return x, y


def create_arc_trace(
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
    """创建弧线的跟踪对象"""
    trace = go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(color=color, width=width, dash=dash),
        opacity=opacity,
        hoverinfo="x+y" if show_hover else "none",
        hoverlabel=dict(bgcolor="white", font=dict(color="black")),
        name=name or "Arc",
    )

    if animate:
        trace.update(
            mode="lines+markers",
            marker=dict(size=8, symbol="circle"),
        )

    return trace


def validate_points(
    center: np.ndarray,
    point1: Optional[np.ndarray] = None,
    point2: Optional[np.ndarray] = None,
) -> None:
    """验证点的有效性"""
    if point1 is not None and np.allclose(point1, center):
        raise ArcError("Point1 cannot coincide with center")
    if point2 is not None and np.allclose(point2, center):
        raise ArcError("Point2 cannot coincide with center")


def arc(
    center: Union[List[float], Tuple[float, float]],
    point1: Union[List[float], Tuple[float, float]],
    point2: Union[List[float], Tuple[float, float]],
    color: str = "blue",
    width: float = 2,
    dash: Optional[str] = None,
    opacity: float = 1.0,
    label: Optional[str] = None,
    animate: bool = False,
) -> Optional[go.Figure]:
    """画顺时针弧"""
    try:
        center_array = np.array(center)
        point1_array = np.array(point1)
        point2_array = np.array(point2)

        validate_points(center_array, point1_array, point2_array)

        vector1 = point1_array - center_array
        vector2 = point2_array - center_array

        r1 = np.linalg.norm(vector1)
        theta1 = np.arctan2(vector1[1], vector1[0])
        theta2 = np.arctan2(vector2[1], vector2[0])

        if theta1 < theta2:
            theta1 += 2 * np.pi

        x, y = _calculate_arc_points(
            tuple(center), r1, theta1, theta2, config.num_points
        )

        fig = go.Figure()
        trace = create_arc_trace(
            x,
            y,
            color,
            width,
            dash,
            opacity,
            f"Arc (r={r1:.2f})",
            config.show_hover,
            animate,
        )
        fig.add_trace(trace)

        if label:
            mid_point_idx = len(x) // 2
            fig.add_annotation(
                x=x[mid_point_idx],
                y=y[mid_point_idx],
                text=label,
                showarrow=True,
                arrowhead=1,
                font=dict(color=config.get_theme()["font"]["color"]),
            )

        if animate:
            fig.update(
                frames=[
                    go.Frame(
                        data=[
                            go.Scatter(
                                x=x[:k],
                                y=y[:k],
                                mode="lines+markers",
                                line=dict(color=color, width=width),
                                marker=dict(size=8, symbol="circle"),
                            )
                        ]
                    )
                    for k in range(2, len(x), 333)
                ]
            )
            fig.update_layout(
                updatemenus=[
                    {
                        "type": "buttons",
                        "showactive": False,
                        "buttons": [
                            {
                                "label": "Play",
                                "method": "animate",
                                "args": [
                                    None,
                                    {
                                        "frame": {
                                            "duration": config.animation_duration
                                            / len(x)
                                        },
                                        "fromcurrent": True,
                                        "transition": {"duration": 0},
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
        print(f"Error drawing arc: {str(e)}")
        return None


def arc_inverse(
    center: Union[List[float], Tuple[float, float]],
    point1: Union[List[float], Tuple[float, float]],
    point2: Union[List[float], Tuple[float, float]],
    color: str = "blue",
    width: float = 2,
    dash: Optional[str] = None,
    opacity: float = 1.0,
    label: Optional[str] = None,
    animate: bool = False,
) -> Optional[go.Figure]:
    """画逆时针弧"""
    try:
        center_array = np.array(center)
        point1_array = np.array(point1)
        point2_array = np.array(point2)

        validate_points(center_array, point1_array, point2_array)

        vector1 = point1_array - center_array
        vector2 = point2_array - center_array

        r1 = np.linalg.norm(vector1)
        theta1 = np.arctan2(vector1[1], vector1[0])
        theta2 = np.arctan2(vector2[1], vector2[0])

        if theta2 < theta1:
            theta2 += 2 * np.pi

        x, y = _calculate_arc_points(
            tuple(center), r1, theta1, theta2, config.num_points
        )

        fig = go.Figure()
        trace = create_arc_trace(
            x,
            y,
            color,
            width,
            dash,
            opacity,
            f"Arc (r={r1:.2f})",
            config.show_hover,
            animate,
        )
        fig.add_trace(trace)

        if label:
            mid_point_idx = len(x) // 2
            fig.add_annotation(
                x=x[mid_point_idx],
                y=y[mid_point_idx],
                text=label,
                showarrow=True,
                arrowhead=1,
                font=dict(color=config.get_theme()["font"]["color"]),
            )

        if animate:
            fig.update(
                frames=[
                    go.Frame(
                        data=[
                            go.Scatter(
                                x=x[:k],
                                y=y[:k],
                                mode="lines+markers",
                                line=dict(color=color, width=width),
                                marker=dict(size=8, symbol="circle"),
                            )
                        ]
                    )
                    for k in range(2, len(x), 10)
                ]
            )
            fig.update_layout(
                updatemenus=[
                    {
                        "type": "buttons",
                        "showactive": False,
                        "buttons": [
                            {
                                "label": "Play",
                                "method": "animate",
                                "args": [
                                    None,
                                    {
                                        "frame": {
                                            "duration": config.animation_duration
                                            / len(x)
                                        },
                                        "fromcurrent": True,
                                        "transition": {"duration": 0},
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
        print(f"Error drawing arc: {str(e)}")
        return None


def arc_degree(
    center: Union[List[float], Tuple[float, float]],
    radius: float,
    angle1: float,
    angle2: float,
    color: str = "blue",
    width: float = 2,
    dash: Optional[str] = None,
    opacity: float = 1.0,
    label: Optional[str] = None,
    animate: bool = False,
) -> Optional[go.Figure]:
    """通过角度画圆弧"""
    try:
        if radius <= 0:
            raise ArcError("Radius must be positive")

        if angle1 < angle2:
            x, y = _calculate_arc_points(
                tuple(center), radius, angle1, angle2, config.num_points
            )

            fig = go.Figure()
            trace = create_arc_trace(
                x,
                y,
                color,
                width,
                dash,
                opacity,
                f"Arc (r={radius:.2f})",
                config.show_hover,
                animate,
            )
            fig.add_trace(trace)

            if label:
                mid_point_idx = len(x) // 2
                fig.add_annotation(
                    x=x[mid_point_idx],
                    y=y[mid_point_idx],
                    text=label,
                    showarrow=True,
                    arrowhead=1,
                    font=dict(color=config.get_theme()["font"]["color"]),
                )

            if animate:
                fig.update(
                    frames=[
                        go.Frame(
                            data=[
                                go.Scatter(
                                    x=x[:k],
                                    y=y[:k],
                                    mode="lines+markers",
                                    line=dict(color=color, width=width),
                                    marker=dict(size=8, symbol="circle"),
                                )
                            ]
                        )
                        for k in range(2, len(x), 10)
                    ]
                )
                fig.update_layout(
                    updatemenus=[
                        {
                            "type": "buttons",
                            "showactive": False,
                            "buttons": [
                                {
                                    "label": "Play",
                                    "method": "animate",
                                    "args": [
                                        None,
                                        {
                                            "frame": {
                                                "duration": config.animation_duration
                                                / len(x)
                                            },
                                            "fromcurrent": True,
                                            "transition": {"duration": 0},
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
        print(f"Error drawing arc: {str(e)}")
        return None


def arc_degree_inverse(
    center: Union[List[float], Tuple[float, float]],
    radius: float,
    angle1: float,
    angle2: float,
    color: str = "blue",
    width: float = 2,
    dash: Optional[str] = None,
    opacity: float = 1.0,
    label: Optional[str] = None,
    animate: bool = False,
) -> Optional[go.Figure]:
    """通过角度画逆时针圆弧"""
    try:
        if radius <= 0:
            raise ArcError("Radius must be positive")

        x, y = _calculate_arc_points(
            tuple(center), radius, angle2 - 2 * np.pi, angle1, config.num_points
        )

        fig = go.Figure()
        trace = create_arc_trace(
            x,
            y,
            color,
            width,
            dash,
            opacity,
            f"Arc (r={radius:.2f})",
            config.show_hover,
            animate,
        )
        fig.add_trace(trace)

        if label:
            mid_point_idx = len(x) // 2
            fig.add_annotation(
                x=x[mid_point_idx],
                y=y[mid_point_idx],
                text=label,
                showarrow=True,
                arrowhead=1,
                font=dict(color=config.get_theme()["font"]["color"]),
            )

        if animate:
            fig.update(
                frames=[
                    go.Frame(
                        data=[
                            go.Scatter(
                                x=x[:k],
                                y=y[:k],
                                mode="lines+markers",
                                line=dict(color=color, width=width),
                                marker=dict(size=8, symbol="circle"),
                            )
                        ]
                    )
                    for k in range(2, len(x), 10)
                ]
            )
            fig.update_layout(
                updatemenus=[
                    {
                        "type": "buttons",
                        "showactive": False,
                        "buttons": [
                            {
                                "label": "Play",
                                "method": "animate",
                                "args": [
                                    None,
                                    {
                                        "frame": {
                                            "duration": config.animation_duration
                                            / len(x)
                                        },
                                        "fromcurrent": True,
                                        "transition": {"duration": 0},
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
        print(f"Error drawing arc: {str(e)}")
        return None


# 测试代码
if __name__ == "__main__":
    # 测试主题切换
    for theme_name in config.themes.keys():
        print(f"Testing theme: {theme_name}")
        config.set_theme(theme_name)

        # 测试基本弧线
        fig = arc(
            [0, 0], [1, 0], [0, 1], color="red", width=3, label="Test Arc", animate=True
        )
        if fig:
            fig.show()

        # 测试逆时针弧线
        fig = arc_inverse(
            [0, 0], [1, 0], [0, 1], color="blue", dash="dash", opacity=0.8, animate=True
        )
        if fig:
            fig.show()

        # 测试角度弧线
        fig = arc_degree([0, 0], 1, 0, np.pi / 2, color="green", width=2, animate=True)
        if fig:
            fig.show()
