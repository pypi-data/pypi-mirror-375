from dash import Dash, html, dcc, Input, Output
import app_waves
import app_flowers

# 创建Dash应用
app = Dash(__name__, suppress_callback_exceptions=True)


# 主页布局
def home_layout():
    return html.Div(
        [
            html.H1("CPR可视化工具", style={"textAlign": "center"}),
            html.Div(
                [
                    dcc.Link(
                        html.Button("波形可视化", className="nav-button"),
                        href="/waves",
                        style={"margin": "10px"},
                    ),
                    dcc.Link(
                        html.Button("花朵可视化", className="nav-button"),
                        href="/flowers",
                        style={"margin": "10px"},
                    ),
                ],
                style={"display": "flex", "justifyContent": "center", "margin": "20px"},
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
        return app_waves.layout
    elif pathname == "/flowers":
        return app_flowers.layout
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
            .nav-button {
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                transition: background-color 0.3s;
            }
            .nav-button:hover {
                background-color: #45a049;
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
