"""
全局配置模块 - 管理sprdspy库的绘图设置

此模块提供了一个统一的配置系统，用于管理绘图的背景、主题、坐标轴等设置。
用户可以通过全局config实例来修改这些设置，影响整个库的绘图风格。
"""

import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List, Union, Tuple
from functools import lru_cache

# 预定义主题
# 经典主题
CLASSIC = {
    "bgcolor": "#FFFFFF",  # 白色背景
    "gridcolor": "#E5ECF6",  # 浅灰网格
    "linecolor": "#444444",  # 深灰线条
    "paper_bgcolor": "#FFFFFF",  # 白色画布
    "plot_bgcolor": "#FFFFFF",  # 白色绘图区
    "font": {"color": "#444444"},  # 深灰字体
    "colorway": [  # 经典配色
        "#1f77b4",  # 蓝色
        "#ff7f0e",  # 橙色
        "#2ca02c",  # 绿色
        "#d62728",  # 红色
        "#9467bd",  # 紫色
        "#8c564b",  # 棕色
        "#e377c2",  # 粉色
        "#7f7f7f",  # 灰色
        "#bcbd22",  # 黄绿色
        "#17becf",  # 青色
    ],
}

# 暗黑主题
DARK = {
    "bgcolor": "#1f2630",  # 深色背景
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

# 深海主题
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

# 赛博朋克主题
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

# 极光主题
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

# 日落主题
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

# 森林主题
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


class ConfigError(Exception):
    """配置相关的自定义异常"""

    pass


class Config:
    """全局绘图配置管理类

    管理sprdspy库的全局绘图设置，包括主题、采样点数、线条样式等。
    """

    def __init__(self):
        # 基本绘图参数
        self.num_points = 1000  # 默认采样点数
        self.line_width = 2  # 默认线宽
        self.opacity = 1.0  # 默认不透明度
        self.show_hover = True  # 是否显示悬停信息
        self.show_legend = True  # 是否显示图例
        self.equal_aspect = True  # 是否保持坐标轴等比例

        # 动画相关
        self.animation_duration = 1000  # 动画持续时间（毫秒）
        self.animation_enabled = False  # 是否启用动画

        # 坐标轴设置
        self.show_grid = True  # 是否显示网格
        self.show_axis = True  # 是否显示坐标轴
        self.axis_mirror = True  # 坐标轴是否镜像

        # 主题设置
        self.themes = {
            "classic": CLASSIC,
            "dark": DARK,
            "deep_sea": DEEP_SEA,
            "cyberpunk": CYBERPUNK,
            "aurora": AURORA,
            "sunset": SUNSET,
            "forest": FOREST,
        }
        self.theme = "classic"  # 默认主题

        # 默认颜色
        self._default_color = None  # 将在get_default_color中懒加载

    def set_theme(self, theme_name: str) -> None:
        """设置绘图主题

        Args:
            theme_name: 主题名称，必须是预定义主题之一

        Raises:
            ValueError: 如果指定了未知的主题名称
        """
        if theme_name not in self.themes:
            raise ValueError(
                f"未知主题: {theme_name}. 可用主题: {list(self.themes.keys())}"
            )
        self.theme = theme_name
        # 重置默认颜色，使其在下次访问时重新加载
        self._default_color = None

    def get_theme(self) -> Dict:
        """获取当前主题配置

        Returns:
            包含当前主题颜色和样式的字典
        """
        return self.themes.get(self.theme, self.themes["classic"])

    @property
    def default_color(self) -> str:
        """获取当前主题的默认颜色

        Returns:
            默认颜色的十六进制代码
        """
        if self._default_color is None:
            # 懒加载默认颜色，使用当前主题的第一个颜色
            self._default_color = self.get_theme()["colorway"][0]
        return self._default_color

    @property
    def layout(self) -> Dict[str, Any]:
        """获取当前布局配置

        Returns:
            适用于plotly图形的布局配置字典
        """
        theme = self.get_theme()

        # 基本布局
        layout = {
            "showlegend": self.show_legend,
            "margin": dict(l=20, r=20, t=20, b=20),
            "plot_bgcolor": theme["plot_bgcolor"],
            "paper_bgcolor": theme["paper_bgcolor"],
            "font": theme["font"],
        }

        # 坐标轴设置
        axis_config = {}
        if self.show_grid:
            axis_config["gridcolor"] = theme["gridcolor"]
        else:
            axis_config["showgrid"] = False

        if self.show_axis:
            axis_config["linecolor"] = theme["linecolor"]
            axis_config["showline"] = True
        else:
            axis_config["showline"] = False

        if self.axis_mirror:
            axis_config["mirror"] = True

        # 应用坐标轴设置
        layout["xaxis"] = axis_config.copy()
        layout["yaxis"] = axis_config.copy()

        # 保持坐标轴等比例
        if self.equal_aspect:
            layout["yaxis"]["scaleanchor"] = "x"
            layout["yaxis"]["scaleratio"] = 1

        return layout

    def apply_to_figure(self, fig: go.Figure) -> go.Figure:
        """将当前配置应用到图形对象

        Args:
            fig: Plotly图形对象

        Returns:
            应用了配置的图形对象
        """
        fig.update_layout(**self.layout)
        return fig

    def create_animation_buttons(self) -> List[Dict[str, Any]]:
        """创建动画控制按钮

        Returns:
            动画控制按钮的配置字典列表
        """
        if not self.animation_enabled:
            return []

        return [
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
                                "frame": {"duration": self.animation_duration},
                                "fromcurrent": True,
                                "transition": {"duration": 0},
                            },
                        ],
                    }
                ],
            }
        ]

    @lru_cache(maxsize=128)
    def calculate_points(
        self, start: float, end: float, num_points: Optional[int] = None
    ) -> np.ndarray:
        """计算采样点（带缓存）

        Args:
            start: 起始值
            end: 结束值
            num_points: 采样点数，如果为None则使用默认值

        Returns:
            均匀分布的采样点数组
        """
        points = num_points if num_points is not None else self.num_points
        if points < 2:
            raise ConfigError("采样点数必须至少为2")
        return np.linspace(start, end, points)


# 创建全局配置实例
config = Config()


def set_theme(theme_name: str) -> None:
    """设置全局主题

    Args:
        theme_name: 主题名称
    """
    config.set_theme(theme_name)


def get_available_themes() -> List[str]:
    """获取所有可用主题名称

    Returns:
        主题名称列表
    """
    return list(config.themes.keys())


def apply_config(fig: go.Figure) -> go.Figure:
    """应用全局配置到图形

    Args:
        fig: Plotly图形对象

    Returns:
        应用了配置的图形对象
    """
    return config.apply_to_figure(fig)


def reset_config() -> None:
    """重置配置到默认值"""
    global config
    config = Config()


# 导出主要的函数和类
__all__ = [
    "Config",
    "ConfigError",
    "config",
    "set_theme",
    "get_available_themes",
    "apply_config",
    "reset_config",
]
