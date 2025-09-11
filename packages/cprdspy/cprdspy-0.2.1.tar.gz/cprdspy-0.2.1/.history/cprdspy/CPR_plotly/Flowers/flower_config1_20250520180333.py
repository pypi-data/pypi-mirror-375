import numpy as np
import plotly.graph_objects as go
from ..Arcs.arc_config import arc_degree, config, ArcError
from functools import lru_cache
from typing import Tuple, List, Optional, Union, Dict

class FlowerError(Exception):
    """自定义花朵绘制错误类"""
    pass

class FlowerConfig:
    """统一管理花朵绘图配置"""
    
    def __init__(self):
        self.num_points = 1000  # 采样点数
        self.default_color = "#FF69B4"  # 默认粉色
        self.default_field_color = "#FFD700"  # 默认填充金色
        self.line_width = 2
        self.opacity = 0.8
        self.show_hover = True
        self.animation_duration = 1000  # 动画持续时间（毫秒）

    @property
    def layout(self) -> Dict:
        """获取布局配置"""
        theme = config.get_theme()  # 使用arc_config中的主题
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

# 创建全局配置实例
flower_config = FlowerConfig()

@lru_cache(maxsize=128)
def _calculate_flower_parameters(R: float, n: float) -> Tuple[float, float, float]:
    """计算花瓣参数（带缓存）"""
    alpha = 2 * np.pi / n
    a = R * np.sin(np.pi / n)
    beta = np.arccos(a)
    return alpha, a, beta

def create_flower_trace(
    x: np.ndarray,
    y: np.ndarray,
    color: str,
    width: float = 2,
    opacity: float = 0.8,
    name: Optional[str] = None,
    fill: Optional[str] = None,
    fillcolor: Optional[str] = None,
) -> go.Scatter:
    """创建花瓣的跟踪对象"""
    return go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(color=color, width=width),
        opacity=opacity,
        name=name or "Flower",
        fill=fill,
        fillcolor=fillcolor,
    )

def flower_petal(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    n: int,
    theta: float = 0,
    color: str = None,
    width: float = None,
    opacity: float = None,
    label: Optional[str] = None,
    fill: bool = False,
    animate: bool = False,
) -> Optional[go.Figure]:
    """绘制单个花瓣"""
    try:
        if R <= 0 or r <= 0:
            raise FlowerError("Radius must be positive")
        
        # 使用默认值
        color = color or flower_config.default_color
        width = width or flower_config.line_width
        opacity = opacity or flower_config.opacity

        alpha, a, beta = _calculate_flower_parameters(R, n)
        
        if r < a:
            raise FlowerError(f"r={r} is too small to form a petal (minimum r={a})")

        fig = go.Figure()
        
        # 计算花瓣的两个圆心
        center1 = (
            np.cos(theta + alpha/2) * R + center[0],
            np.sin(theta + alpha/2) * R + center[1]
        )
        center2 = (
            np.cos(theta + alpha/2 - 2*np.pi/n) * R + center[0],
            np.sin(theta + alpha/2 - 2*np.pi/n) * R + center[1]
        )

        # 创建两条弧线
        theta_arc = np.pi/2 - np.pi/n + np.arccos(a/r)
        arc1 = arc_degree(
            center=center1,
            radius=r,
            angle1=np.pi + alpha/2 + theta,
            angle2=np.pi + alpha/2 + theta + theta_arc,
            color=color,
            width=width,
            opacity=opacity,
        )
        arc2 = arc_degree(
            center=center2,
            radius=r,
            angle1=np.pi/2 - beta + theta,
            angle2=np.pi/2 - beta + theta + theta_arc,
            color=color,
            width=width,
            opacity=opacity,
        )

        # 将两条弧线添加到图中
        if arc1 and arc2:
            for trace in arc1.data:
                fig.add_trace(trace)
            for trace in arc2.data:
                fig.add_trace(trace)

        if label:
            # 添加标签在花瓣中心位置
            center_x = (center1[0] + center2[0]) / 2
            center_y = (center1[1] + center2[1]) / 2
            fig.add_annotation(
                x=center_x,
                y=center_y,
                text=label,
                showarrow=True,
                arrowhead=1,
                font=dict(color=config.get_theme()["font"]["color"])
            )

        fig.update_layout(**flower_config.layout)
        return fig

    except Exception as e:
        print(f"Error drawing flower petal: {str(e)}")
        return None

def flower(
    center: Union[List[float], Tuple[float, float]],
    R: float,
    r: float,
    N: int,
    n: int,
    theta: float = 0,
    color: str = None,
    width: float = None,
    opacity: float = None,
    labels: Optional[List[str]] = None,
) -> Optional[go.Figure]:
    """绘制完整的花"""
    try:
        fig = go.Figure()
        
        for i in range(N):
            angle = theta + 2 * np.pi * i / N
            petal = flower_petal(
                center=center,
                R=R,
                r=r,
                n=n,
                theta=angle,
                color=color,
                width=width,
                opacity=opacity,
                label=labels[i] if labels and i < len(labels) else None
            )
            if petal:
                for trace in petal.data:
                    fig.add_trace(trace)

        fig.update_layout(**flower_config.layout)
        return fig

    except Exception as e:
        print(f"Error drawing flower: {str(e)}")
        return None

# 导出主要函数和配置
__all__ = ['flower_config', 'flower_petal', 'flower', 'FlowerError']


# 设置主题（使用arc_config中的主题）
config.set_theme("sunset")

# 绘制一朵花
fig = flower(
    center=[0, 0],
    R=1,
    r=0.5,
    N=6,  # 6片花瓣
    n=4,  # 每片花瓣的复杂度
    color="red",
    labels=["1", "2", "3", "4", "5", "6"]  # 为每片花瓣添加标签
)
fig.show()