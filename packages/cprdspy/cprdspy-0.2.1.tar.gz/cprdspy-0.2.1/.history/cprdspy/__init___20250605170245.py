"""
cprdspy - 一个用于绘制各种几何图形的Python库

这个库提供了绘制圆形、弧线、点阵、线条、螺旋线和花朵等几何图形的功能。
所有图形都使用Plotly绘制，支持交互式显示和自定义样式。
"""

# 导入各个模块的公开API
from .CPR_plotly.Circles.circle_config import (
    CircleConfig,
    CircleError,
    config as circle_config,
    circle,
    circle_from_point,
    concentric_circles,
    concentric_circles_geometric,
)

from .CPR_plotly.Arcs.arc_config import (
    ArcConfig,
    ArcError,
    config as arc_config,
    arc,
    arc_inverse,
    arc_degree,
    arc_degree_inverse,
)

from .CPR_plotly.Dots.dot_config import (
    DotConfig,
    DotError,
    config as dot_config,
    n_points,
    draw_points,
    n_points_array,
    n_points_array_inner,
    n_points_array_outer,
    n_points_array_rotate,
    n_points_array_inner_rotate,
    n_points_array_outer_rotate,
    draw_n_points_array,
    draw_n_points_array_inner,
    draw_n_points_array_outer,
    colorful_dots,
)

from .CPR_plotly.Lines.line_config import (
    LineConfig,
    LineError,
    config as line_config,
    n_points as line_n_points,
    draw_points as line_draw_points,
    connect_points,
    multi_polygon,
    metatron_cube,
    swastika,
    multi_swastika,
)

from .CPR_plotly.Spirals.spiral_config import (
    SpiralConfig,
    SpiralError,
    config as spiral_config,
    logSpiral,
    logSpiral_out,
    logSpiral_in,
    n_spiral,
    n_spiral_rotate,
    n_spiral_rotate_out,
    n_spiral_rotate_in,
    calla_petal,
    calla_by_petal,
    rodincoil,
    rodincoil_colorful,
)

from .CPR_plotly.Flowers.flower_config import (
    FlowerConfig,
    FlowerError,
    config as flower_config,
    n_flower_petal,
    n_flower_arc,
    n_flowers_flower_arc_with_field,
    one_flower_petal,
    one_flower_arc,
    one_flower_flower_arc_with_field,
    flowers_flower_by_petal,
    flowers_flower_by_arc,
    flowers_flower_by_flower_arc_with_field,
    flowers_flower_by_petal_multi,
    flower_by_petal_fill,
    n_lily_petal_fill,
)

from .CPR_plotly.Waves.wave_config import (
    WaveConfig,
    WaveError,
    config as wave_config,
    wave_circle_arithmetic,
    wave_circle_geometric,
    wave_circle_ari_o,
    wave_circle_ari_i,
    wave_circle_ari,
    wave_circle_pro_o,
    wave_circle_pro_i,
    wave_circle_pro,
)

# 导出所有公开API
__all__ = [
    # 圆形模块
    "CircleConfig",
    "CircleError",
    "circle_config",
    "circle",
    "circle_from_point",
    "concentric_circles",
    "concentric_circles_geometric",
    # 弧线模块
    "ArcConfig",
    "ArcError",
    "arc_config",
    "arc",
    "arc_inverse",
    "arc_degree",
    "arc_degree_inverse",
    # 点阵模块
    "DotConfig",
    "DotError",
    "dot_config",
    "n_points",
    "draw_points",
    "n_points_array",
    "n_points_array_inner",
    "n_points_array_outer",
    "n_points_array_rotate",
    "n_points_array_inner_rotate",
    "n_points_array_outer_rotate",
    "draw_n_points_array",
    "draw_n_points_array_inner",
    "draw_n_points_array_outer",
    "colorful_dots",
    # 线条模块
    "LineConfig",
    "LineError",
    "line_config",
    "line_n_points",
    "line_draw_points",
    "connect_points",
    "multi_polygon",
    "metatron_cube",
    "swastika",
    "multi_swastika",
    # 螺旋线模块
    "SpiralConfig",
    "SpiralError",
    "spiral_config",
    "logSpiral",
    "logSpiral_out",
    "logSpiral_in",
    "n_spiral",
    "n_spiral_rotate",
    "n_spiral_rotate_out",
    "n_spiral_rotate_in",
    "calla_petal",
    "calla_by_petal",
    "rodincoil",
    "rodincoil_colorful",
    # 花朵模块
    "FlowerConfig",
    "FlowerError",
    "flower_config",
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
    # 波形模块
    "WaveConfig",
    "WaveError",
    "wave_config",
    "wave_circle_arithmetic",
    "wave_circle_geometric",
    "wave_circle_ari_o",
    "wave_circle_ari_i",
    "wave_circle_ari",
    "wave_circle_pro_o",
    "wave_circle_pro_i",
    "wave_circle_pro",
]

# 版本信息
__version__ = "0.1.0"
