"""
波形可视化Dash应用

此模块提供了一个交互式界面来展示和调整cprdspy库中的各种波形。
支持实时参数调整和主题切换。
"""

import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import plotly.graph_objects as go
import numpy as np
from cprdspy import (
    config,
    set_theme,
    get_available_themes,
    wave_circle_arithmetic,
    wave_circle_geometric,
    wave_circle_ari_o,
    wave_circle_ari_i,
    wave_circle_ari,
    wave_circle_pro_o,
    wave_circle_pro_i,
    wave_circle_pro,
)

# 创建Dash应用
app = dash.Dash(__name__)
server = app.server  # 导出服务器实例，用于生产环境

# 定义波形类型选项
WAVE_TYPES = {
    "wave_circle_arithmetic": "等差圆形波 (Both)",
    "wave_circle_ari_o": "等差圆形波 (Out)",
    "wave_circle_ari_i": "等差圆形波 (In)",
    "wave_circle_geometric": "等比圆形波 (Both)",
    "wave_circle_pro_o": "等比圆形波 (Out)",
    "wave_circle_pro_i": "等比圆形波 (In)",
}

# 波形函数映射
WAVE_FUNCTIONS = {
    "wave_circle_arithmetic": wave_circle_arithmetic,
    "wave_circle_ari_o": wave_circle_ari_o,
    "wave_circle_ari_i": wave_circle_ari_i,
    "wave_circle_geometric": wave_circle_geometric,
    "wave_circle_pro_o": wave_circle_pro_o,
    "wave_circle_pro_i": wave_circle_pro_i,
}

