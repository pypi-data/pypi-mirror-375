"""
花朵可视化Dash应用

此模块提供了一个交互式界面来展示和调整cprdspy库中的各种花朵图形。
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
    n_flower_petal,
    n_flower_arc,
    n_flowers_flower_arc_with_field,
    flowers_flower_by_petal,
    flowers_flower_by_arc,
    flowers_flower_by_flower_arc_with_field,
    flowers_flower_by_petal_multi,
    flower_by_petal_fill,
)

# 创建Dash应用
app = dash.Dash(__name__)

# 定义花朵类型选项
FLOWER_TYPES = {
    "n_flower_petal": "基本花瓣",
    "n_flower_arc": "基本花弧",
    "n_flowers_flower_arc_with_field": "带场花弧",
    "flowers_flower_by_petal": "花瓣单层花",
    "flowers_flower_by_arc": "花弧单层花",
    "flowers_flower_by_flower_arc_with_field": "带场单层花",
    "flowers_flower_by_petal_multi": "多层花",
    "flower_by_petal_fill": "带填充花朵",
}

# 花朵函数映射
FLOWER_FUNCTIONS = {
    "n_flower_petal": n_flower_petal,
    "n_flower_arc": n_flower_arc,
    "n_flowers_flower_arc_with_field": n_flowers_flower_arc_with_field,
    "flowers_flower_by_petal": flowers_flower_by_petal,
    "flowers_flower_by_arc": flowers_flower_by_arc,
    "flowers_flower_by_flower_arc_with_field": flowers_flower_by_flower_arc_with_field,
    "flowers_flower_by_petal_multi": flowers_flower_by_petal_multi,
    "flower_by_petal_fill": flower_by_petal_fill,
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
                html.H1("花朵可视化", style={"flex": "1", "margin": "0"}),
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
                                # 花朵类型选择
                                html.Label("花朵类型"),
                                dcc.Dropdown(
                                    id="flower-type",
                                    options=[
                                        {"label": v, "value": k}
                                        for k, v in FLOWER_TYPES.items()
                                    ],
                                    value="flowers_flower_by_petal",
                                ),
                                # 基准半径控制 (R)
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
                                                    for i in range(1, 13)
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
                                # 花瓣半径控制 (r)
                                html.Label("花瓣半径 (r)"),
                                html.Div(
                                    [
                                        html.Div(
                                            dcc.Slider(
                                                id="petal-radius-slider",
                                                min=0.5,
                                                max=6.0,
                                                step=0.1,
                                                value=2.0,
                                                marks={
                                                    i / 2: str(i / 2)
                                                    for i in range(1, 13)
                                                },
                                            ),
                                            style={
                                                "width": "300px",
                                                "marginRight": "10px",
                                            },
                                        ),
                                        dcc.Input(
                                            id="petal-radius-input",
                                            type="number",
                                            min=0.5,
                                            max=6.0,
                                            step=0.1,
                                            value=2.0,
                                            style={"width": "80px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                # 花瓣形状控制 (n)
                                html.Label("花瓣形状 (n边形)"),
                                html.Div(
                                    [
                                        html.Div(
                                            dcc.Slider(
                                                id="petal-shape-slider",
                                                min=3,
                                                max=36,
                                                step=1,
                                                value=5,
                                                marks={
                                                    i: str(i) for i in range(3, 37, 3)
                                                },
                                            ),
                                            style={
                                                "width": "300px",
                                                "marginRight": "10px",
                                            },
                                        ),
                                        dcc.Input(
                                            id="petal-shape-input",
                                            type="number",
                                            min=3,
                                            max=36,
                                            step=1,
                                            value=5,
                                            style={"width": "80px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                # 花瓣数量控制 (N)
                                html.Label("花瓣数量 (N)"),
                                html.Div(
                                    [
                                        html.Div(
                                            dcc.Slider(
                                                id="petal-count-slider",
                                                min=1,
                                                max=36,
                                                step=1,
                                                value=8,
                                                marks={
                                                    i: str(i) for i in range(1, 37, 3)
                                                },
                                            ),
                                            style={
                                                "width": "300px",
                                                "marginRight": "10px",
                                            },
                                        ),
                                        dcc.Input(
                                            id="petal-count-input",
                                            type="number",
                                            min=1,
                                            max=36,
                                            step=1,
                                            value=8,
                                            style={"width": "80px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                # 旋转角度控制 (theta)
                                html.Label("旋转角度 (θ)"),
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
                                # 多层花参数
                                html.Div(
                                    id="multi-layer-params",
                                    children=[
                                        # 层数控制 (M)
                                        html.Label("层数 (M)"),
                                        html.Div(
                                            [
                                                html.Div(
                                                    dcc.Slider(
                                                        id="layer-count-slider",
                                                        min=1,
                                                        max=10,
                                                        step=1,
                                                        value=3,
                                                        marks={
                                                            i: str(i)
                                                            for i in range(1, 11)
                                                        },
                                                    ),
                                                    style={
                                                        "width": "300px",
                                                        "marginRight": "10px",
                                                    },
                                                ),
                                                dcc.Input(
                                                    id="layer-count-input",
                                                    type="number",
                                                    min=1,
                                                    max=10,
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
                                        # 缩放比例控制 (ratio)
                                        html.Label("缩放比例 (ratio)"),
                                        html.Div(
                                            [
                                                html.Div(
                                                    dcc.Slider(
                                                        id="ratio-slider",
                                                        min=0.1,
                                                        max=2.0,
                                                        step=0.1,
                                                        value=0.8,
                                                        marks={
                                                            i / 10: str(i / 10)
                                                            for i in range(1, 21, 2)
                                                        },
                                                    ),
                                                    style={
                                                        "width": "300px",
                                                        "marginRight": "10px",
                                                    },
                                                ),
                                                dcc.Input(
                                                    id="ratio-input",
                                                    type="number",
                                                    min=0.1,
                                                    max=2.0,
                                                    step=0.1,
                                                    value=0.8,
                                                    style={"width": "80px"},
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "alignItems": "center",
                                                "marginBottom": "20px",
                                            },
                                        ),
                                    ],
                                ),
                                # 颜色控制
                                html.Label("主要颜色"),
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
                                # 填充颜色控制（用于带场和填充类型）
                                html.Div(
                                    id="fill-color-control",
                                    children=[
                                        html.Label("填充颜色"),
                                        html.Div(
                                            [
                                                dcc.Dropdown(
                                                    id="fill-color",
                                                    options=[
                                                        {
                                                            "label": "黄色",
                                                            "value": "#ffd700",
                                                        },
                                                        {
                                                            "label": "浅蓝",
                                                            "value": "#87ceeb",
                                                        },
                                                        {
                                                            "label": "浅绿",
                                                            "value": "#90ee90",
                                                        },
                                                        {
                                                            "label": "浅粉",
                                                            "value": "#ffb6c1",
                                                        },
                                                        {
                                                            "label": "浅紫",
                                                            "value": "#e6e6fa",
                                                        },
                                                        {
                                                            "label": "浅橙",
                                                            "value": "#ffdab9",
                                                        },
                                                    ],
                                                    value="#ffd700",
                                                    clearable=False,
                                                    style={"width": "140px"},
                                                ),
                                                dcc.Input(
                                                    id="custom-fill-color",
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
                            id="flower-plot",
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
                "radius": 1.0,
                "petal_radius": 2.0,
                "petal_shape": 5,
                "petal_count": 8,
                "theta": 0,
                "layer_count": 3,
                "ratio": 0.8,
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


# 参数同步回调
@callback(
    [
        Output("param-values", "data"),
        Output("radius-slider", "value"),
        Output("radius-input", "value"),
        Output("petal-radius-slider", "value"),
        Output("petal-radius-input", "value"),
        Output("petal-shape-slider", "value"),
        Output("petal-shape-input", "value"),
        Output("petal-count-slider", "value"),
        Output("petal-count-input", "value"),
        Output("theta-slider", "value"),
        Output("theta-input", "value"),
        Output("layer-count-slider", "value"),
        Output("layer-count-input", "value"),
        Output("ratio-slider", "value"),
        Output("ratio-input", "value"),
    ],
    [
        Input("radius-slider", "value"),
        Input("radius-input", "value"),
        Input("petal-radius-slider", "value"),
        Input("petal-radius-input", "value"),
        Input("petal-shape-slider", "value"),
        Input("petal-shape-input", "value"),
        Input("petal-count-slider", "value"),
        Input("petal-count-input", "value"),
        Input("theta-slider", "value"),
        Input("theta-input", "value"),
        Input("layer-count-slider", "value"),
        Input("layer-count-input", "value"),
        Input("ratio-slider", "value"),
        Input("ratio-input", "value"),
    ],
    [State("param-values", "data")],
)
def sync_params(
    radius_slider,
    radius_input,
    petal_radius_slider,
    petal_radius_input,
    petal_count_slider,
    petal_count_input,
    theta_slider,
    theta_input,
    layer_count_slider,
    layer_count_input,
    ratio_slider,
    ratio_input,
    param_values,
):
    # 获取触发回调的组件ID
    triggered_id = ctx.triggered_id if ctx.triggered_id else None

    # 如果没有触发组件，返回当前值
    if triggered_id is None:
        return (
            param_values,
            param_values["radius"],
            param_values["radius"],
            param_values["petal_radius"],
            param_values["petal_radius"],
            param_values["petal_count"],
            param_values["petal_count"],
            param_values["theta"],
            param_values["theta"],
            param_values["layer_count"],
            param_values["layer_count"],
            param_values["ratio"],
            param_values["ratio"],
        )

    # 更新参数值
    new_params = param_values.copy()

    # 根据触发组件更新相应的参数
    if triggered_id in ["radius-slider", "radius-input"]:
        value = radius_slider if triggered_id == "radius-slider" else radius_input
        if value is not None:
            new_params["radius"] = value
            radius_slider = radius_input = value

    elif triggered_id in ["petal-radius-slider", "petal-radius-input"]:
        value = (
            petal_radius_slider
            if triggered_id == "petal-radius-slider"
            else petal_radius_input
        )
        if value is not None:
            new_params["petal_radius"] = value
            petal_radius_slider = petal_radius_input = value

    elif triggered_id in ["petal-count-slider", "petal-count-input"]:
        value = (
            petal_count_slider
            if triggered_id == "petal-count-slider"
            else petal_count_input
        )
        if value is not None:
            new_params["petal_count"] = value
            petal_count_slider = petal_count_input = value

    elif triggered_id in ["theta-slider", "theta-input"]:
        value = theta_slider if triggered_id == "theta-slider" else theta_input
        if value is not None:
            new_params["theta"] = value
            theta_slider = theta_input = value

    elif triggered_id in ["layer-count-slider", "layer-count-input"]:
        value = (
            layer_count_slider
            if triggered_id == "layer-count-slider"
            else layer_count_input
        )
        if value is not None:
            new_params["layer_count"] = value
            layer_count_slider = layer_count_input = value

    elif triggered_id in ["ratio-slider", "ratio-input"]:
        value = ratio_slider if triggered_id == "ratio-slider" else ratio_input
        if value is not None:
            new_params["ratio"] = value
            ratio_slider = ratio_input = value

    # 返回更新后的所有值
    return (
        new_params,
        new_params["radius"],
        new_params["radius"],
        new_params["petal_radius"],
        new_params["petal_radius"],
        new_params["petal_shape"],
        new_params["petal_shape"],
        new_params["petal_count"],
        new_params["petal_count"],
        new_params["theta"],
        new_params["theta"],
        new_params["layer_count"],
        new_params["layer_count"],
        new_params["ratio"],
        new_params["ratio"],
    )


# 控制多层参数显示的回调
@callback(
    [Output("multi-layer-params", "style"), Output("fill-color-control", "style")],
    [Input("flower-type", "value")],
)
def toggle_parameter_visibility(flower_type):
    multi_layer_style = {"display": "none"}
    fill_color_style = {"display": "none"}

    if flower_type == "flowers_flower_by_petal_multi":
        multi_layer_style = {"display": "block"}

    if flower_type in [
        "n_flowers_flower_arc_with_field",
        "flowers_flower_by_flower_arc_with_field",
        "flower_by_petal_fill",
    ]:
        fill_color_style = {"display": "block"}

    return multi_layer_style, fill_color_style


# 主回调函数：更新图形
@callback(
    Output("flower-plot", "figure"),
    [
        Input("theme-selector", "value"),
        Input("flower-type", "value"),
        Input("param-values", "data"),
        Input("color", "value"),
        Input("custom-color", "value"),
        Input("fill-color", "value"),
        Input("custom-fill-color", "value"),
    ],
)
def update_figure(
    theme, flower_type, params, color, custom_color, fill_color, custom_fill_color
):
    # 设置主题
    set_theme(theme)

    # 获取对应的花朵函数
    flower_func = FLOWER_FUNCTIONS[flower_type]

    # 确定使用哪个颜色值
    import re

    if custom_color and re.match(r"^#([A-Fa-f0-9]{6})$", custom_color):
        selected_color = custom_color
    else:
        selected_color = color

    if custom_fill_color and re.match(r"^#([A-Fa-f0-9]{6})$", custom_fill_color):
        selected_fill_color = custom_fill_color
    else:
        selected_fill_color = fill_color

    # 根据花朵类型调用相应的函数
    if flower_type == "n_flowers_flower_arc_with_field":
        fig = flower_func(
            center=(0, 0),
            R=params["radius"],
            r=params["petal_radius"],
            n=params["petal_shape"],
            theta=params["theta"],
            color=selected_color,
            field_color=selected_fill_color,
        )
    elif flower_type == "flowers_flower_by_flower_arc_with_field":
        fig = flower_func(
            center=(0, 0),
            R=params["radius"],
            r=params["petal_radius"],
            N=params["petal_count"],
            n=params["petal_shape"],
            theta=params["theta"],
            color=selected_color,
            field_color=selected_fill_color,
        )
    elif flower_type == "flowers_flower_by_petal_multi":
        fig = flower_func(
            center=(0, 0),
            R=params["radius"],
            r=params["petal_radius"],
            n=params["petal_shape"],
            ratio=params["ratio"],
            M=params["layer_count"],
            N=params["petal_count"],
            theta=params["theta"],
            color=selected_color,
        )
    elif flower_type == "flower_by_petal_fill":
        fig = flower_func(
            center=(0, 0),
            r=params["radius"],
            M=params["layer_count"],
            N=params["petal_count"],
            n=params["petal_shape"],
            theta=params["theta"],
            color=selected_color,
            fill_color=selected_fill_color,
        )
    elif flower_type in ["flowers_flower_by_petal", "flowers_flower_by_arc"]:
        fig = flower_func(
            center=(0, 0),
            R=params["radius"],
            r=params["petal_radius"],
            N=params["petal_count"],
            n=params["petal_shape"],
            theta=params["theta"],
            color=selected_color,
        )
    else:
        # 基本花瓣和花弧
        fig = flower_func(
            center=(0, 0),
            R=params["radius"],
            r=params["petal_radius"],
            n=params["petal_shape"],
            theta=params["theta"],
            color=selected_color,
        )

    # 应用主题配置
    config.apply_to_figure(fig)

    return fig


# 运行服务器
if __name__ == "__main__":
    app.run(debug=True)
