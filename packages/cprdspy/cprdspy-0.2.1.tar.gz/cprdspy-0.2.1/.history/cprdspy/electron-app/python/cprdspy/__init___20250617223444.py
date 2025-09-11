"""
CPR波形可视化库

此模块提供了用于创建和显示CPR波形的函数和类。
"""

from .CPR_plotly.Waves.wave_config import (
    config,
    wave_circle_arithmetic,
    wave_circle_geometric,
    wave_circle_ari_o,
    wave_circle_ari_i,
    wave_circle_ari,
    wave_circle_pro_o,
    wave_circle_pro_i,
    wave_circle_pro,
)


# 主题相关函数
def set_theme(theme_name):
    """设置当前主题"""
    config.theme = theme_name
    return theme_name


def get_available_themes():
    """获取可用的主题列表"""
    return ["classic", "dark", "light", "colorful", "minimal"]


# 导出主要的函数和类
__all__ = [
    "config",
    "set_theme",
    "get_available_themes",
    "wave_circle_arithmetic",
    "wave_circle_geometric",
    "wave_circle_ari_o",
    "wave_circle_ari_i",
    "wave_circle_ari",
    "wave_circle_pro_o",
    "wave_circle_pro_i",
    "wave_circle_pro",
]