# 应用布局
app.layout = html.Div(
    [
        # 标题栏
        html.Div(
            [
                # 侧边栏切换按钮
                html.Button(
                    "☰",
                    id="sidebar-toggle",
                    style={
                        "fontSize": "24px",
                        "border": "none",
                        "background": "none",
                        "cursor": "pointer",
                        "marginRight": "20px",
                    },
                ),
                html.H1("波形可视化", style={"flex": "1", "margin": "0"}),
                html.Div(
                    [
                        html.Label("主题：", style={"marginRight": "10px"}),
                        dcc.Dropdown(
                            id="theme-selector",
                            options=[
                                {"label": theme, "value": theme}
                                for theme in get_available_themes()
                            ],
                            value="classic",
                            style={"width": "200px"},
                        ),
                    ],
                    style={"display": "flex", "alignItems": "center"},
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "padding": "20px",
                "borderBottom": "1px solid #ddd",
                "backgroundColor": "white",
                "position": "fixed",
                "top": 0,
                "left": 0,
                "right": 0,
                "zIndex": 1000,
            },
        ),
        # 主要内容区域
        html.Div(
            [
                # 侧边栏控制面板
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3("参数控制"),
                                # 波形类型选择
                                html.Label("波形类型"),
                                dcc.Dropdown(
                                    id="wave-type",
                                    options=[
                                        {"label": v, "value": k}
                                        for k, v in WAVE_TYPES.items()
                                    ],
                                    value="wave_circle_arithmetic",
                                ),
                                # 振幅控制
                                html.Label("振幅 (A)"),
                                html.Div(
                                    [
                                        html.Div(
                                            dcc.Slider(
                                                id="amplitude-slider",
                                                min=0.1,
                                                max=6.0,
                                                step=0.01,
                                                value=0.5,
                                                marks={
                                                    i / 2: str(i / 2)
                                                    for i in range(1, 6)
                                                },
                                            ),
                                            style={
                                                "width": "300px",
                                                "marginRight": "10px",
                                            },
                                        ),
                                        dcc.Input(
                                            id="amplitude-input",
                                            type="number",
                                            min=0.1,
                                            max=6.0,
                                            step=0.01,
                                            value=0.5,
                                            style={"width": "80px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                # 频率控制
                                html.Label("频率 (F)"),
                                html.Div(
                                    [
                                        html.Div(
                                            dcc.Slider(
                                                id="frequency-slider",
                                                min=1,
                                                max=12,
                                                step=1,
                                                value=3,
                                                marks={
                                                    i: str(i) for i in range(1, 13, 2)
                                                },
                                            ),
                                            style={
                                                "width": "300px",
                                                "marginRight": "10px",
                                            },
                                        ),
                                        dcc.Input(
                                            id="frequency-input",
                                            type="number",
                                            min=1,
                                            max=12,
                                            step=1,
                                            value=3,
                                            style={"width": "80px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                # 周期控制
                                html.Label("周期 (P)"),
                                html.Div(
                                    [
                                        html.Div(
                                            dcc.Slider(
                                                id="period-slider",
                                                min=3,
                                                max=36,
                                                step=1,
                                                value=11,
                                                marks={
                                                    i: str(i) for i in range(3, 36, 3)
                                                },
                                            ),
                                            style={
                                                "width": "300px",
                                                "marginRight": "10px",
                                            },
                                        ),
                                        dcc.Input(
                                            id="period-input",
                                            type="number",
                                            min=3,
                                            max=36,
                                            step=1,
                                            value=11,
                                            style={"width": "80px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                # 相位控制
                                html.Label("相位 (θ)"),
                                html.Div(
                                    [
                                        html.Div(
                                            dcc.Slider(
                                                id="theta-slider",
                                                min=0,
                                                max=2 * np.pi,
                                                step=np.pi / 12,
                                                value=0,
                                                marks={
                                                    0: "0",
                                                    np.pi / 2: "π/2",
                                                    np.pi: "π",
                                                    3 * np.pi / 2: "3π/2",
                                                    2 * np.pi: "2π",
                                                },
                                            ),
                                            style={
                                                "width": "300px",
                                                "marginRight": "10px",
                                            },
                                        ),
                                        dcc.Input(
                                            id="theta-input",
                                            type="number",
                                            min=0,
                                            max=2 * np.pi,
                                            step=np.pi / 12,
                                            value=0,
                                            style={"width": "80px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                # 基准半径控制
                                html.Label("基准半径 (R)"),
                                html.Div(
                                    [
                                        html.Div(
                                            dcc.Slider(
                                                id="radius-slider",
                                                min=0.5,
                                                max=6.0,
                                                step=0.1,
                                                value=1.0,
                                                marks={
                                                    i / 2: str(i / 2)
                                                    for i in range(1, 7)
                                                },
                                            ),
                                            style={
                                                "width": "300px",
                                                "marginRight": "10px",
                                            },
                                        ),
                                        dcc.Input(
                                            id="radius-input",
                                            type="number",
                                            min=0.5,
                                            max=6.0,
                                            step=0.1,
                                            value=1.0,
                                            style={"width": "80px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                # 线宽控制
                                html.Label("线宽"),
                                html.Div(
                                    [
                                        html.Div(
                                            dcc.Slider(
                                                id="line-width-slider",
                                                min=1,
                                                max=5,
                                                step=0.5,
                                                value=2,
                                                marks={i: str(i) for i in range(1, 6)},
                                            ),
                                            style={
                                                "width": "300px",
                                                "marginRight": "10px",
                                            },
                                        ),
                                        dcc.Input(
                                            id="line-width-input",
                                            type="number",
                                            min=1,
                                            max=5,
                                            step=0.5,
                                            value=2,
                                            style={"width": "80px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                # 透明度控制
                                html.Label("透明度"),
                                html.Div(
                                    [
                                        html.Div(
                                            dcc.Slider(
                                                id="opacity-slider",
                                                min=0.1,
                                                max=1.0,
                                                step=0.1,
                                                value=1.0,
                                                marks={
                                                    i / 10: str(i / 10)
                                                    for i in range(1, 11, 2)
                                                },
                                            ),
                                            style={
                                                "width": "300px",
                                                "marginRight": "10px",
                                            },
                                        ),
                                        dcc.Input(
                                            id="opacity-input",
                                            type="number",
                                            min=0.1,
                                            max=1.0,
                                            step=0.1,
                                            value=1.0,
                                            style={"width": "80px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                # 颜色控制
                                html.Label("颜色"),
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            id="color",
                                            options=[
                                                {"label": "蓝色", "value": "#1f77b4"},
                                                {"label": "红色", "value": "#d62728"},
                                                {"label": "绿色", "value": "#2ca02c"},
                                                {"label": "橙色", "value": "#ff7f0e"},
                                                {"label": "紫色", "value": "#9467bd"},
                                                {"label": "粉色", "value": "#e377c2"},
                                                {"label": "青色", "value": "#17becf"},
                                                {"label": "黄色", "value": "#bcbd22"},
                                            ],
                                            value="#1f77b4",
                                            clearable=False,
                                            style={"width": "140px"},
                                        ),
                                        dcc.Input(
                                            id="custom-color",
                                            type="text",
                                            value="",
                                            placeholder="#RRGGBB",
                                            style={
                                                "width": "100px",
                                                "marginLeft": "10px",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                            ],
                            style={"padding": "20px"},
                        ),
                    ],
                    id="sidebar",
                    style={
                        "width": "450px",
                        "backgroundColor": "#f8f9fa",
                        "borderRight": "1px solid #ddd",
                        "position": "fixed",
                        "top": "80px",
                        "left": "-450px",  # 初始状态隐藏
                        "bottom": 0,
                        "overflowY": "auto",
                        "transition": "left 0.3s",
                        "zIndex": 900,
                    },
                ),
                # 图形显示区域
                html.Div(
                    [
                        dcc.Graph(
                            id="wave-plot",
                            style={"height": "calc(100vh - 80