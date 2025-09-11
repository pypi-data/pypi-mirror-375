"""
波形可视化Dash应用

此模块提供了一个交互式界面来展示和调整cprdspy库中的各种波形。
支持实时参数调整和主题切换。
"""

import dash
from dash import html, dcc, callback, Input, Output, State
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
        # 标题和主题选择
        html.Div(
            [
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
            },
        ),
        # 主要内容区域
        html.Div(
            [
                # 控制面板
                html.Div(
                    [
                        html.H3("参数控制"),
                        # 波形类型选择
                        html.Label("波形类型"),
                        dcc.Dropdown(
                            id="wave-type",
                            options=[
                                {"label": v, "value": k} for k, v in WAVE_TYPES.items()
                            ],
                            value="wave_circle_arithmetic",
                        ),
                        # 振幅控制
                        html.Label("振幅 (A)"),
                        html.Div(
                            [
                                dcc.Slider(
                                    id="amplitude",
                                    min=0.1,
                                    max=2.0,
                                    step=0.01,
                                    value=0.5,
                                    marks={i / 2: str(i / 2) for i in range(1, 5)},
                                ),
                                dcc.Input(
                                    id="amplitude-input",
                                    type="number",
                                    min=0.1,
                                    max=2.0,
                                    step=0.01,
                                    value=0.5,
                                    style={"width": "60px", "marginLeft": "10px"},
                                ),
                            ],
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        # 频率控制
                        html.Label("频率 (F)"),
                        dcc.Slider(
                            id="frequency",
                            min=1,
                            max=10,
                            step=1,
                            value=3,
                            marks={i: str(i) for i in range(1, 11)},
                        ),
                        # 周期控制
                        html.Label("周期 (P)"),
                        dcc.Slider(
                            id="period",
                            min=3,
                            max=20,
                            step=1,
                            value=11,
                            marks={i: str(i) for i in range(3, 21, 2)},
                        ),
                        # 相位控制
                        html.Label("相位 (θ)"),
                        dcc.Slider(
                            id="theta",
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
                        # 基准半径控制
                        html.Label("基准半径 (R)"),
                        dcc.Slider(
                            id="radius",
                            min=0.5,
                            max=2.0,
                            step=0.1,
                            value=1.0,
                            marks={i / 10: str(i / 10) for i in range(5, 21, 2)},
                        ),
                        # 线宽控制
                        html.Label("线宽"),
                        dcc.Slider(
                            id="line-width",
                            min=1,
                            max=5,
                            step=0.5,
                            value=2,
                            marks={i: str(i) for i in range(1, 6)},
                        ),
                        # 透明度控制
                        html.Label("透明度"),
                        dcc.Slider(
                            id="opacity",
                            min=0.1,
                            max=1.0,
                            step=0.1,
                            value=1.0,
                            marks={i / 10: str(i / 10) for i in range(1, 11)},
                        ),
                        # 颜色选择
                        html.Label("颜色"),
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
                        ),
                        # 自定义颜色输入
                        html.Div(
                            [
                                html.Label("自定义颜色 (HEX格式, 例如: #FF5733)"),
                                dcc.Input(
                                    id="custom-color",
                                    type="text",
                                    value="",
                                    placeholder="#RRGGBB",
                                    pattern="^#([A-Fa-f0-9]{6})$",
                                    style={"width": "100%"},
                                ),
                            ],
                            style={"marginTop": "10px"},
                        ),
                    ],
                    style={
                        "width": "300px",
                        "padding": "20px",
                        "backgroundColor": "#f8f9fa",
                        "borderRight": "1px solid #ddd",
                    },
                ),
                # 图形显示区域
                html.Div(
                    [
                        dcc.Graph(
                            id="wave-plot", style={"height": "calc(100vh - 100px)"}
                        )
                    ],
                    style={"flex": "1", "padding": "20px"},
                ),
            ],
            style={"display": "flex", "height": "calc(100vh - 100px)"},
        ),
    ]
)


# 回调函数：更新主题
@callback(
    Output("wave-plot", "figure"),
    [
        Input("theme-selector", "value"),
        Input("wave-type", "value"),
        Input("amplitude", "value"),
        Input("frequency", "value"),
        Input("period", "value"),
        Input("theta", "value"),
        Input("radius", "value"),
        Input("line-width", "value"),
        Input("opacity", "value"),
        Input("color", "value"),
        Input("custom-color", "value"),
    ],
)
def update_figure(
    theme, wave_type, A, F, P, theta, R, width, opacity, color, custom_color
):
    # 设置主题
    set_theme(theme)

    # 获取对应的波形函数
    wave_func = WAVE_FUNCTIONS[wave_type]

    # 确定使用哪个颜色值
    # 如果自定义颜色有效，则使用自定义颜色
    import re

    if custom_color and re.match(r"^#([A-Fa-f0-9]{6})$", custom_color):
        selected_color = custom_color
    else:
        selected_color = color

    # 创建波形图
    fig = wave_func(
        A=A,
        F=F,
        P=P,
        color=selected_color,
        theta=theta,
        R=R,
        width=width,
        opacity=opacity,
    )

    # 应用主题配置
    config.apply_to_figure(fig)

    return fig


# 运行服务器
if __name__ == "__main__":
    app.run(debug=True)
