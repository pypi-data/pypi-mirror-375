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
                                                    i: str(i) for i in range(3, 24, 3)
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
                                                max=2.0,
                                                step=0.1,
                                                value=1.0,
                                                marks={
                                                    i / 2: str(i / 2)
                                                    for i in range(1, 5)
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
                                            max=2.0,
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
                            style={"height": "calc(100vh - 80px)"},
                            config={"displayModeBar": True, "scrollZoom": True},
                        )
                    ],
                    style={
                        "marginTop": "80px",
                        "padding": "20px",
                        "transition": "margin-left 0.3s",
                    },
                    id="content",
                ),
            ],
            style={"height": "100vh"},
        ),
        # 存储侧边栏状态和参数值
        dcc.Store(id="sidebar-status", data={"is_open": False}),
        dcc.Store(
            id="param-values",
            data={
                "amplitude": 0.5,
                "frequency": 3,
                "period": 11,
                "theta": 0,
                "radius": 1.0,
                "line-width": 2,
                "opacity": 1.0,
            },
        ),
    ]
)


# 侧边栏切换回调
@callback(
    [
        Output("sidebar", "style"),
        Output("content", "style"),
        Output("sidebar-status", "data"),
    ],
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar-status", "data")],
)
def toggle_sidebar(n_clicks, status):
    if n_clicks is None:
        is_open = False
    else:
        is_open = not status.get("is_open", False)

    sidebar_style = {
        "width": "450px",
        "backgroundColor": "#f8f9fa",
        "borderRight": "1px solid #ddd",
        "position": "fixed",
        "top": "80px",
        "left": "0px" if is_open else "-450px",
        "bottom": 0,
        "overflowY": "auto",
        "transition": "left 0.3s",
        "zIndex": 900,
    }

    content_style = {
        "marginTop": "80px",
        "marginLeft": "470px" if is_open else "20px",
        "marginRight": "20px",
        "transition": "margin-left 0.3s",
    }

    return sidebar_style, content_style, {"is_open": is_open}


# 参数同步回调 - 使用单一回调处理所有参数
@callback(
    [
        Output("param-values", "data"),
        Output("amplitude-slider", "value"),
        Output("amplitude-input", "value"),
        Output("frequency-slider", "value"),
        Output("frequency-input", "value"),
        Output("period-slider", "value"),
        Output("period-input", "value"),
        Output("theta-slider", "value"),
        Output("theta-input", "value"),
        Output("radius-slider", "value"),
        Output("radius-input", "value"),
        Output("line-width-slider", "value"),
        Output("line-width-input", "value"),
        Output("opacity-slider", "value"),
        Output("opacity-input", "value"),
    ],
    [
        Input("amplitude-slider", "value"),
        Input("amplitude-input", "value"),
        Input("frequency-slider", "value"),
        Input("frequency-input", "value"),
        Input("period-slider", "value"),
        Input("period-input", "value"),
        Input("theta-slider", "value"),
        Input("theta-input", "value"),
        Input("radius-slider", "value"),
        Input("radius-input", "value"),
        Input("line-width-slider", "value"),
        Input("line-width-input", "value"),
        Input("opacity-slider", "value"),
        Input("opacity-input", "value"),
    ],
    [State("param-values", "data")],
)
def sync_params(
    amplitude_slider,
    amplitude_input,
    frequency_slider,
    frequency_input,
    period_slider,
    period_input,
    theta_slider,
    theta_input,
    radius_slider,
    radius_input,
    line_width_slider,
    line_width_input,
    opacity_slider,
    opacity_input,
    param_values,
):
    # 获取触发回调的组件ID
    triggered_id = ctx.triggered_id if ctx.triggered_id else None

    # 如果没有触发组件，返回当前值
    if triggered_id is None:
        return (
            param_values,
            param_values["amplitude"],
            param_values["amplitude"],
            param_values["frequency"],
            param_values["frequency"],
            param_values["period"],
            param_values["period"],
            param_values["theta"],
            param_values["theta"],
            param_values["radius"],
            param_values["radius"],
            param_values["line-width"],
            param_values["line-width"],
            param_values["opacity"],
            param_values["opacity"],
        )

    # 更新参数值
    new_params = param_values.copy()

    # 根据触发组件更新相应的参数
    if triggered_id == "amplitude-slider" or triggered_id == "amplitude-input":
        value = (
            amplitude_slider if triggered_id == "amplitude-slider" else amplitude_input
        )
        if value is not None:
            new_params["amplitude"] = value
            amplitude_slider = amplitude_input = value

    elif triggered_id == "frequency-slider" or triggered_id == "frequency-input":
        value = (
            frequency_slider if triggered_id == "frequency-slider" else frequency_input
        )
        if value is not None:
            new_params["frequency"] = value
            frequency_slider = frequency_input = value

    elif triggered_id == "period-slider" or triggered_id == "period-input":
        value = period_slider if triggered_id == "period-slider" else period_input
        if value is not None:
            new_params["period"] = value
            period_slider = period_input = value

    elif triggered_id == "theta-slider" or triggered_id == "theta-input":
        value = theta_slider if triggered_id == "theta-slider" else theta_input
        if value is not None:
            new_params["theta"] = value
            theta_slider = theta_input = value

    elif triggered_id == "radius-slider" or triggered_id == "radius-input":
        value = radius_slider if triggered_id == "radius-slider" else radius_input
        if value is not None:
            new_params["radius"] = value
            radius_slider = radius_input = value

    elif triggered_id == "line-width-slider" or triggered_id == "line-width-input":
        value = (
            line_width_slider
            if triggered_id == "line-width-slider"
            else line_width_input
        )
        if value is not None:
            new_params["line-width"] = value
            line_width_slider = line_width_input = value

    elif triggered_id == "opacity-slider" or triggered_id == "opacity-input":
        value = opacity_slider if triggered_id == "opacity-slider" else opacity_input
        if value is not None:
            new_params["opacity"] = value
            opacity_slider = opacity_input = value

    # 返回更新后的所有值
    return (
        new_params,
        new_params["amplitude"],
        new_params["amplitude"],
        new_params["frequency"],
        new_params["frequency"],
        new_params["period"],
        new_params["period"],
        new_params["theta"],
        new_params["theta"],
        new_params["radius"],
        new_params["radius"],
        new_params["line-width"],
        new_params["line-width"],
        new_params["opacity"],
        new_params["opacity"],
    )


# 主回调函数：更新图形
@callback(
    Output("wave-plot", "figure"),
    [
        Input("theme-selector", "value"),
        Input("wave-type", "value"),
        Input("param-values", "data"),
        Input("color", "value"),
        Input("custom-color", "value"),
    ],
)
def update_figure(theme, wave_type, params, color, custom_color):
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
        A=params["amplitude"],
        F=params["frequency"],
        P=params["period"],
        color=selected_color,
        theta=params["theta"],
        R=params["radius"],
        width=params["line-width"],
        opacity=params["opacity"],
    )

    # 应用主题配置
    config.apply_to_figure(fig)

    return fig


# 运行服务器
if __name__ == "__main__":
    app.run(debug=True)
