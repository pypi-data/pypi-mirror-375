"""
CPR可视化工具主应用

此模块提供了应用的主要入口点和路由控制。
"""

from dash import Dash, html, dcc, Input, Output
from pages import waves, flowers

# 创建Dash应用
app = Dash(__name__, suppress_callback_exceptions=True)


# 主页布局
def home_layout():
    return html.Div(
        [
            html.H1(
                "CPR可视化工具", style={"textAlign": "center", "marginTop": "50px"}
            ),
            html.Div(
                [
                    dcc.Link(
                        html.Button(
                            "波形可视化",
                            className="nav-button",
                            style={
                                "fontSize": "18px",
                                "padding": "15px 30px",
                                "margin": "10px",
                                "backgroundColor": "#4CAF50",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "5px",
                                "cursor": "pointer",
                                "transition": "background-color 0.3s",
                            },
                        ),
                        href="/waves",
                    ),
                    dcc.Link(
                        html.Button(
                            "花朵可视化",
                            className="nav-button",
                            style={
                                "fontSize": "18px",
                                "padding": "15px 30px",
                                "margin": "10px",
                                "backgroundColor": "#2196F3",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "5px",
                                "cursor": "pointer",
                                "transition": "background-color 0.3s",
                            },
                        ),
                        href="/flowers",
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "marginTop": "50px",
                },
            ),
            html.Div(
                [
                    html.H2(
                        "功能说明", style={"textAlign": "center", "marginTop": "50px"}
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3("波形可视化", style={"color": "#4CAF50"}),
                                    html.P("生成和可视化各种类型的波形，包括："),
                                    html.Ul(
                                        [
                                            html.Li("等差圆形波"),
                                            html.Li("等比圆形波"),
                                            html.Li("可调节振幅、频率、周期等参数"),
                                        ]
                                    ),
                                ],
                                style={
                                    "flex": "1",
                                    "margin": "20px",
                                    "padding": "20px",
                                    "backgroundColor": "#f5f5f5",
                                    "borderRadius": "10px",
                                },
                            ),
                            html.Div(
                                [
                                    html.H3("花朵可视化", style={"color": "#2196F3"}),
                                    html.P("创建和可视化各种类型的花朵图案，包括："),
                                    html.Ul(
                                        [
                                            html.Li("基本花瓣和花弧"),
                                            html.Li("单层和多层花朵"),
                                            html.Li("可调节花瓣形状、数量、大小等参数"),
                                        ]
                                    ),
                                ],
                                style={
                                    "flex": "1",
                                    "margin": "20px",
                                    "padding": "20px",
                                    "backgroundColor": "#f5f5f5",
                                    "borderRadius": "10px",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "justifyContent": "center",
                            "maxWidth": "1200px",
                            "margin": "0 auto",
                        },
                    ),
                ]
            ),
        ]
    )


# 应用布局
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)


# 页面路由回调
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/waves":
        return waves.layout
    elif pathname == "/flowers":
        return flowers.layout
    else:
        return home_layout()


# 添加CSS样式
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>CPR可视化工具</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #ffffff;
            }
            .nav-button:hover {
                opacity: 0.9;
                transform: scale(1.05);
            }
            ul {
                padding-left: 20px;
            }
            li {
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

if __name__ == "__main__":
    app.run_server(debug=True)
