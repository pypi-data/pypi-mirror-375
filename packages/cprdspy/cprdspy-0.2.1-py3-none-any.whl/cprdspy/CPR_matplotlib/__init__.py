"""
cprdspy.CPR_matplotlib - Matplotlib 绘图模块

这个模块提供了使用 Matplotlib 绘制各种几何图形的功能，包括：
- 圆形 (Circles)
- 弧线 (Arcs)
- 螺旋线 (Spirals)
- 花朵 (Flowers)
- 点阵 (Dots)
- 线条 (Lines)
- 波形 (Waves)

所有函数都以 _mpl 后缀结尾，以区分于 Plotly 版本。
"""

import os
import importlib
import sys
from typing import List, Dict, Any, Callable

# 初始化导出的函数列表
__all__: List[str] = []

# 导入 Circles 模块
try:
    from .Circles.circle import (
        circle as circle_modern_mpl,
        draw_circle as draw_circle_mpl,
    )
    
    __all__.extend([
        "circle_modern_mpl",
        "draw_circle_mpl",
    ])
except ImportError:
    pass

# 导入 Arcs 模块
try:
    from .Arcs.arc import (
        arc as arc_mpl,
        arc_inverse as arc_inverse_mpl,
        arc_degree as arc_degree_mpl,
        arc_degree_inverse as arc_degree_inverse_mpl,
        arc_dot as arc_dot_mpl,
    )
    
    __all__.extend([
        "arc_mpl",
        "arc_inverse_mpl",
        "arc_degree_mpl",
        "arc_degree_inverse_mpl",
        "arc_dot_mpl",
    ])
except ImportError:
    pass

# 导入 Spirals 模块
try:
    from .Spirals.spiral import (
        logSpiral as logSpiral_mpl,
        logSpiral_out as logSpiral_out_mpl,
        logSpiral_in as logSpiral_in_mpl,
        n_spiral as n_spiral_mpl,
        n_spiral_rotate as n_spiral_rotate_mpl,
        n_spiral_rotate_out as n_spiral_rotate_out_mpl,
        n_spiral_rotate_in as n_spiral_rotate_in_mpl,
        calla_petal as calla_petal_mpl,
        calla_by_petal as calla_by_petal_mpl,
    )
    
    __all__.extend([
        "logSpiral_mpl",
        "logSpiral_out_mpl",
        "logSpiral_in_mpl",
        "n_spiral_mpl",
        "n_spiral_rotate_mpl",
        "n_spiral_rotate_out_mpl",
        "n_spiral_rotate_in_mpl",
        "calla_petal_mpl",
        "calla_by_petal_mpl",
    ])
except ImportError:
    pass

# 导入 Flowers 模块
try:
    from .Flowers.flower import (
        n_flower_arc as n_flower_arc_mpl,
        n_flowers_arc_p as n_flowers_arc_p_mpl,
        n_flower_petal as n_flower_petal_mpl,
        one_flower_petal as one_flower_petal_mpl,
        one_flower_arc as one_flower_arc_mpl,
        one_flower_flower_arc_with_field as one_flower_flower_arc_with_field_mpl,
        flowers_flower_by_petal as flowers_flower_by_petal_mpl,
        flowers_flower_by_arc as flowers_flower_by_arc_mpl,
        flowers_flower_by_flower_arc_with_field as flowers_flower_by_flower_arc_with_field_mpl,
        flowers_flower_by_petal_multi as flowers_flower_by_petal_multi_mpl,
        rotate_point as rotate_point_mpl,
        oval_petal as oval_petal_mpl,
        oval_petal_a as oval_petal_a_mpl,
        n_flowers_petal_fill as n_flowers_petal_fill_mpl,
        oval_petal_flower as oval_petal_flower_mpl,
        oval_petal_flower_a as oval_petal_flower_a_mpl,
    )
    
    __all__.extend([
        "n_flower_arc_mpl",
        "n_flowers_arc_p_mpl",
        "n_flower_petal_mpl",
        "one_flower_petal_mpl",
        "one_flower_arc_mpl",
        "one_flower_flower_arc_with_field_mpl",
        "flowers_flower_by_petal_mpl",
        "flowers_flower_by_arc_mpl",
        "flowers_flower_by_flower_arc_with_field_mpl",
        "flowers_flower_by_petal_multi_mpl",
        "rotate_point_mpl",
        "oval_petal_mpl",
        "oval_petal_a_mpl",
        "n_flowers_petal_fill_mpl",
        "oval_petal_flower_mpl",
        "oval_petal_flower_a_mpl",
    ])
except ImportError:
    pass

# 动态导入其他子目录中的模块
def import_submodules() -> None:
    """动态导入所有子目录中的模块并添加到 __all__"""
    base_path = os.path.dirname(__file__)
    
    # 获取所有子目录
    subdirs = [
        d for d in os.listdir(base_path) 
        if os.path.isdir(os.path.join(base_path, d)) and not d.startswith('__')
    ]
    
    for subdir in subdirs:
        subdir_path = os.path.join(base_path, subdir)
        
        # 获取子目录中的所有 Python 文件
        py_files = [
            f[:-3] for f in os.listdir(subdir_path)
            if f.endswith('.py') and not f.startswith('__')
        ]
        
        # 导入每个 Python 文件
        for py_file in py_files:
            try:
                # 构建模块路径
                module_path = f"cprdspy.CPR_matplotlib.{subdir}.{py_file}"
                
                # 尝试导入模块
                module = importlib.import_module(module_path)
                
                # 获取模块中的所有函数
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    # 只导出非私有函数
                    if callable(attr) and not attr_name.startswith('_'):
                        # 为函数添加 _mpl 后缀
                        new_name = f"{attr_name}_mpl"
                        
                        # 避免重复导入
                        if new_name not in globals():
                            globals()[new_name] = attr
                            if new_name not in __all__:
                                __all__.append(new_name)
            except (ImportError, AttributeError) as e:
                # 忽略导入错误，继续处理其他模块
                pass

# 执行动态导入
import_submodules()